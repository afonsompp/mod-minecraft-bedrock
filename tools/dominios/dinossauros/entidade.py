"""A criatura: geometria, textura, client entity, animações, controller e o behavior do BP.

Primeira entidade com **comportamento** do projeto (o dardo é um projétil). Duas coisas que o resto
do add-on já esperava e que estreiam aqui:

 - a família `joao:sedavel` e os eventos `joao:dormir` / `joao:acordar`. O módulo do dardo
   tranquilizante dispara esses eventos desde a v1.7.0 e, até agora, ninguém os atendia;
 - `minecraft:is_sleeping` no grupo do sono. Não é enfeite: o script marca o bicho com uma **tag de
   runtime**, e Molang não lê tag de runtime — o cliente precisa de `q.is_sleeping` para escolher o
   clipe de dormir.
"""
import json

import numpy as np
from PIL import Image

from nucleo.camera import orbital
from nucleo.esqueleto import achatar, vistas
from nucleo.geometria import build_geometry, render
from dominios.dinossauros import animacoes


def _caixa(ossos):
    pts = np.array([list(c["o"]) for o in ossos for c in o.cubos]
                   + [[c["o"][i] + c["s"][i] for i in range(3)] for o in ossos for c in o.cubos])
    return pts.min(0), pts.max(0)


