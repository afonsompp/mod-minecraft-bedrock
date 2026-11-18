"""Leva o registro de espécies para o lado do script.

O `especies.py` é a fonte única, mas o script do behavior pack é JavaScript e não lê Python. Em vez
de manter a mesma lista nos dois lados — que é exatamente o erro que a v1.7.2 acabou de tirar das
armas —, o gerador **escreve** o módulo JS. Ele entra no `npm run check` como qualquer outro.
"""
import json

CABECA = """// GERADO por tools/dominios/dinossauros/dados.py — não edite à mão.
// A fonte é tools/dominios/dinossauros/especies.py; acrescentar uma espécie é uma linha lá.

/**
 * @typedef {Object} Especie
 * @property {string} id
 * @property {string} nome
 * @property {number} raridade    peso no sorteio do extrator (0 = híbrido, não sai de fóssil)
 * @property {number} incubacao   segundos na incubadora
 * @property {string[]} genes     vazio em espécie natural; nos híbridos, os DNAs que a receita pede
 */

/** @type {Especie[]} */
export const ESPECIES = """


def gerar(bp, especies):
    linhas = [{"id": e.id, "nome": e.nome,
               "raridade": 0 if e.genes else e.raridade,
               "incubacao": e.incubacao, "genes": list(e.genes)} for e in especies]
    destino = bp / "scripts" / "dinossauros"
    destino.mkdir(parents=True, exist_ok=True)
    corpo = CABECA + json.dumps(linhas, indent=2, ensure_ascii=False) + """;

/** @type {Record<string, Especie>} */
export const POR_ID = Object.fromEntries(ESPECIES.map((e) => [e.id, e]));

/** As que o extrator pode sortear: híbrido não vem de fóssil, vem da incubadora. */
export const NATURAIS = ESPECIES.filter((e) => e.raridade > 0);

/** Sorteia uma espécie pelo peso de raridade. Devolve o id. */
export function sortear() {
  const total = NATURAIS.reduce((s, e) => s + e.raridade, 0);
  let n = Math.random() * total;
  for (const e of NATURAIS) {
    n -= e.raridade;
    if (n <= 0) return e.id;
  }
  return NATURAIS[NATURAIS.length - 1].id;
}

/** O híbrido cujo par de genes casa com esses dois DNAs, ou undefined.
 * @param {string} a @param {string} b */
export function hibridoDe(a, b) {
  const par = [a, b].sort().join("+");
  return ESPECIES.find((e) => e.genes.length === 2 && [...e.genes].sort().join("+") === par);
}
"""
    (destino / "especies.js").write_text(corpo, encoding="utf-8")
    return len(linhas)
