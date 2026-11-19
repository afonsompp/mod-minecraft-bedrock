/**
 * Os dinossauros: o que o JSON da entidade não cobre.
 *
 * Hoje é uma coisa só — **chocar o ovo**, e mesmo isso só como reserva. Quem coloca o bicho é o
 * componente nativo `minecraft:entity_placer` do próprio ovo, o mesmo que o ovo de spawn do jogo
 * usa: ele não depende de evento de script nenhum. Este módulo confere, dois ticks depois do toque,
 * se nasceu alguém ali — e só coloca o bicho se não nasceu.
 *
 * **Por que a reserva existe.** Entre a v1.9.0 e a v1.9.2 o ovo dependia só de script, por três
 * caminhos diferentes (`itemUse`, componente de uso, interação com bloco), e nenhum chegou a
 * disparar no aparelho. Um item que não reage é indistinguível de um item quebrado, então agora o
 * caminho principal é nativo e o script é o cinto de segurança — nunca o contrário.
 *
 * O resto do comportamento (andar, caçar, entrar em pânico, crescer, dormir) é componente nativo no
 * behavior pack, como o `CLAUDE.md` manda. O sono do dardo tranquilizante também não precisa de nada
 * aqui: o bicho declara a família `joao:sedavel` e os eventos `joao:dormir` / `joao:acordar`, e o
 * módulo `sedativo/` já os dispara desde a v1.7.0.
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
 * @param {import("@minecraft/server").Dimension} dim
 * @param {import("@minecraft/server").Vector3} onde
 * @param {string} tipo
 */
function quantosPerto(dim, onde, tipo) {
  try {
    return dim.getEntities({ location: onde, maxDistance: 6, type: tipo }).length;
  } catch {
    return 0;             // área descarregada: trata como "não nasceu ninguém"
  }
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
  if (!primeiroNoTick(p)) return;

  const dim = p.dimension;
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

  const tipo = `joao:${id}`;
  const antes = quantosPerto(dim, onde, tipo);

  // dois ticks de espera: é o que o componente nativo leva para colocar o bicho, se for ele a agir
  system.runTimeout(() => {
    if (quantosPerto(dim, onde, tipo) <= antes) {
      try {
        dim.spawnEntity(tipo, onde);
      } catch {
        hud.barra(p, "§7Aqui não dá. Mire no chão, num lugar aberto.", true);
        return;
      }
      gastar(p, item.typeId);   // no caminho nativo o jogo já consumiu; aqui, consumimos nós
    }
    try {
      dim.playSound("mob.turtle.egg_crack", onde, { pitch: 0.9, volume: 1 });
      particula(dim, "minecraft:egg_destroy_emitter", onde);
    } catch { /* área descarregada */ }
    hud.barra(p, `§aNasceu um §f${especie.nome}§a!`, true);
  }, 2);
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
