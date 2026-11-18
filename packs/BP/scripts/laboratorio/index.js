/**
 * O laboratório: o Extrator de DNA e a Incubadora.
 *
 * Os dois são **blocos com componente customizado** (`joao:maquina`), o mesmo mecanismo das armas do
 * outro lado da API. Quando o jogador toca no bloco, o jogo chama `onPlayerInteract` e entrega os
 * parâmetros escritos no JSON — aqui, só qual máquina é.
 *
 * **Onde mora o estado.** Uma máquina precisa lembrar o que está dentro e quando fica pronta, e isso
 * tem de sobreviver a sair do mundo. Não uso `minecraft:block_entity` (é recente, e o projeto não
 * precisa dele): o estado vai numa dynamic property do mundo, com a chave formada pela dimensão e
 * pela coordenada. O bloco em si só carrega a **fase**, que é o que se vê — luz e, na incubadora, o
 * ovo no ninho.
 */
import { ItemStack, system, world } from "@minecraft/server";
import { FOSSIL, OVO_SINTETICO, MAQUINA, ESTADO_FASE } from "../comum/tags.js";
import { contar, itemNaMao } from "../comum/inventario.js";
import { particula } from "../comum/efeitos.js";
import * as hud from "../comum/hud.js";
import { POR_ID, sortear } from "../dinossauros/especies.js";

const EXTRATOR = "extrator_dna";
const INCUBADORA = "incubadora";
const MOER = 6;              // segundos que o extrator leva para moer um fóssil

const PREFIXO = "joao:lab:";
/** @type {Map<string, Maquina>} máquinas em andamento, para o laço não varrer o mundo todo */
const ativas = new Map();

/**
 * @typedef {Object} Maquina
 * @property {string} dim
 * @property {number} x
 * @property {number} y
 * @property {number} z
 * @property {number} pronta   tick em que termina
 * @property {string} saida    id do item que vai sair
 */

/** @param {import("@minecraft/server").Block} b */
function chave(b) {
  return `${PREFIXO}${b.dimension.id}:${b.location.x},${b.location.y},${b.location.z}`;
}

/** @param {string} k @returns {Maquina | undefined} */
function ler(k) {
  const bruto = world.getDynamicProperty(k);
  if (typeof bruto !== "string") return undefined;
  try {
    return JSON.parse(bruto);
  } catch {
    return undefined;       // guardado por uma versão antiga do add-on: trata como vazia
  }
}

/** @param {string} k @param {Maquina | undefined} m */
function guardar(k, m) {
  world.setDynamicProperty(k, m ? JSON.stringify(m) : undefined);
  if (m) ativas.set(k, m);
  else ativas.delete(k);
}

/** Muda a fase do bloco — a luz e, na incubadora, o ovo no ninho.
 * @param {import("@minecraft/server").Block} b @param {number} valor */
function fase(b, valor) {
  try {
    // o estado é nosso (joao:fase), e a tipagem só conhece os do jogo
    const estado = /** @type {any} */ (ESTADO_FASE);
    b.setPermutation(b.permutation.withState(estado, valor));
  } catch {
    /* o bloco foi quebrado entre o começo e o fim do trabalho */
  }
}

/** @param {import("@minecraft/server").Player} p @param {string} id quantos itens desse tipo tirar */
function gastarUm(p, id) {
  const inv = p.getComponent("inventory")?.container;
  if (!inv) return false;
  for (let i = 0; i < inv.size; i++) {
    const it = inv.getItem(i);
    if (it?.typeId !== id) continue;
    if (it.amount > 1) {
      it.amount -= 1;
      inv.setItem(i, it);
    } else {
      inv.setItem(i, undefined);
    }
    return true;
  }
  return false;
}

/** Entrega o que a máquina produziu, em cima dela. @param {Maquina} m */
function entregar(m) {
  const dim = world.getDimension(m.dim);
  try {
    dim.spawnItem(new ItemStack(m.saida, 1), { x: m.x + 0.5, y: m.y + 1.2, z: m.z + 0.5 });
    dim.playSound("random.levelup", { x: m.x, y: m.y, z: m.z }, { pitch: 1.4, volume: 0.5 });
  } catch {
    /* área descarregada: o item fica para quando alguém voltar (ver o laço) */
  }
}

