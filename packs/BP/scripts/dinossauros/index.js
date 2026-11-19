/**
 * Os dinossauros: o que o JSON da entidade não cobre.
 *
 * Hoje é uma coisa só — **chocar o ovo**. O resto do comportamento (andar, caçar, entrar em pânico,
 * crescer, dormir) é componente nativo no behavior pack, como o `CLAUDE.md` manda: script entra só
 * onde o JSON não chega.
 *
 * O sono do dardo tranquilizante também não precisa de nada aqui: o bicho declara a família
 * `joao:sedavel` e os eventos `joao:dormir` / `joao:acordar`, e o módulo `sedativo/` já os dispara
 * desde a v1.7.0.
 *
 * **Por que dois ganchos para um toque.** O gesto natural é mirar o chão e tocar — e isso no Bedrock
 * é *interação com bloco*, que não passa por `itemUse`. Então o ovo é atendido pelos dois ganchos, e
 * `primeiroNoTick` garante que um toque só choque um ovo mesmo quando os dois disparam juntos.
 */
import { system } from "@minecraft/server";
import { OVO_DINO } from "../comum/tags.js";
import { particula } from "../comum/efeitos.js";
import { gastar } from "../comum/inventario.js";
import * as hud from "../comum/hud.js";
import { POR_ID } from "./especies.js";

/** Último tick em que cada jogador chocou algo: o mesmo toque chega por dois eventos. */
const ultimoToque = new Map();

/** @param {import("@minecraft/server").Player} p */
function primeiroNoTick(p) {
  if (ultimoToque.get(p.id) === system.currentTick) return false;
  ultimoToque.set(p.id, system.currentTick);
  return true;
}

/**
 * @param {import("@minecraft/server").Player} p
 * @param {import("@minecraft/server").ItemStack} item
 * @param {import("@minecraft/server").Block} [bloco] o bloco tocado, quando veio por interação
 */
function chocar(p, item, bloco) {
  const id = item.typeId.slice("joao:ovo_".length);
  const especie = POR_ID[id];
  if (!especie) return;

  // onde ele apontou. Sem bloco à vista, nasce logo à frente dele.
  let onde;
  try {
    const alvo = bloco ?? p.getBlockFromViewDirection({ maxDistance: 6 })?.block;
    // ovo na mão e toque numa máquina do laboratório: ele quis mexer na máquina, não chocar
    if (alvo?.typeId.startsWith("joao:")) return;
    const d = p.getViewDirection();
    onde = alvo
      ? { x: alvo.location.x + 0.5, y: alvo.location.y + 1, z: alvo.location.z + 0.5 }
      : { x: p.location.x + d.x * 2, y: p.location.y, z: p.location.z + d.z * 2 };
  } catch {
    return;
  }

  if (!primeiroNoTick(p)) return;

  try {
    const bicho = p.dimension.spawnEntity(`joao:${id}`, onde);
    bicho.triggerEvent("joao:nascer");          // nasce filhote e cresce sozinho
    if (!gastar(p, item.typeId)) { /* criativo: o ovo não se gasta */ }
    p.dimension.playSound("mob.turtle.egg_crack", onde, { pitch: 0.9, volume: 1 });
    particula(p.dimension, "minecraft:egg_destroy_emitter", onde);
    hud.barra(p, `§aNasceu um §f${especie.nome}§a!`, true);
  } catch {
    hud.barra(p, "§7Aqui não dá. Mire no chão, num lugar aberto.", true);
  }
}

/** @type {import("../comum/dominio.js").Dominio} */
export const dominio = {
  nome: "dinossauros",

  aoUsar(p, item) {
    if (item?.hasTag(OVO_DINO)) chocar(p, item);
  },

  aoUsarEmBloco(p, item, bloco) {
    if (item.hasTag(OVO_DINO)) chocar(p, item, bloco);
  },

  aoSair(playerId) {
    ultimoToque.delete(playerId);
  },
};
