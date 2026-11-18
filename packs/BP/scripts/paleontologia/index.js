/**
 * De onde vêm os fósseis: minerar fundo.
 *
 * **Por que no script e não na geração de mundo.** O jeito "certo" seria um bloco nosso espalhado
 * por `feature_rules`, como um minério. Só que feature rules povoam apenas pedaço de mundo **novo**
 * — e o João já joga num mundo que existe há tempo, onde nada disso apareceria perto de casa. Em
 * jogos anteriores à 1.21.110 elas ainda exigem ligar o Experimento "Criação de Biomas
 * Personalizados" no mundo, e o `min_engine_version` do projeto é 1.21.90.
 *
 * Aqui, o fóssil pode sair de qualquer pedra que ele quebre, no mundo de hoje, sem ligar nada. A
 * chance e a profundidade são dados, fáceis de calibrar depois do primeiro teste.
 */
import { ItemStack, world } from "@minecraft/server";
import { FOSSIL } from "../comum/tags.js";
import { particula } from "../comum/efeitos.js";
import * as hud from "../comum/hud.js";

/** Onde osso fossilizado faz sentido: rocha e sedimento, não madeira nem minério. */
const ROCHAS = new Set([
  "minecraft:stone", "minecraft:cobblestone", "minecraft:andesite", "minecraft:diorite",
  "minecraft:granite", "minecraft:tuff", "minecraft:deepslate", "minecraft:cobbled_deepslate",
  "minecraft:gravel", "minecraft:clay", "minecraft:sandstone", "minecraft:dripstone_block",
]);

/** Acima desta altura não há nada: fóssil é coisa de camada funda. */
const TETO = 24;
/** Chance por bloco quebrado, do teto para baixo. Quanto mais fundo, mais osso. */
const CHANCE_RASA = 1 / 420;
const CHANCE_FUNDA = 1 / 150;
const FUNDO = -24;

/** @param {number} y */
function chance(y) {
  if (y > TETO) return 0;
  const t = Math.min(1, Math.max(0, (TETO - y) / (TETO - FUNDO)));
  return CHANCE_RASA + (CHANCE_FUNDA - CHANCE_RASA) * t;
}

/** @type {import("../comum/dominio.js").Dominio} */
export const dominio = {
  nome: "paleontologia",

  iniciar() {
    world.afterEvents.playerBreakBlock.subscribe((ev) => {
      const quebrado = ev.brokenBlockPermutation?.type?.id;
      if (!quebrado || !ROCHAS.has(quebrado)) return;
      const loc = ev.block.location;
      if (Math.random() >= chance(loc.y)) return;

      const centro = { x: loc.x + 0.5, y: loc.y + 0.5, z: loc.z + 0.5 };
      try {
        ev.dimension.spawnItem(new ItemStack(FOSSIL, 1), centro);
        ev.dimension.playSound("block.bone_block.break", centro, { pitch: 0.75, volume: 0.9 });
      } catch {
        return;     // a área saiu de carregada entre quebrar o bloco e isto
      }
      particula(ev.dimension, "minecraft:basic_crit_particle", centro);
      hud.barra(ev.player, "§eUm Fóssil! §7Leve-o ao Extrator de DNA.", true);
    });
  },
};