/** @param {import("@minecraft/server").Player} p @param {import("@minecraft/server").Block} b */
function usarExtrator(p, b) {
  const k = chave(b);
  if (ler(k)) {
    hud.barra(p, "§7O extrator está trabalhando…", true);
    return;
  }
  if (itemNaMao(p)?.typeId !== FOSSIL) {
    hud.barra(p, "§7Precisa de um §fFóssil§7 na mão. Cave fundo para achar.", true);
    return;
  }
  if (!gastarUm(p, FOSSIL)) return;

  // qual bicho era aquele osso só se descobre agora — é o que dá graça a cavar
  const especie = sortear();
  guardar(k, { dim: b.dimension.id, x: b.location.x, y: b.location.y, z: b.location.z,
               pronta: system.currentTick + MOER * 20, saida: `joao:dna_${especie}` });
  fase(b, 1);
  b.dimension.playSound("block.barrel.open", b.location, { pitch: 0.8 });
  hud.barra(p, "§bExtraindo DNA…", true);
}

/** @param {import("@minecraft/server").Player} p @param {import("@minecraft/server").Block} b */
function usarIncubadora(p, b) {
  const k = chave(b);
  const m = ler(k);
  if (m) {
    if (system.currentTick < m.pronta) {
      const faltam = Math.ceil((m.pronta - system.currentTick) / 20);
      hud.barra(p, `§7Incubando… §f${faltam}s`, true);
    } else {
      entregar(m);              // o ovo estava pronto no ninho, esperando ser recolhido
      guardar(k, undefined);
      fase(b, 0);
    }
    return;
  }

  const mao = itemNaMao(p);
  const id = mao?.typeId ?? "";
  if (!id.startsWith("joao:dna_")) {
    hud.barra(p, "§7Precisa de um §fDNA§7 na mão. Faça-o no Extrator.", true);
    return;
  }
  if (contar(p, OVO_SINTETICO) < 1) {
    hud.barra(p, "§7Falta um §fOvo Sintético§7 — ele se faz na bancada.", true);
    return;
  }
  const especie = POR_ID[id.slice("joao:dna_".length)];
  if (!especie) return;

  gastarUm(p, id);
  gastarUm(p, OVO_SINTETICO);
  guardar(k, { dim: b.dimension.id, x: b.location.x, y: b.location.y, z: b.location.z,
               pronta: system.currentTick + especie.incubacao * 20,
               saida: `joao:ovo_${especie.id}` });
  fase(b, 1);
  b.dimension.playSound("block.beehive.enter", b.location, { pitch: 0.9 });
  hud.barra(p, `§bIncubando §f${especie.nome}§b…`, true);
}

/** @type {import("../comum/dominio.js").Dominio} */
export const dominio = {
  nome: "laboratorio",

  componentes(ev) {
    ev.blockComponentRegistry.registerCustomComponent(MAQUINA, {
      onPlayerInteract({ block, player }, { params }) {
        if (!player) return;
        const tipo = /** @type {{ tipo: string }} */ (params).tipo;
        if (tipo === EXTRATOR) usarExtrator(player, block);
        else if (tipo === INCUBADORA) usarIncubadora(player, block);
      },
    });
  },

  iniciar() {
    // recupera o que estava em andamento quando o mundo fechou
    for (const k of world.getDynamicPropertyIds()) {
      if (!k.startsWith(PREFIXO)) continue;
      const m = ler(k);
      if (m) ativas.set(k, m);
    }

    // Um laço só, de segundo em segundo, e apenas sobre as máquinas em andamento.
    system.runInterval(() => {
      const agora = system.currentTick;
      for (const [k, m] of [...ativas]) {
        let bloco;
        try {
          bloco = world.getDimension(m.dim).getBlock({ x: m.x, y: m.y, z: m.z });
        } catch {
          continue;             // área descarregada: fica para a próxima volta
        }
        if (!bloco || !bloco.typeId.startsWith("joao:")) {
          guardar(k, undefined);   // alguém quebrou a máquina no meio do trabalho
          continue;
        }
        if (agora < m.pronta) {
          if (agora % 40 === 0) {
            particula(bloco.dimension, "minecraft:basic_smoke_particle",
                      { x: m.x + 0.5, y: m.y + 1.1, z: m.z + 0.5 });
          }
          continue;
        }
        // terminou. O extrator entrega sozinho; a incubadora segura o ovo à vista, no ninho.
        if (bloco.typeId === `joao:${INCUBADORA}`) {
          // o ovo fica à vista no ninho até alguém recolher. Sai do laço, mas o estado continua
          // guardado: sem isso o laço reporia a fase 2 a cada segundo, para sempre.
          fase(bloco, 2);
          ativas.delete(k);
        } else {
          entregar(m);
          guardar(k, undefined);
          fase(bloco, 0);
        }
      }
    }, 20);
  },
};
