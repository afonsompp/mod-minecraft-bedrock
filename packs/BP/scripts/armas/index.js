// Armas de fogo: tiro por raycast instantâneo, rajada, munição e zoom da mira.
import { EntityDamageCause, system } from "@minecraft/server";
import { COOLDOWN_TIRO } from "../comum/tags.js";
import { contar, ehCriativo, gastar } from "../comum/inventario.js";
import { particula, ponto, rastro } from "../comum/efeitos.js";
import { espalhar, tiro } from "../comum/raycast.js";
import * as hud from "../comum/hud.js";
import * as mira from "../comum/mira.js";

/**
 * @typedef {Object} Arma
 * @property {string} nome
 * @property {number} dano        dano por tiro (1 = meio coração)
 * @property {number} alcance     em blocos
 * @property {number} intervalo   ticks entre tiros (20 ticks = 1 segundo)
 * @property {boolean} automatica
 * @property {string} municao     id do item de munição
 * @property {string} som
 * @property {number} tom
 * @property {number} dispersao   imprecisão do tiro
 * @property {Mira} mira          mira (agachar): zoom e precisão
 * @property {number} [empurrao]  força do empurrão no alvo (padrão 0.4; sniper empurra mais)
 */

/**
 * Mira (ADS). A pose da arma na mira fica no resource pack (agachado = mira completa).
 * Fuzil com luneta: fov bem menor (ex.: 20) e dispersão ~0.
 * @typedef {Object} Mira
 * @property {number} fov         campo de visão ao mirar, em graus. O jogo só aceita de 30 a 110:
 *                                fora disso o zoom é recusado e a mira fica sem ampliação.
 * @property {number} dispersao   multiplicador da dispersão ao mirar
 */

/** @type {Record<string, Arma>} */
const ARMAS = {
  "joao:glock": {
    nome: "Glock", dano: 6, alcance: 48, intervalo: 5, automatica: false,
    municao: "joao:municao_pistola", som: "joao.glock.tiro", tom: 1.0, dispersao: 0.01,
    mira: { fov: 58, dispersao: 0.4 },
  },
  "joao:ak47": {
    nome: "AK-47", dano: 8, alcance: 64, intervalo: 3, automatica: true,
    municao: "joao:municao_fuzil", som: "joao.ak47.tiro", tom: 1.0, dispersao: 0.035,
    mira: { fov: 52, dispersao: 0.3 },
  },
  "joao:m4a4": {
    nome: "M4A4", dano: 7, alcance: 64, intervalo: 3, automatica: true,
    municao: "joao:municao_fuzil", som: "joao.m4a4.tiro", tom: 1.0, dispersao: 0.02,
    mira: { fov: 52, dispersao: 0.3 },
  },
  // Sniper de ferrolho: 1 tiro por toque, ciclo longo, derruba a maioria dos bichos num tiro.
  // Sem luneta (de quadril) é muito imprecisa; na luneta vira um laser, como no CS.
  "joao:awp": {
    nome: "AWP", dano: 30, alcance: 160, intervalo: 25, automatica: false,
    municao: "joao:municao_sniper", som: "joao.awp.tiro", tom: 1.0, dispersao: 0.12,
    mira: { fov: 30, dispersao: 0.04 }, empurrao: 1.0,
  },
};

/** @type {Record<string, string>} */
const NOME_MUNICAO = {
  "joao:municao_pistola": "Munição de Pistola",
  "joao:municao_fuzil": "Munição de Fuzil",
  "joao:municao_sniper": "Munição de Sniper",
};

/** @type {Map<string, number>} próximo tick em que cada jogador pode atirar */
const proximoTiro = new Map();
/** @type {Map<string, string>} jogadores segurando o gatilho de uma arma automática */
const atirando = new Map();
/** Mostra arma e munição na actionbar. Mirando, nunca mostra, e limpa o que estiver na tela.
 * @param {import("@minecraft/server").Player} p @param {string} id @param {boolean} [forcar] */
