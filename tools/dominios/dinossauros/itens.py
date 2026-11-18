"""Itens e receitas do laboratório, gerados a partir do registro de espécies.

É a primeira vez que o projeto **gera** arquivos do behavior pack: até aqui `packs/BP/**` era todo
escrito à mão, o que funcionava com nove itens e não funciona com dois por espécie.

Tudo o que é gerado vai para a subpasta `dinossauros/` de `items/` e `recipes/` — o Bedrock varre as
subpastas, e assim o que é gerado nunca se mistura com o que é escrito à mão. **Marcar o arquivo com
uma chave de comentário não serve**: o JSON de item só espera `format_version` e `minecraft:item`, e
no Bedrock uma chave a mais é o tipo de coisa que faz o item sumir sem erro nenhum.

O que é escrito:
  joao:fossil          um só, genérico — o extrator é que sorteia de qual bicho era
  joao:ovo_sintetico   um só, da bancada
  joao:dna_<id>        um por espécie
  joao:ovo_<id>        um por espécie, saído da incubadora
"""
import json
from pathlib import Path

SUB = "dinossauros"     # subpasta de items/ e recipes/ onde o gerado mora


def _escrever(caminho, dados):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _item(id_, nome, textura, pilha, tags, extra=None):
    comp = {
        "minecraft:icon": {"textures": {"default": textura}},
        "minecraft:display_name": {"value": nome},
        "minecraft:max_stack_size": pilha,
        "minecraft:tags": {"tags": list(tags)},
    }
    comp.update(extra or {})
    return {"format_version": "1.21.90",
            "minecraft:item": {"description": {"identifier": id_,
                                               "menu_category": {"category": "items"}},
                               "components": comp}}


def gerar(bp, especies):
    """Escreve os itens e as receitas. Devolve os ids criados, para o script e o site."""
    itens, receitas = bp / "items" / SUB, bp / "recipes" / SUB
    # a pasta é só nossa: limpa e reescreve, para espécie removida não deixar item órfão no pacote
    for pasta in (itens, receitas):
        if pasta.exists():
            for antigo in pasta.glob("*.json"):
                antigo.unlink()

    _escrever(itens / "fossil.json",
              _item("joao:fossil", "Fóssil", "joao_fossil", 64, ["joao:fossil"]))
    _escrever(itens / "ovo_sintetico.json",
              _item("joao:ovo_sintetico", "Ovo Sintético", "joao_ovo_sintetico", 16,
                    ["joao:ovo_sintetico"]))

    # A casca vazia é a única coisa do laboratório que se faz na bancada. Argila dá a casca e a
    # slime, a membrana — e as duas são fáceis o bastante para não travar o fluxo logo no começo.
    _escrever(receitas / "ovo_sintetico.json", {
        "format_version": "1.20.10",
        "minecraft:recipe_shaped": {
            "description": {"identifier": "joao:ovo_sintetico"},
            "tags": ["crafting_table"],
            "pattern": [" A ", "ASA", " A "],
            "key": {"A": {"item": "minecraft:clay_ball"}, "S": {"item": "minecraft:slime_ball"}},
            "unlock": [{"item": "joao:fossil"}],
            "result": {"item": "joao:ovo_sintetico", "count": 2},
        }})

    ids = ["joao:fossil", "joao:ovo_sintetico"]
    for e in especies:
        _escrever(itens / f"dna_{e.id}.json",
                  _item(f"joao:dna_{e.id}", f"DNA de {e.nome}", f"joao_dna_{e.id}", 16,
                        ["joao:dna"]))
        # O ovo fecundado não empilha alto de propósito: cada um custou um fóssil, um sorteio e uma
        # incubação, e vê-lo ocupando um slot inteiro ajuda a sentir isso.
        _escrever(itens / f"ovo_{e.id}.json",
                  _item(f"joao:ovo_{e.id}", f"Ovo de {e.nome}", f"joao_ovo_{e.id}", 8,
                        ["joao:ovo_dino"]))
        ids += [f"joao:dna_{e.id}", f"joao:ovo_{e.id}"]
    return ids