def _previas(faces, ossos, especie, previews, clipes):
    """Pose parada, 3/4, cabeça e uma faixa de quadros-chave por clipe.

    A faixa é o que o `CLAUDE.md` cobra para entidade: pose estática não diz se a animação funciona,
    e a prévia não interpreta Molang — mas interpreta as **poses**, que são a mesma fonte do JSON."""
    mn, mx = _caixa(ossos)
    alvo = (-(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, (mn[2] + mx[2]) / 2)
    fundo = (150, 154, 158, 255)

    def desenhar(pose, giro, incl, dist, tela, al=None, fov=26):
        vista, proj, size = orbital(giro, incl, dist, alvo=al or alvo, fov=fov, tela=tela)
        return render(faces, vistas(ossos, pose, vista), proj, size,
                      bg=Image.new("RGBA", size, fundo))

    desenhar({}, 90, 4, 210, (1200, 620)).save(f"{previews}/dino_{especie}_lado.png")
    desenhar({}, 34, 17, 200, (1060, 760)).save(f"{previews}/dino_{especie}_tres.png")
    desenhar({}, 58, 8, 78, (900, 680), al=(0, 26.5, -24)).save(f"{previews}/dino_{especie}_cabeca.png")

    for clipe in clipes:
        larg = 380
        faixa = Image.new("RGBA", (larg * 5, 300), fundo)
        for i in range(5):
            t = i / 4
            im = desenhar(animacoes.amostra(clipe, t), 90, 6, 230, (larg * 2, 600))
            faixa.alpha_composite(im.resize((larg, 300), Image.LANCZOS), (i * larg, 0))
        faixa.save(f"{previews}/dino_{especie}_{clipe.nome}.png")


def gerar(rp, bp, previews, especie, modelo):
    """Escreve tudo do bicho. `modelo` é a lista de `Osso` da pose parada."""
    ident = especie.id
    ossos = achatar(modelo)
    mn, mx = _caixa(ossos)
    largura = max(mx[0] - mn[0], mx[2] - mn[2]) / 16.0
    altura = (mx[1] - mn[1]) / 16.0

    geo, atlas, faces = build_geometry(
        f"geometry.joao.{ident}", [(o.nome, o.pai, o.pivo, o.cubos) for o in ossos],
        atlas_width=512, binding=False, oclusao="vizinhos",
        # a caixa visível TEM de sair do modelo: o padrão 4x4 corta um bicho grande do campo de
        # visão quando ele sai parcialmente da tela, e a prévia nunca mostra isso (não tem frustum)
        limites=(round(largura + 1.5, 2), round(altura + 1.0, 2), [0, round(altura / 2, 2), 0]))

    for sub in ("models/entity/joao", "textures/entity/joao", "entity", "animations",
                "animation_controllers", "render_controllers"):
        (rp / sub).mkdir(parents=True, exist_ok=True)
    (rp / f"models/entity/joao/{ident}.geo.json").write_text(json.dumps(geo, indent=1))
    atlas.save(rp / f"textures/entity/joao/{ident}.png")

    clipes = animacoes.clipes()
    anims = dict(animacoes.bedrock(c, ident) for c in clipes)
    (rp / f"animations/joao_{ident}.animation.json").write_text(
        json.dumps({"format_version": "1.8.0", "animations": anims}, indent=1))

    # Controller: quem decide o clipe. Dormir ganha de tudo; depois correr, andar e parado.
    ctrl = f"controller.animation.joao_{ident}"
    (rp / f"animation_controllers/joao_{ident}.animation_controllers.json").write_text(json.dumps({
        "format_version": "1.10.0",
        "animation_controllers": {ctrl: {
            "initial_state": "parado",
            "states": {
                "parado": {"animations": ["parado"], "transitions": [
                    {"dormindo": "q.mark_variant == 1"},
                    {"correndo": "q.modified_move_speed > 0.62"},
                    {"andando": "q.modified_move_speed > 0.04"}]},
                "andando": {"animations": ["andar"], "blend_transition": 0.2, "transitions": [
                    {"dormindo": "q.mark_variant == 1"},
                    {"correndo": "q.modified_move_speed > 0.62"},
                    {"parado": "q.modified_move_speed <= 0.04"}]},
                "correndo": {"animations": ["correr"], "blend_transition": 0.2, "transitions": [
                    {"dormindo": "q.mark_variant == 1"},
                    {"andando": "q.modified_move_speed <= 0.62"}]},
                "dormindo": {"animations": ["dormir"], "blend_transition": 0.6, "transitions": [
                    {"parado": "q.mark_variant != 1"}]},
            }}}}, indent=1))

    (rp / f"render_controllers/joao_{ident}.render_controllers.json").write_text(json.dumps({
        "format_version": "1.10.0",
        "render_controllers": {f"controller.render.joao_{ident}": {
            "geometry": "Geometry.default",
            "materials": [{"*": "Material.default"}],
            "textures": ["Texture.default"]}}}, indent=1))

    (rp / f"entity/{ident}.entity.json").write_text(json.dumps({
        "format_version": "1.10.0",
        "minecraft:client_entity": {"description": {
            "identifier": f"joao:{ident}",
            "materials": {"default": "entity_alphatest"},
            "textures": {"default": f"textures/entity/joao/{ident}"},
            "geometry": {"default": f"geometry.joao.{ident}"},
            "animations": {**{c.nome: f"animation.joao.{ident}.{c.nome}" for c in clipes},
                           "controlador": ctrl},
            "scripts": {"animate": ["controlador"]},
            "spawn_egg": {"base_color": "#6f7a4a", "overlay_color": "#b9b489"},
            "render_controllers": [f"controller.render.joao_{ident}"]}}}, indent=1))

    # A entidade vai na RAIZ de `entities/`, não numa subpasta: a documentação oficial diz que é
    # onde o jogo procura, e o dardo — a única entidade nossa que comprovadamente carrega — está lá.
    # Subpasta é confirmada em `items/`; aqui não há garantia, e um bicho que não carrega não dá erro.
    (bp / "entities").mkdir(parents=True, exist_ok=True)
    (bp / f"entities/{ident}.json").write_text(
        json.dumps(_behavior(especie, largura, altura), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")

    if previews:
        _previas(faces, ossos, ident, previews, clipes)
    print(f"  {ident}: {len(ossos)} ossos, {sum(len(o.cubos) for o in ossos)} cubos, "
          f"{altura:.2f} x {largura:.2f} blocos, atlas {atlas.size[0]}x{atlas.size[1]}")
    return {f"joao:{ident}"}


def _behavior(e, largura, altura):
    """O comportamento, em componentes nativos. Script só no que o JSON não resolve — e aqui o JSON
    resolve tudo: andar, caçar, entrar em pânico, crescer e dormir."""
    carnivoro = e.dieta == "carnivoro"
    return {
        "format_version": "1.21.90",
        "minecraft:entity": {
            "description": {
                "identifier": f"joao:{e.id}",
                "is_spawnable": True,      # dá o ovo de spawn no criativo, útil para testar
                "is_summonable": True,
            },
            "component_groups": {
                "joao:bebe": {
                    "minecraft:is_baby": {},
                    "minecraft:scale": {"value": 0.45},
                    "minecraft:health": {"value": max(4, e.vida // 3), "max": max(4, e.vida // 3)},
                    "minecraft:ageable": {
                        "duration": 1200,
                        "grow_up": {"event": "joao:crescer"},
                        "feed_items": ["beef", "porkchop", "mutton", "chicken"] if carnivoro
                        else ["wheat", "hay_block"],
                    },
                    "minecraft:behavior.follow_parent": {"priority": 4, "speed_multiplier": 1.1},
                },
                "joao:adulto": {
                    "minecraft:scale": {"value": 1.0},
                    "minecraft:health": {"value": e.vida, "max": e.vida},
                    "minecraft:attack": {"damage": e.dano},
                    **({"minecraft:behavior.melee_attack": {"priority": 3, "speed_multiplier": 1.4,
                                                            "track_target": True},
                        "minecraft:behavior.nearest_attackable_target": {
                            "priority": 2, "must_see": True, "reselect_targets": True,
                            "within_radius": 24,
                            "entity_types": [{"filters": {"any_of": [
                                {"test": "is_family", "subject": "other", "value": "player"},
                                {"test": "is_family", "subject": "other", "value": "mob"}]},
                                "max_dist": 24}]}} if carnivoro else {}),
                },
                # O sono do dardo tranquilizante. O `mark_variant` existe para o CLIENTE: o script
                # marca uma tag de runtime, e Molang não lê tag — sem isto o bicho não deitaria na
                # tela. **Tem de ser `mark_variant`**: até a v1.9.3 isto era um `minecraft:is_sleeping`
                # que eu supus existir e não existe. Componente desconhecido não é ignorado — ele
                # derruba a entidade inteira na carga, sem erro visível, e o bicho simplesmente não
                # pode ser colocado no mundo por nada (nem ovo, nem /summon).
                "joao:dormindo": {
                    "minecraft:mark_variant": {"value": 1},
                    "minecraft:movement": {"value": 0.0},
                    "minecraft:knockback_resistance": {"value": 1.0},
                },
            },
            "components": {
                "minecraft:type_family": {"family": ["joao", "joao:dino",
                                                     f"joao:dino_{e.dieta}", "joao:sedavel", "mob"]},
                "minecraft:collision_box": {"width": round(min(largura, 1.6), 2),
                                            "height": round(altura, 2)},
                "minecraft:health": {"value": e.vida, "max": e.vida},
                "minecraft:movement": {"value": e.velocidade},
                "minecraft:navigation.walk": {"can_path_over_water": True, "avoid_water": True},
                "minecraft:movement.basic": {},
                "minecraft:jump.static": {},
                "minecraft:can_climb": {},
                "minecraft:physics": {},
                "minecraft:breathable": {"total_supply": 15, "suffocate_time": 0},
                "minecraft:nameable": {},
                "minecraft:pushable": {"is_pushable": True, "is_pushable_by_piston": True},
                "minecraft:behavior.float": {"priority": 0},
                "minecraft:behavior.panic": {"priority": 1, "speed_multiplier": 1.5},
                "minecraft:behavior.random_stroll": {"priority": 6, "speed_multiplier": 0.9},
                "minecraft:behavior.look_at_player": {"priority": 7, "look_distance": 10},
                "minecraft:behavior.random_look_around": {"priority": 8},
                "minecraft:hurt_on_condition": {"damage_conditions": [
                    {"filters": {"test": "in_lava", "subject": "self"},
                     "cause": "lava", "damage_per_tick": 4}]},
            },
            "events": {
                "minecraft:entity_spawned": {"add": {"component_groups": ["joao:adulto"]}},
                "joao:nascer": {"add": {"component_groups": ["joao:bebe"]}},
                "joao:crescer": {"remove": {"component_groups": ["joao:bebe"]},
                                 "add": {"component_groups": ["joao:adulto"]}},
                "joao:dormir": {"add": {"component_groups": ["joao:dormindo"]}},
                "joao:acordar": {"remove": {"component_groups": ["joao:dormindo"]}},
            },
        },
    }
