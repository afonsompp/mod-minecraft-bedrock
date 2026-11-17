/** Partículas e sons. Tudo em try/catch: fora da área carregada o jogo recusa, e isso não é erro. */

/** @param {import("@minecraft/server").Dimension} dim @param {string} efeito
 *  @param {import("@minecraft/server").Vector3} loc */
export function particula(dim, efeito, loc) {
  try {
    dim.spawnParticle(efeito, loc);
  } catch {
    // fora da área carregada — ignora
  }
}

/** Ponto a `t` blocos da origem, na direção `d` (unitária).
 * @param {import("@minecraft/server").Vector3} o @param {import("@minecraft/server").Vector3} d
 * @param {number} t */
export function ponto(o, d, t) {
  return { x: o.x + d.x * t, y: o.y + d.y * t, z: o.z + d.z * t };
}

/** Rastro de partículas ao longo do tiro. Começa a 3 blocos para não estourar na cara do jogador.
 * @param {import("@minecraft/server").Dimension} dim @param {import("@minecraft/server").Vector3} origem
 * @param {import("@minecraft/server").Vector3} dir @param {number} distancia @param {string} [efeito] */
export function rastro(dim, origem, dir, distancia, efeito = "minecraft:basic_crit_particle") {
  for (let t = 3; t < distancia; t += 2) particula(dim, efeito, ponto(origem, dir, t));
}
