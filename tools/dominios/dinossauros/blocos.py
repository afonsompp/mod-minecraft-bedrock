"""Os dois blocos do laboratório: o Extrator de DNA e a Incubadora.

**Primeiros blocos do projeto.** O que isso trouxe de novo, e que não existia em lugar nenhum:

  packs/BP/blocks/            o bloco em si (comportamento é dado, mas aqui é gerado dos dados)
  packs/RP/blocks/            a ligação bloco → geometria e textura
  packs/RP/textures/blocks/   a textura
  packs/RP/textures/terrain_texture.json   o atlas de blocos, o irmão do item_texture

Reaproveitam o `build_geometry` das armas, com duas diferenças:

 1. **unidade 1/16**, não 1/64: um bloco tem 16 unidades, e vai de -8 a 8 em X e Z, de 0 a 16 em Y;
 2. **`material_instances` com uma instância só** (`*`), apontando para a nossa textura. Assim a
    geometria mapeia o atlas por face exatamente como faz numa arma, e o bloco herda a pintura 3D
    (oclusão, quina clara, desgaste) em vez de parecer um cubo chapado.

A lógica — o que entra, quanto demora, o que sai — não está aqui: está em
`packs/BP/scripts/laboratorio/`, ligada pelo componente customizado que cada bloco declara.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

from nucleo.formas import box, sym
from nucleo.geometria import build_geometry, render

FASES = (0, 1, 2)    # 0 parado · 1 trabalhando · 2 pronto para recolher
ESTADO = "joao:fase"


def _pes():
    """Quatro pés recuados: tiram o bloco do chão e matam a silhueta de caixa."""
    return [box(x, x + 1.6, 0, 1.2, z, z + 1.6, "aco_escuro")
            for x in (-7.4, 5.8) for z in (-7.4, 5.8)]


def _painel(y0, y1, z, inclinacao=-12):
    """Painel de comando inclinado na frente. −Z é a frente de qualquer coisa no Bedrock.

    Duas regras que as serrilhas pretas da primeira versão ensinaram: o painel inteiro fica **fora**
    da parede do gabinete (com `rx` negativo o topo vai para dentro, então a inclinação é pequena),
    e cada peça saliente **entra** 0,15 na que está atrás — faces coincidentes brigam pelo mesmo
    plano e o jogo pisca entre as duas."""
    piv = (0, (y0 + y1) / 2, z + 0.4)
    r = (inclinacao, 0, 0)
    return [
        box(-5.6, 5.6, y0, y1, z, z + 0.8, "aco_escuro", r=r, p=piv),
        box(-4.4, 0.6, y0 + 0.9, y1 - 0.7, z - 0.35, z + 0.15, "boca", r=r, p=piv),      # mostrador
        box(1.6, 2.6, y0 + 1.1, y1 - 1.1, z - 0.35, z + 0.15, "fluor", r=r, p=piv),      # luz
        box(3.2, 4.8, y0 + 1.1, y1 - 1.1, z - 0.35, z + 0.15, "aco_claro", r=r, p=piv),  # botão
    ]


def extrator():
    """Centrífuga de bancada: gabinete, tambor com visor e painel de comando.

    **Sem cúpula de vidro.** O "vidro" do projeto é um material opaco quase preto, e numa superfície
    grande ele vira um buraco preto em vez de uma janela — a primeira versão deste bloco provou
    isso. Equipamento de laboratório de verdade é metal com visor pequeno, que é também o que
    funciona aqui."""
    A, E, C, Z, V, L = "aluminio", "aco_escuro", "aco_claro", "aco", "boca", "fluor"
    return [
        box(-8, 8, 1.2, 2.2, -8, 8, E),
        box(-7.4, 7.4, 2.2, 9, -7.4, 7.4, A),              # gabinete
        box(-8, 8, 9, 10.2, -8, 8, C),                     # tampo, com saliência
        # tambor da centrífuga: dois cubos cruzados viram um cilindro de oito lados
        box(-4.6, 4.6, 10.2, 15, -3.1, 3.1, Z),
        box(-3.1, 3.1, 10.2, 15, -4.6, 4.6, Z),
        box(-4.0, 4.0, 10.2, 15, -4.0, 4.0, Z),
        # aros do tambor, que quebram a parede lisa
        box(-4.8, 4.8, 11.4, 12.0, -3.2, 3.2, A),
        box(-3.2, 3.2, 11.4, 12.0, -4.8, 4.8, A),
        box(-5.0, 5.0, 15.0, 16.0, -5.0, 5.0, C),          # tampa do tambor
        box(-1.4, 1.4, 14.6, 15.2, -1.4, 1.4, E),          # manopla da tampa
        box(-2.4, 2.4, 12.4, 14.2, -4.95, -4.45, V),       # visor do tambor (entra no aro)
        *_painel(3.6, 7.2, -8.05),
        # dutos laterais
        *[box(s * 7.4, s * 8.3, 3.2, 6.4, -2.4, 2.4, E) for s in (-1, 1)],
        *[box(s * 7.6, s * 8.1, 6.4, 8.6, -1.2, 1.2, Z) for s in (-1, 1)],
        *_pes(),
    ]


def _incubadora(com_ovo):
    """Chocadeira: ninho aberto no tampo e a lâmpada de aquecimento num arco por cima.

    O ninho é **aberto** de propósito. Fechar com uma cúpula esconderia justamente a coisa pela qual
    o João vai estar esperando; assim o ovo aparece de verdade, trocado por permutação do estado."""
    A, E, C, Z, V, L = "aluminio", "aco_escuro", "aco_claro", "aco", "boca", "fluor"
    c = [
        box(-8, 8, 1.2, 2.2, -8, 8, E),
        box(-7.4, 7.4, 2.2, 5.6, -7.4, 7.4, A),            # gabinete, só até onde o ninho começa
        # O ninho é um FURO, e furo em bloco se faz com moldura: tanto a parte alta do gabinete
        # quanto o tampo são quatro peças em volta do vão. Na primeira versão o gabinete era um cubo
        # inteiro e tapava o ninho por baixo — de cima via-se uma chapa lisa.
        *[box(ax, bx, 5.6, 8, az, bz, A) for ax, bx, az, bz in
          ((-7.4, 7.4, -7.4, -4.8), (-7.4, 7.4, 4.8, 7.4),
           (-7.4, -4.8, -4.8, 4.8), (4.8, 7.4, -4.8, 4.8))],
        *[box(ax, bx, 8, 9.2, az, bz, C) for ax, bx, az, bz in
          ((-8, 8, -8, -4.6), (-8, 8, 4.6, 8), (-8, -4.6, -4.6, 4.6), (4.6, 8, -4.6, 4.6))],
        box(-4.9, 4.9, 4.6, 5.8, -4.9, 4.9, Z),            # fundo do ninho, 3 un. abaixo do tampo
        box(-3.8, 3.8, 5.4, 6.0, -3.8, 3.8, E),            # forro escuro onde o ovo se apoia
        # porta frontal com janela, como uma chocadeira de verdade
        box(-5.4, 5.4, 3.0, 7.4, -7.9, -7.3, Z),
        box(-3.4, 3.4, 4.0, 6.6, -8.15, -7.75, V),
        box(4.0, 5.0, 4.8, 5.8, -8.25, -7.8, C),           # puxador
        box(-5.0, -3.8, 5.0, 5.6, -8.25, -7.8, L),         # luz de aquecimento ligada
        # arco que segura a lâmpada, logo acima do ninho
        *[box(x, x + 1.2, 9.0, 12.4, -0.9, 0.9, A) for x in (-5.8, 4.6)],
        box(-5.8, 5.8, 12.4, 13.4, -1.5, 1.5, C),
        box(-2.4, 2.4, 11.3, 12.5, -2.4, 2.4, A),          # refletor cônico (aproximado)
        box(-1.7, 1.7, 10.5, 11.5, -1.7, 1.7, L),          # lâmpada
        *_pes(),
    ]
    if com_ovo:
        # ovo no ninho: cubos cruzados afinando no topo, do mesmo jeito que o tambor vira cilindro
        c += [
            # ovo: mais alto que largo, e com o bojo abaixo do meio — senão lê como pedra
            box(-1.5, 1.5, 5.9, 6.6, -1.1, 1.1, "cabo"),
            box(-1.9, 1.9, 6.6, 8.2, -1.4, 1.4, "cabo"),
            box(-1.4, 1.4, 6.6, 8.2, -1.9, 1.9, "cabo"),
            box(-1.5, 1.5, 8.2, 9.2, -1.1, 1.1, "cabo"),
            box(-1.1, 1.1, 8.2, 9.2, -1.5, 1.5, "cabo"),
            box(-0.9, 0.9, 9.2, 9.8, -0.7, 0.7, "cabo"),
        ]
    return c


def incubadora():
    return _incubadora(False)


def incubadora_cheia():
    return _incubadora(True)


BLOCOS = {
    "extrator_dna": dict(nome="Extrator de DNA", modelo=extrator, luz=(0, 9, 5),
                         receita=[["III", "IVI", "IRI"],
                                  {"I": "minecraft:iron_ingot", "V": "minecraft:glass",
                                   "R": "minecraft:redstone_block"}]),
    "incubadora": dict(nome="Incubadora", modelo=incubadora, luz=(0, 7, 12),
                       cheia=incubadora_cheia,
                       receita=[["IVI", "VLV", "III"],
                                {"I": "minecraft:iron_ingot", "V": "minecraft:glass",
                                 "L": "minecraft:lantern"}]),
}


def _bloco_json(id_, cfg):
    """O JSON do bloco. A lógica entra pelo componente customizado `joao:maquina`, registrado no
    script — o mesmo mecanismo das armas, do outro lado da API."""
    return {
        "format_version": "1.21.90",
        "minecraft:block": {
            "description": {
                "identifier": f"joao:{id_}",
                "menu_category": {"category": "items"},
                # a fase é só visual aqui (a luz); quem guarda o que está dentro é o script
                "states": {ESTADO: list(FASES)},
            },
            "components": {
                "minecraft:display_name": cfg["nome"],
                "minecraft:geometry": f"geometry.joao.{id_}",
                "minecraft:material_instances": {
                    "*": {"texture": f"joao_{id_}", "render_method": "opaque"},
                },
                "minecraft:destructible_by_mining": {"seconds_to_destroy": 3.5},
                "minecraft:destructible_by_explosion": {"explosion_resistance": 15},
                "minecraft:map_color": "#7e838a",
                # cheio, mas não sólido: a torre e a cúpula deixariam buracos num collision box cheio
                "minecraft:collision_box": {"origin": [-8, 0, -8], "size": [16, 16, 16]},
                "minecraft:selection_box": {"origin": [-8, 0, -8], "size": [16, 16, 16]},
                "joao:maquina": {"tipo": id_},
            },
            "permutations": [
                {"condition": f"q.block_state('{ESTADO}') == {f}",
                 "components": _fase(id_, cfg, f, luz)}
                for f, luz in zip(FASES, cfg["luz"])
            ],
        },
    }


def _fase(id_, cfg, fase, luz):
    """O que muda em cada fase: a luz sempre, e na incubadora também a geometria — é assim que o ovo
    aparece no ninho quando ele fica pronto, sem precisar de entidade nenhuma."""
    comp = {"minecraft:light_emission": luz}
    if cfg.get("cheia") and fase == 2:
        # a geometria cheia tem atlas próprio, então a textura TEM de trocar junto: cada modelo
        # mapeia as UVs da sua, e trocar só a geometria embaralharia as faces
        comp["minecraft:geometry"] = f"geometry.joao.{id_}_cheia"
        comp["minecraft:material_instances"] = {
            "*": {"texture": f"joao_{id_}_cheia", "render_method": "opaque"}}
    return comp


def _receita_json(id_, cfg):
    padrao, chaves = cfg["receita"]
    return {
        "format_version": "1.20.10",
        "minecraft:recipe_shaped": {
            "description": {"identifier": f"joao:{id_}"},
            "tags": ["crafting_table"],
            "pattern": padrao,
            "key": {k: {"item": v} for k, v in chaves.items()},
            "unlock": [{"item": "joao:fossil"}],
            "result": {"item": f"joao:{id_}", "count": 1},
        },
    }


def _previa(faces, destino, osso):
    """Vista 3/4 de cima, como se olha um bloco no mundo. Sem isto, a única forma de julgar a
    silhueta é pôr o bloco no jogo — e o `CLAUDE.md` cobra a prévia antes disso.

    Câmera orbital: gira `giro` em torno de Y e sobe `incl`. Com a elevação, o topo do bloco fica
    **mais perto** da câmera — que é o que distingue olhar de cima de olhar de baixo, e o erro que
    a primeira versão desta função cometeu."""
    W, H = 760, 760
    giro, incl = np.radians(34.0), np.radians(24.0)
    cg, sg, ci, si = np.cos(giro), np.sin(giro), np.cos(incl), np.sin(incl)

    def vista(q_bb):
        q = np.asarray(q_bb, float) - np.array([0.0, 8.0, 0.0])
        # a direita da tela é -X do espaço bb: o referencial de câmera do renderizador é espelhado.
        # Com o sinal trocado, o teste de visibilidade inverte e aparecem as faces de dentro.
        direita = -(q[:, 0] * cg - q[:, 2] * sg)
        fundo = q[:, 0] * sg + q[:, 2] * cg
        cima = q[:, 1] * ci + fundo * si
        prof = fundo * ci - q[:, 1] * si
        return np.stack([direita, cima, prof + 52.0], axis=1)

    f = W / 2 / np.tan(np.radians(13))
    im = render(faces, {osso: vista},
                lambda p: (W / 2 + p[0] / p[2] * f, H / 2 - p[1] / p[2] * f), (W, H),
                bg=Image.new("RGBA", (W, H), (152, 156, 160, 255)))
    im.save(destino)
    return im


def gerar(rp, bp, previews):
    """Escreve os dois blocos (BP e RP) e devolve as entradas do atlas de blocos."""
    for sub in ("models/blocks", "textures/blocks", "blocks"):
        (rp / sub).mkdir(parents=True, exist_ok=True)
    pasta_bp = bp / "blocks" / "dinossauros"
    pasta_rc = bp / "recipes" / "dinossauros"
    pasta_bp.mkdir(parents=True, exist_ok=True)
    pasta_rc.mkdir(parents=True, exist_ok=True)

    terreno, ligacao = {}, {}
    for id_, cfg in BLOCOS.items():
        cubos = cfg["modelo"]()
        geo, atlas, _faces = build_geometry(f"geometry.joao.{id_}", [(id_, None, (0, 0, 0), cubos)],
                                       atlas_width=512, binding=False)
        # um bloco não flutua nem se move: a caixa visível é a dele mesmo
        g = geo["minecraft:geometry"][0]["description"]
        g["visible_bounds_width"] = 2
        g["visible_bounds_height"] = 2
        g["visible_bounds_offset"] = [0, 0.5, 0]
        (rp / f"models/blocks/{id_}.geo.json").write_text(json.dumps(geo, indent=1))
        atlas.save(rp / f"textures/blocks/{id_}.png")

        (pasta_bp / f"{id_}.json").write_text(
            json.dumps(_bloco_json(id_, cfg), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (pasta_rc / f"{id_}.json").write_text(
            json.dumps(_receita_json(id_, cfg), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        if previews:
            _previa(_faces, Path(previews) / f"dino_bloco_{id_}.png", id_)
        if cfg.get("cheia"):
            nome2 = f"{id_}_cheia"
            geo2, atlas2, faces2 = build_geometry(f"geometry.joao.{nome2}",
                                                  [(nome2, None, (0, 0, 0), cfg["cheia"]())],
                                                  atlas_width=512, binding=False)
            d2 = geo2["minecraft:geometry"][0]["description"]
            d2["visible_bounds_width"] = 2
            d2["visible_bounds_height"] = 2
            d2["visible_bounds_offset"] = [0, 0.5, 0]
            (rp / f"models/blocks/{nome2}.geo.json").write_text(json.dumps(geo2, indent=1))
            atlas2.save(rp / f"textures/blocks/{nome2}.png")
            terreno[f"joao_{nome2}"] = {"textures": f"textures/blocks/{nome2}"}
            if previews:
                _previa(faces2, Path(previews) / f"dino_bloco_{nome2}.png", nome2)
        terreno[f"joao_{id_}"] = {"textures": f"textures/blocks/{id_}"}
        ligacao[f"joao:{id_}"] = {"sound": "metal"}
        print(f"  bloco {id_}: {len(cubos)} cubos")

    (rp / "textures/terrain_texture.json").write_text(json.dumps({
        "resource_pack_name": "armas_do_joao",
        "texture_name": "atlas.terrain",
        "padding": 8,
        "num_mip_levels": 4,
        "texture_data": terreno,
    }, indent=1) + "\n", encoding="utf-8")
    # blocks.json só liga o som de passo/quebra: a aparência vem do minecraft:geometry do bloco
    (rp / "blocks.json").write_text(json.dumps({"format_version": [1, 1, 0], **ligacao}, indent=1) + "\n",
                                    encoding="utf-8")
    return list(BLOCOS)
