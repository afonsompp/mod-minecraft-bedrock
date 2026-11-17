import { GameMode } from "@minecraft/server";

/** Item na mão principal (undefined se a mão está vazia).
 * @param {import("@minecraft/server").Player} p */
export function itemNaMao(p) {
  const inv = p.getComponent("minecraft:inventory");
  return inv?.container?.getItem(p.selectedSlotIndex);
}

/** @param {import("@minecraft/server").Player} p */
export function ehCriativo(p) {
  return p.getGameMode() === GameMode.Creative;
}

/** Quantos itens desse tipo o jogador tem no inventário inteiro.
 * @param {import("@minecraft/server").Player} p @param {string} id */
export function contar(p, id) {
  const c = p.getComponent("minecraft:inventory")?.container;
  if (!c) return 0;
  let total = 0;
  for (let i = 0; i < c.size; i++) {
    const it = c.getItem(i);
    if (it?.typeId === id) total += it.amount;
  }
  return total;
}

/** Gasta uma unidade. Devolve false se não havia nenhuma.
 * @param {import("@minecraft/server").Player} p @param {string} id */
export function gastar(p, id) {
  const c = p.getComponent("minecraft:inventory")?.container;
  if (!c) return false;
  for (let i = 0; i < c.size; i++) {
    const it = c.getItem(i);
    if (it?.typeId !== id) continue;
    if (it.amount > 1) {
      it.amount -= 1;
      c.setItem(i, it);
    } else {
      c.setItem(i, undefined);
    }
    return true;
  }
  return false;
}
