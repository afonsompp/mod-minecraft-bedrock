"""Build do add-on Armas do João.

Exemplos (rodar na raiz do repositório):
  python tools/build.py                    # valida e gera dist/Armas_do_Joao_vX.Y.Z.mcaddon
  python tools/build.py --gerar            # regenera modelos, texturas, ícones e sons antes
  python tools/build.py --versao 1.2.0     # sobe a versão em todos os manifests
  python tools/build.py --deploy           # copia os packs para as pastas de desenvolvimento do Minecraft (PC)
  python tools/build.py --deploy "C:/caminho/para/com.mojang"
  python tools/build.py --site             # gera o site de downloads em site/ (dist/ + CHANGELOG.md)
  python tools/build.py --publicar         # gera o site e publica na Vercel (1ª vez: npx vercel login)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TOOLS = RAIZ / "tools"
PACKS = RAIZ / "packs"
DIST = RAIZ / "dist"
PREVIEWS = RAIZ / "previews"

# pasta no repositório -> nome da pasta dentro do .mcaddon / pasta de desenvolvimento
PASTAS = {
    "BP": ("Armas_do_Joao_BP", "development_behavior_packs"),
    "RP": ("Armas_do_Joao_RP", "development_resource_packs"),
}

# domínios do modpack, na ordem em que geram (ver gerar())
DOMINIOS = ("armas", "dinossauros")

sys.path.insert(0, str(TOOLS))


def ler_json(p):
    sys.path.insert(0, str(TOOLS))
    from nucleo.jsonc import load
    return load(p)


def versao_atual():
    return ler_json(PACKS / "BP" / "manifest.json")["header"]["version"]


def subir_versao(nova):
    v = [int(x) for x in nova.split(".")]
    assert len(v) == 3, "use o formato X.Y.Z"
    uuids = {}
    for pasta in PASTAS:
        m = json.loads((PACKS / pasta / "manifest.json").read_text(encoding="utf-8"))
        uuids[m["header"]["uuid"]] = True
    for pasta in PASTAS:
        p = PACKS / pasta / "manifest.json"
        m = json.loads(p.read_text(encoding="utf-8"))
        m["header"]["version"] = v
        # versão no NOME do pack (logo depois de "Armas do João", para não ser cortada em tela pequena):
        # ao importar uma nova, o Minecraft mantém a antiga também, e assim dá para ver qual apagar em
        # Configurações > Armazenamento. Só o nome exibido muda; UUID nunca.
        h = m["header"]
        nome = re.sub(r" v\d+\.\d+\.\d+", "", h["name"])
        h["name"] = nome.replace("Armas do João", f"Armas do João v{nova}", 1)
        h["description"] = re.sub(r"^v\d+\.\d+\.\d+ — ", "", h.get("description", ""))
        for mod in m.get("modules", []):
            mod["version"] = v
        for dep in m.get("dependencies", []):
            if dep.get("uuid") in uuids:      # dependências entre os nossos packs
                dep["version"] = v
        p.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # A versão também vai para o script: ao entrar no mundo o add-on a anuncia no chat. É o único
    # jeito de saber, de dentro do jogo, QUAL versão o aparelho carregou — o Minecraft guarda as
    # antigas, e um pack velho rodando é indistinguível de um recurso quebrado.
    (PACKS / "BP" / "scripts" / "comum" / "versao.js").write_text(
        "// GERADO por tools/build.py --versao — não edite à mão.\n"
        f'export const VERSAO = "{nova}";\n', encoding="utf-8")
    print(f"versão -> {nova}")


def gerar():
    """Roda cada domínio registrado, na ordem, e depois o que depende das prévias deles.

    Domínio novo (dinossauros, veículos, armaduras) = uma linha em DOMINIOS e um `gerar(rp, bp,
    previews)` no `__init__.py` dele. Cada um escreve só nas suas pastas."""
    import importlib
    texturas = {}
    for nome in DOMINIOS:
        d = importlib.import_module(f"dominios.{nome}").gerar(PACKS / "RP", PACKS / "BP", PREVIEWS)
        texturas.update(d or {})
    atlas_itens(texturas)
    # o ícone do pack monta as prévias laterais das armas, então vem depois dos domínios
    subprocess.run([sys.executable, "-m", "icone", str(PREVIEWS)], check=True, cwd=TOOLS)
    print(f"gerado — confira as prévias em {PREVIEWS}")


def atlas_itens(texturas):
    """Monta o packs/RP/textures/item_texture.json com o que cada domínio declarou.

    Era escrito à mão até a v1.7.1, o que já dava trabalho com nove itens; com dois por espécie de
    dinossauro, esquecer uma linha aqui (e ver o item virar o quadriculado roxo) seria rotina."""
    alvo = PACKS / "RP" / "textures" / "item_texture.json"
    alvo.write_text(json.dumps({
        "resource_pack_name": "armas_do_joao",
        "texture_name": "atlas.items",
        "texture_data": {k: {"textures": v} for k, v in texturas.items()},
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def checar():
    erros = 0
    for p in PACKS.rglob("*.json"):
        try:
            ler_json(p)
        except Exception as e:  # noqa: BLE001
            print(f"JSON inválido: {p.relative_to(RAIZ)} — {e}")
            erros += 1
    if (RAIZ / "node_modules" / "@minecraft" / "server").exists():
        npx = "npx.cmd" if os.name == "nt" else "npx"
        r = subprocess.run([npx, "tsc", "-p", "jsconfig.json"], cwd=RAIZ)
        if r.returncode != 0:
            print("tsc encontrou problemas no script")
            erros += 1
    else:
        print("(dica: rode 'npm install' para checar o script contra a API do Minecraft)")
    if erros:
        sys.exit(f"{erros} problema(s) encontrados")
    print("checagem ok")


def empacotar():
    DIST.mkdir(exist_ok=True)
    v = ".".join(str(x) for x in versao_atual())
    destino = DIST / f"Armas_do_Joao_v{v}.mcaddon"
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for pasta, (nome, _) in PASTAS.items():
            for f in sorted((PACKS / pasta).rglob("*")):
                if f.is_file():
                    z.write(f, f"{nome}/{f.relative_to(PACKS / pasta).as_posix()}")
    print(f"pacote: {destino.relative_to(RAIZ)}")
    return destino


def achar_com_mojang():
    candidatos = []
    appdata = os.environ.get("APPDATA")
    local = os.environ.get("LOCALAPPDATA")
    if appdata:   # versões novas (GDK)
        candidatos.append(Path(appdata) / "Minecraft Bedrock" / "Users" / "Shared" / "games" / "com.mojang")
    if local:     # versões antigas (UWP)
        candidatos.append(Path(local) / "Packages" / "Microsoft.MinecraftUWP_8wekyb3d8bbwe" / "LocalState" / "games" / "com.mojang")
    for c in candidatos:
        if c.exists():
            return c
    return None


def deploy(alvo):
    base = Path(alvo) if alvo else achar_com_mojang()
    if not base or not base.exists():
        sys.exit("não achei a pasta com.mojang — passe o caminho: --deploy \"C:/.../com.mojang\"")
    for pasta, (nome, dev) in PASTAS.items():
        dest = base / dev / nome
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(PACKS / pasta, dest)
        print(f"copiado: {dest}")
    print("No jogo: ative os packs no mundo. Mudou só o script? Use /reload. Mudou modelo/textura? Saia e entre no mundo.")


def publicar(pasta):
    npx = "npx.cmd" if os.name == "nt" else "npx"
    r = subprocess.run([npx, "--yes", "vercel", "deploy", str(pasta), "--prod", "--yes"], cwd=RAIZ)
    if r.returncode != 0:
        sys.exit("falhou ao publicar: rode 'npx vercel login' uma vez e tente de novo")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gerar", action="store_true", help="regenera modelos, texturas, ícones e sons")
    ap.add_argument("--versao", help="nova versão X.Y.Z para todos os manifests")
    ap.add_argument("--deploy", nargs="?", const="", help="copia para as pastas de desenvolvimento do Minecraft")
    ap.add_argument("--sem-pacote", action="store_true", help="não gera o .mcaddon")
    ap.add_argument("--site", action="store_true", help="gera o site de downloads em site/")
    ap.add_argument("--publicar", action="store_true", help="gera o site e publica na Vercel")
    a = ap.parse_args()
    if a.versao:
        subir_versao(a.versao)
    if a.gerar:
        gerar()
    checar()
    if not a.sem_pacote:
        empacotar()
    if a.deploy is not None:
        deploy(a.deploy or None)
    if a.site or a.publicar:
        from site_joao import gerar_site
        pasta = gerar_site()
        if a.publicar:
            publicar(pasta)


if __name__ == "__main__":
    main()
