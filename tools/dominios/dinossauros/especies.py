"""Fonte única das espécies do modpack.

**Para acrescentar um dinossauro, acrescente uma linha em `ESPECIES`.** Dela saem sozinhos: o item de
DNA e o de ovo (JSON, ícone e entrada no atlas), a entidade do behavior pack, a client entity do
resource pack, a geometria, as animações e o peso no sorteio do extrator.

O fluxo que o João pediu, e onde cada campo entra:

    minerar fundo  ->  joao:fossil  --(extrator)-->  joao:dna_<id>   (sorteado por `raridade`)
    joao:dna_<id> + joao:ovo_sintetico  --(incubadora, `incubacao` s)-->  joao:ovo_<id>
    joao:ovo_<id> no chão  ->  choca  ->  joao:<id>

Híbrido é uma espécie como qualquer outra — modelo próprio, animações próprias. O que o distingue é
`genes`: a incubadora, ao receber dois DNAs, procura a espécie cujo `genes` casa com o par.
"""
from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Especie:
    """Um dinossauro do modpack, dos ossos no chão até o bicho andando."""

    id: str
    """Sem namespace: `velociraptor` vira `joao:velociraptor`, `joao:dna_velociraptor`, `joao:ovo_velociraptor`."""

    nome: str
    """Como aparece na tela. Vira "DNA de <nome>" e "Ovo de <nome>"."""

    dieta: str
    """`carnivoro` ou `herbivoro` — vira a família `joao:dino_carnivoro` / `joao:dino_herbivoro`."""

    raridade: int
    """Peso no sorteio do extrator. Quanto maior, mais comum. Um bicho de peso 2 contra um de 8 sai
    quatro vezes menos."""

    vida: int
    dano: int
    velocidade: float
    """`minecraft:movement` do bicho. Um lobo do jogo anda a 0,3; um cavalo, a 0,22."""

    altura: float
    """Em metros, do chão ao alto da cabeça em pé. É o número que decide a escala do modelo e a
    `collision_box` — e o que o João vai comparar com o que ele viu no filme."""

    comprimento: float
    """Em metros, do focinho à ponta da cauda."""

    cor: tuple
    """RGB do bicho. Pinta o líquido do tubo de DNA e as manchas do ovo, para dar para saber o que é
    sem ler o nome."""

    incubacao: int
    """Segundos na incubadora."""

    genes: tuple = ()
    """Vazio = espécie natural, e o DNA dela sai do extrator. Preenchido = **híbrido**: não aparece no
    sorteio, e o ovo só sai misturando na incubadora os DNAs listados aqui."""

    modelo: Callable | None = None
    """A função que devolve a lista de `Osso` do bicho. Sem ela, a espécie existe só como DNA e ovo
    — foi assim que o Velociraptor passou a v1.8.0 inteira, enquanto o laboratório era construído."""

    doses: int = field(default=0)
    """Dardos tranquilizantes para apagar o bicho. 0 = calcula pela vida (um a cada 10, de 1 a 5),
    que é a mesma conta que o módulo do sedativo já faz com os bichos do jogo."""


def _raptor():
    # import tardio: o módulo do modelo importa o núcleo, e o registro é lido por quem só quer a lista
    from dominios.dinossauros import raptor
    return raptor


ESPECIES = (
    # O raptor do cinema, não o do registro fóssil (que tinha o tamanho de um peru) — a régua do João
    # é o filme. Carnívoro rápido, caça em bando.
    Especie("velociraptor", "Velociraptor", "carnivoro", raridade=8,
            vida=30, dano=6, velocidade=0.42, altura=1.8, comprimento=3.5,
            cor=(0x6f, 0x7a, 0x4a), incubacao=90, modelo=lambda: _raptor().modelo()),
)

POR_ID = {e.id: e for e in ESPECIES}
NATURAIS = tuple(e for e in ESPECIES if not e.genes)
"""As que o extrator pode sortear. Híbrido não vem de fóssil: vem da incubadora."""

HIBRIDAS = tuple(e for e in ESPECIES if e.genes)


def sorteio():
    """Pares (id, peso) para o extrator — o script recebe isto pronto, em vez de uma tabela à mão."""
    return [(e.id, e.raridade) for e in NATURAIS]


def doses(e):
    """Quantos dardos a besta precisa. Mesma conta do `sedativo/index.js` para os bichos do jogo."""
    return e.doses or max(1, min(5, -(-e.vida // 10)))
