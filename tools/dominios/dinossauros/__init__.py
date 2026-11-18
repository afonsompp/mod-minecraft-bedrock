"""Dinossauros: o laboratório (fóssil → DNA → ovo) e, depois, as criaturas.

Ponto de entrada do domínio para o `build.py --gerar`. Tudo o que ele escreve sai de
`especies.py` — acrescentar um dinossauro é uma linha lá.
"""
from dominios.dinossauros import especies, icones, itens


def gerar(rp, bp, previews):
    """Escreve os ícones (RP) e os itens e receitas (BP). Devolve as texturas de item para o atlas."""
    destino = rp / "textures" / "items"
    destino.mkdir(parents=True, exist_ok=True)
    nomes = icones.gerar(str(destino), str(previews), especies.ESPECIES)
    itens.gerar(bp, especies.ESPECIES)
    print(f"dinossauros ok — {len(especies.ESPECIES)} espécie(s)")
    return nomes
