"""As cinco armas de fogo e a besta: modelos, pose de 1ª/3ª pessoa, sons e munição.

Ponto de entrada do domínio para o `build.py --gerar`. A ordem aqui importa: `attachables.main` produz as
prévias laterais de que o ícone do pack depende, e `pose.py` reaproveita o `player.entity.json` que
já está no RP como base.
"""
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2]


def gerar(rp, bp, previews):
    """Escreve o resource pack das armas. `bp` ainda não é usado: item e receita são escritos à mão."""
    from dominios.armas import dardo
    from dominios.armas import attachables
    attachables.main(rp, previews)
    dardo.main(rp, previews)      # entidade do dardo em voo (modelo, textura, client entity)
    py = sys.executable
    subprocess.run([py, "-m", "dominios.armas.sons", str(rp / "sounds" / "joao")], check=True, cwd=TOOLS)
    subprocess.run([py, "-m", "dominios.armas.municao", str(rp / "textures" / "items"), str(previews)],
                   check=True, cwd=TOOLS)
    # pose de mira em 3ª pessoa
    subprocess.run([py, "-m", "dominios.armas.pose"], check=True, cwd=TOOLS)
