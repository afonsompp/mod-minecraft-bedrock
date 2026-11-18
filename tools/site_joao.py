"""Gera o site de downloads (pasta site/) a partir de dist/*.mcaddon e do CHANGELOG.md.

O site é estático e roda na Vercel: python tools/build.py --publicar
(nome site_joao.py: "site" é um módulo padrão do Python e não pode ser sombreado)
Só entram versões que têm .mcaddon em dist/ E seção no CHANGELOG.md.
"""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITE = RAIZ / "site"
MODELO = Path(__file__).resolve().parent / "site" / "modelo.html"
MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()

# armas mostradas no topo (imagem gerada por gerar.py em previews/lado_t_<id>.png)
ARMAS = [("besta", "Besta"), ("awp", "AWP"), ("m4a4", "M4A4"), ("ak47", "AK-47"),
         ("glock", "Glock")]

VERCEL = {
    "cleanUrls": True,
    "headers": [
        {"source": "/downloads/(.*)", "headers": [
            {"key": "Content-Type", "value": "application/octet-stream"},
            {"key": "Content-Disposition", "value": "attachment"},
            {"key": "Cache-Control", "value": "public, max-age=31536000, immutable"},
        ]},
        {"source": "/", "headers": [{"key": "Cache-Control", "value": "no-cache"}]},
        {"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]},
    ],
}


def comprimentos():
    """Comprimento de cada arma no modelo (extensão em Z dos cubos), para mostrar na escala certa."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from dominios.armas import modelos
    out = {}
    for id_, _ in ARMAS:
        corpo = modelos.ARMAS[id_][0]()[0]
        zs = [c["o"][2] for c in corpo] + [c["o"][2] + c["s"][2] for c in corpo]
        out[id_] = max(zs) - min(zs)
    return out


def ler_changelog():
    """[(versao, data, testado, [itens em markdown])], na ordem do arquivo (mais nova primeiro)."""
    out = []
    for bloco in re.split(r"^## ", (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8"), flags=re.M)[1:]:
        cab, *linhas = bloco.splitlines()
        m = re.match(r"(\d+\.\d+\.\d+)\s+—\s+(\d{4}-\d{2}-\d{2})", cab)
        if not m:
            continue
        itens = [ln[2:].strip() for ln in linhas if ln.startswith("- ")]
        out.append((m.group(1), m.group(2), "testado no celular" in cab, itens))
    return out


def inline(md):
    t = html.escape(md, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return re.sub(r"`(.+?)`", r"\1", t)


def data_br(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {MESES[d.month - 1]} {d.year}"


def tamanho(n):
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.1f} MB".replace(".", ",")


def gerar_site():
    versoes = []
    for v, d, testado, itens in ler_changelog():
        arq = RAIZ / "dist" / f"Armas_do_Joao_v{v}.mcaddon"
        if arq.exists():
            versoes.append(dict(v=v, data=d, testado=testado, itens=itens, arq=arq))
    if not versoes:
        raise SystemExit("nenhuma versão com .mcaddon em dist/ e seção no CHANGELOG.md")

    if SITE.exists():
        for sub in ("downloads", "img"):
            shutil.rmtree(SITE / sub, ignore_errors=True)
    (SITE / "downloads").mkdir(parents=True, exist_ok=True)
    (SITE / "img").mkdir(exist_ok=True)
    for x in versoes:
        shutil.copy2(x["arq"], SITE / "downloads" / x["arq"].name)
    shutil.copy2(RAIZ / "packs" / "RP" / "pack_icon.png", SITE / "img" / "icone.png")

    armeiro = []
    comp = comprimentos()
    maior = max(comp.values())
    for id_, nome in ARMAS:
        img = RAIZ / "previews" / f"lado_t_{id_}.png"
        if not img.exists():
            continue
        from PIL import Image          # recorta a margem transparente da renderização
        im = Image.open(img)
        im = im.crop(im.getbbox())
        im.save(SITE / "img" / img.name, optimize=True)
        largura = 100 * comp[id_] / maior       # escala real entre as armas
        armeiro.append(f'      <li class="{id_}"><img src="img/{img.name}" alt="{nome}" '
                       f'width="{im.width}" height="{im.height}" style="width:{largura:.0f}%">'
                       f"<span>{nome}</span></li>")

    hist = []
    for i, x in enumerate(versoes):
        badge = ' <span class="testado">Testado no celular</span>' if x["testado"] else ""
        itens = "\n".join(f"          <li>{inline(t)}</li>" for t in x["itens"])
        link = f'downloads/{x["arq"].name}'
        hist.append(f'''      <li class="versao{' atual' if i == 0 else ''}">
        <header><h3>Versão {x["v"]}</h3><time datetime="{x["data"]}">{data_br(x["data"])}</time>{badge}</header>
        <ul>
{itens}
        </ul>
        <a href="{link}" download>Baixar a {x["v"]} ({tamanho(x["arq"].stat().st_size)})</a>
      </li>''')

    atual = versoes[0]
    selo = (f"Lançada em {data_br(atual['data'])}. <b>Testada no celular.</b>" if atual["testado"]
            else f"Lançada em {data_br(atual['data'])}. Ainda em teste: se algo estranho acontecer, avise o tio Afonso.")
    hoje = date.today()
    pagina = (MODELO.read_text(encoding="utf-8")
              .replace("{{ARMEIRO}}", "\n".join(armeiro))
              .replace("{{HREF}}", f'downloads/{atual["arq"].name}')
              .replace("{{VERSAO}}", atual["v"])
              .replace("{{TAMANHO}}", tamanho(atual["arq"].stat().st_size))
              .replace("{{SELO}}", selo)
              .replace("{{HISTORICO}}", "\n".join(hist))
              .replace("{{GERADO}}", f"{hoje.day} {MESES[hoje.month - 1]} {hoje.year}"))
    assert "{{" not in pagina, "marcador sem valor no modelo do site"
    (SITE / "index.html").write_text(pagina, encoding="utf-8")
    (SITE / "vercel.json").write_text(json.dumps(VERCEL, indent=2) + "\n", encoding="utf-8")
    print(f"site: {SITE.relative_to(RAIZ)}/ ({len(versoes)} versões, atual {atual['v']})")
    return SITE


if __name__ == "__main__":
    gerar_site()
