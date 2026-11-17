import { ATRAVESSA } from "./tags.js";

/** Espalha a direção do tiro (dispersão) e renormaliza.
 * @param {import("@minecraft/server").Vector3} v @param {number} s */
export function espalhar(v, s) {
  const x = v.x + (Math.random() - 0.5) * 2 * s;
  const y = v.y + (Math.random() - 0.5) * 2 * s;
  const z = v.z + (Math.random() - 0.5) * 2 * s;
  const len = Math.hypot(x, y, z) || 1;
  return { x: x / len, y: y / len, z: z / len };
}

/**
 * Tiro instantâneo: acha o bloco e, antes dele, o primeiro bicho no caminho.
 * @param {import("@minecraft/server").Dimension} dim
 * @param {import("@minecraft/server").Vector3} origem
 * @param {import("@minecraft/server").Vector3} dir  unitária
 * @param {number} alcance em blocos
 * @param {string} atirador id do jogador, para o tiro não acertar ele mesmo
 * @returns {{ distancia: number, alvo: import("@minecraft/server").Entity | undefined, bloco: boolean }}
 */
export function tiro(dim, origem, dir, alcance, atirador) {
  let distancia = alcance;
  const bloco = dim.getBlockFromRay(origem, dir, { maxDistance: alcance });
  if (bloco) {
    const b = bloco.block.location;
    const f = bloco.faceLocation;
    const hit = { x: b.x + f.x, y: b.y + f.y, z: b.z + f.z };
    distancia = Math.hypot(hit.x - origem.x, hit.y - origem.y, hit.z - origem.z);
  }
  const acerto = dim
    .getEntitiesFromRay(origem, dir, { maxDistance: distancia })
    .find((h) => h.entity.id !== atirador && !ATRAVESSA.has(h.entity.typeId) && h.distance <= distancia);
  if (acerto) distancia = acerto.distance;
  return { distancia, alvo: acerto?.entity, bloco: Boolean(bloco) };
}