function mostrarMunicao(p, id, forcar) {
  const arma = ARMAS[id];
  if (p.isSneaking) {                      // na mira a tela fica limpa
    hud.limpar(p);
    return;
  }
  const qtd = ehCriativo(p) ? "∞" : String(contar(p, arma.municao));
  hud.barra(p, `§e${arma.nome} §7| §f${NOME_MUNICAO[arma.municao]}: §a${qtd}`, forcar);
}

/** @param {import("@minecraft/server").Player} p @param {string} id */
function atirar(p, id) {
  const arma = ARMAS[id];
  if (!arma) return;

  const agora = system.currentTick;
  if ((proximoTiro.get(p.id) ?? 0) > agora) return;
  proximoTiro.set(p.id, agora + arma.intervalo);

  if (!ehCriativo(p) && !gastar(p, arma.municao)) {
    p.playSound("joao.vazio");
    p.onScreenDisplay.setActionBar(`§cSem ${NOME_MUNICAO[arma.municao]}! Faça mais na bancada.`);
    atirando.delete(p.id);
    return;
  }
  // a partir daqui o tiro sai: avisa a animação da arma
  try {
    p.startItemCooldown(COOLDOWN_TIRO, arma.intervalo);
  } catch {
    /* mundo descarregado ou jogador saindo: a animação só perde um quadro */
  }

  const dim = p.dimension;
  const origem = p.getHeadLocation();
  const dir = espalhar(p.getViewDirection(), arma.dispersao * (p.isSneaking ? arma.mira.dispersao : 1));
  const { distancia, alvo, bloco } = tiro(dim, origem, dir, arma.alcance, p.id);

  if (alvo) {
    try {
      alvo.applyDamage(arma.dano, { cause: EntityDamageCause.entityAttack, damagingEntity: p });
      const emp = arma.empurrao ?? 0.4;
      alvo.applyKnockback({ x: dir.x * emp, z: dir.z * emp }, 0.1 * emp / 0.4);
    } catch {
      // algumas entidades não aceitam empurrão — tudo bem
    }
    particula(dim, "minecraft:critical_hit_emitter", ponto(origem, dir, distancia));
    p.playSound("random.orb", { pitch: 2, volume: 0.4 }); // "plim" de acerto
  } else if (bloco) {
    particula(dim, "minecraft:basic_smoke_particle", ponto(origem, dir, distancia - 0.1));
  }

  // Som (com pequena variação) e rastro da bala — o clarão do cano fica no modelo 3D
  dim.playSound(arma.som, origem, { volume: 1, pitch: arma.tom * (0.95 + Math.random() * 0.1) });
  rastro(dim, origem, dir, distancia);

  mostrarMunicao(p, id, true);
}

/** Agachado com arma na mão = FOV da arma; senão, FOV normal.
 * @param {import("@minecraft/server").Player} p @param {string | undefined} id */
function atualizarMira(p, id) {
  const arma = id ? ARMAS[id] : undefined;
  mira.zoom(p, arma && p.isSneaking ? arma.mira.fov : undefined, "armas");
}

/** @type {import("../comum/dominio.js").Dominio} */
export const dominio = {
  nome: "armas",

  // Toque/clique: um tiro (vale para todas, inclusive as automáticas)
  aoUsar(p, item) {
    if (ARMAS[item.typeId]) atirar(p, item.typeId);
  },

  // Segurar: rajada nas automáticas
  aoComecarUso(p, item) {
    if (item && ARMAS[item.typeId]?.automatica) atirando.set(p.id, item.typeId);
  },

  aoSoltarUso(p) {
    atirando.delete(p.id);
  },

  // rajada, zoom da mira e (a cada 10 ticks) contador de munição
  aCadaTick(p, id) {
    const arma = atirando.get(p.id);
    if (arma) {
      if (id === arma) atirar(p, arma);
      else atirando.delete(p.id);
    }
    atualizarMira(p, id);
    const mostrar = system.currentTick % 10 === 0;
    if (mostrar && id && ARMAS[id] && !atirando.has(p.id)) mostrarMunicao(p, id);
    else if (mostrar && !id) hud.esquecer(p.id);   // guardou a arma: próxima vez mostra de novo
  },

  aoSair(playerId) {
    atirando.delete(playerId);
    proximoTiro.delete(playerId);
    mira.esquecer(playerId);
  },
};
