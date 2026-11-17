"""Gera o dardo tranquilizante em voo: geometria, textura, client entity e render controller.

Primeira ENTIDADE do modpack (as armas são attachables). A diferença prática é o osso raiz: um
attachable se prende à mão do jogador (`binding`), e uma entidade solta não tem a que se prender.

Unidades aqui são pixels de modelo (1/16 de bloco), não os 1/64 das armas: a entidade não leva o
`scale 0.25` do osso da arma. O dardo é desenhado com ~10 px (0,6 bloco) — bem maior que os 13 cm
reais, pelo mesmo motivo que a flecha do Minecraft tem um bloco de comprimento: menor que isso, não
se enxerga nada em voo.

A ponta fica em +Z: é a direção em que o jogo orienta um projétil (o mesmo do arrow vanilla, de quem
a entidade herda a física por `runtime_identifier`).
"""
import json
import sys
from pathlib import Path

from PIL import Image
import numpy as np

from geometria import build_geometry, render
from modelos import box


def modelo():
    AL, D, S, L = "aluminio", "aco_escuro", "aco", "fluor"
    c = [
        # penacho (estabilizador), atrás: duas abas cruzadas, como o pompom de um dardo de verdade
        box(-1.7, 1.7, -0.45, 0.45, -4.2, -1.4, L),
        box(-0.45, 0.45, -1.7, 1.7, -4.2, -1.4, L),
        box(-0.9, 0.9, -0.9, 0.9, -4.4, -1.4, L),
        # corpo de alumínio (o tubo do sedativo), seção cruzada para ficar redondo
        box(-1.15, 1.15, -0.8, 0.8, -1.4, 3.0, AL),
        box(-0.8, 0.8, -1.15, 1.15, -1.4, 3.0, AL),
        # colar de gelatina e agulha
        box(-0.9, 0.9, -0.9, 0.9, 3.0, 3.6, D),
        box(-0.3, 0.3, -0.3, 0.3, 3.6, 5.8, S),
    ]
    return c


def textura_sono(rp):
    """O "z" da partícula de sono. Mob do jogo não tem pose de dormir: sem este sinal em cima da
    cabeça, um bicho sedado parece só um bicho travado."""
    from PIL import ImageDraw
    S, E = 32, 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cor = (226, 238, 255, 255)
    d.line([(8, 8), (24, 8)], fill=cor, width=E)         # traço de cima
    d.line([(23, 9), (9, 23)], fill=cor, width=E)        # diagonal
    d.line([(8, 24), (24, 24)], fill=cor, width=E)       # traço de baixo
    (rp / "textures/particle").mkdir(parents=True, exist_ok=True)
    im.save(rp / "textures/particle/joao_sono.png")


def main(rp, previews):
    rp, previews = Path(rp), Path(previews)
    for sub in ("models/entity/joao", "textures/entity/joao", "entity", "render_controllers"):
        (rp / sub).mkdir(parents=True, exist_ok=True)
    cubos = modelo()
    geo, atlas, faces = build_geometry("geometry.joao.dardo", [("dardo", None, (0, 0, 0), cubos)],
                                       atlas_width=256, binding=False)
    (rp / "models/entity/joao/dardo.geo.json").write_text(json.dumps(geo, indent=1))
    atlas.save(rp / "textures/entity/joao/dardo.png")

    (rp / "entity/dardo.entity.json").write_text(json.dumps({
        "format_version": "1.10.0",
        "minecraft:client_entity": {"description": {
            "identifier": "joao:dardo_voo",
            "materials": {"default": "entity_alphatest"},
            "textures": {"default": "textures/entity/joao/dardo"},
            "geometry": {"default": "geometry.joao.dardo"},
            "render_controllers": ["controller.render.joao_dardo"]}}}, indent=1))

    (rp / "render_controllers/joao_dardo.render_controllers.json").write_text(json.dumps({
        "format_version": "1.10.0",
        "render_controllers": {"controller.render.joao_dardo": {
            "geometry": "Geometry.default",
            "materials": [{"*": "Material.default"}],
            "textures": ["Texture.default"]}}}, indent=1))

    textura_sono(rp)

    # prévia: o dardo de 3/4, grande, para conferir as peças e a cor do penacho
    pts = np.array([c["o"] for c in cubos] + [np.add(c["o"], c["s"]) for c in cubos])
    centro = (pts.min(0) + pts.max(0)) / 2
    W, H = 900, 420
    giro, incl = np.radians(32.0), np.radians(18.0)
    cg, sg, ci, si = np.cos(giro), np.sin(giro), np.cos(incl), np.sin(incl)

    def vista(q_bb):
        q = np.asarray(q_bb, float) - np.array([-centro[0], centro[1], centro[2]])
        x = q[:, 0] * cg + q[:, 2] * sg
        z = q[:, 2] * cg - q[:, 0] * sg
        y = q[:, 1] * ci - z * si
        return np.stack([z * ci + q[:, 1] * si, y, x + 26.0], axis=1)

    f = W / 2 / np.tan(np.radians(16))
    im = render(faces, {"dardo": vista}, lambda p: (W / 2 + p[0] / p[2] * f, H / 2 - p[1] / p[2] * f),
                (W, H), bg=Image.new("RGBA", (W, H), (200, 203, 207, 255)))
    im.save(previews / "dardo.png")
    print("dardo ok")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
