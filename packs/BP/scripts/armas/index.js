// Armas de fogo: tiro por raycast instantâneo, rajada, munição e zoom da mira.
//
// Nada aqui sabe o nome de nenhuma arma. Os números de cada uma (dano, alcance, cadência, munição,
// som, dispersão) moram no JSON do item, no componente customizado `joao:arma_fogo`, e chegam a este
// módulo pelo `params` do componente. Acrescentar uma arma é escrever um item novo — este arquivo não
// muda. Quem diz "sou arma" e "sou de rajada" são as tags `minecraft:tags` do item.
import { EntityDamageCause, system } from "@minecraft/server";
import { ARMA_FOGO, COOLDOWN_TIRO, RAJADA } from "../comum/tags.js";
import { contar, ehCriativo, gastar } from "../comum/inventario.js";
import { particula, ponto, rastro } from "../comum/efeitos.js";
import { espalhar, tiro } from "../comum/raycast.js";
import * as hud from "../comum/hud.js";
import * as mira from "../comum/mira.js";

/**
 * A ficha de uma arma, como está escrita no componente `joao:arma_fogo` do JSON do item.
 * As chaves são planas de propósito: o `params` de um componente customizado é dado cru, e aninhar
 * objetos ali é pedir para descobrir um limite do Bedrock no meio do caminho.
 *
 * @typedef {Object} Ficha
 * @property {string} nome
 * @property {number} dano             por tiro (1 = meio coração)
 * @property {number} alcance          em blocos
 * @property {number} intervalo        ticks entre tiros (20 ticks = 1 segundo)
 * @property {string} municao          id do item de munição
 * @property {string} municao_nome     como ela aparece na actionbar
 * @property {string} som
 * @property {number} tom
 * @property {number} dispersao        imprecisão do tiro
 * @property {number} mira_fov         campo de visão ao mirar, em graus. O jogo só aceita de 30 a
 *                                     110: fora disso o zoom é recusado e a mira fica sem ampliação
 * @property {number} mira_dispersao   multiplicador da dispersão ao mirar
 * @property {number} [empurrao]       força do empurrão no alvo (padrão 0.4; sniper empurra mais)
 */

/**
 * Fichas já vistas, por id de item.
 *
 * O jogo só entrega o `params` de um componente quando ele **dispara**, e não existe gancho de
 * "equipou o item". Então a ficha entra aqui no primeiro uso da arma, que é também o primeiro tiro.
 * Consequência, pequena e de propósito: ao pegar uma arma e agachar **antes** de atirar uma vez, a
 * mira funciona (a pose vem do resource pack) mas ainda sem ampliação — e o zoom depende de Cheats
 * de qualquer modo. A partir do primeiro tiro, tudo normal.
 * @type {Map<string, Ficha>}
 */
const FICHA = new Map();

/** @type {Map<string, number>} próximo tick em que cada jogador pode atirar */
const proximoTiro = new Map();
/** @type {Map<string, string>} jogadores segurando o gatilho de uma arma de rajada */
const atirando = new Map();

/** Mostra arma e munição na actionbar. Mirando, nunca mostra, e limpa o que estiver na tela.
 * @param {import("@minecraft/server").Player} p @param {Ficha} arma @param {boolean} [forcar] */
function mostrarMunicao(p, arma, forcar) {
  if (p.isSneaking) {                      // na mira a tela fica limpa
    hud.limpar(p);
    return;
  }
  const qtd = ehCriativo(p) ? "∞" : String(contar(p, arma.municao));
  hud.barra(p, `§e${arma.nome} §7| §f${arma.municao_nome}: §a${qtd}`, forcar);
}

/** @param {import("@minecraft/server").Player} p @param {Ficha} arma */
function atirar(p, arma) {
  const agora = system.currentTick;
  if ((proximoTiro.get(p.id) ?? 0) > agora) return;
  proximoTiro.set(p.id, agora + arma.intervalo);

  if (!ehCriativo(p) && !gastar(p, arma.municao)) {
    p.playSound("joao.vazio");
    p.onScreenDisplay.setActionBar(`§cSem ${arma.municao_nome}! Faça mais na bancada.`);
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
  const dir = espalhar(p.getViewDirection(), arma.dispersao * (p.isSneaking ? arma.mira_dispersao : 1));
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

  mostrarMunicao(p, arma, true);
}

/** Agachado com arma na mão = FOV da arma; senão, FOV normal.
 * @param {import("@minecraft/server").Player} p @param {Ficha | undefined} arma */
function atualizarMira(p, arma) {
  mira.zoom(p, arma && p.isSneaking ? arma.mira_fov : undefined, "armas");
}

/** @type {import("../comum/dominio.js").Dominio} */
export const dominio = {
  nome: "armas",

  // O tiro é o próprio componente do item: toque/clique chama onUse, e é dali que vêm os números.
  // Vale para todas as armas, inclusive as de rajada — é também o caminho de reserva se segurar
  // para atirar não funcionar no celular.
  componentes(ev) {
    ev.itemComponentRegistry.registerCustomComponent(ARMA_FOGO, {
      onUse({ source, itemStack }, { params }) {
        const arma = /** @type {Ficha} */ (params);
        if (itemStack) FICHA.set(itemStack.typeId, arma);
        atirar(source, arma);
      },
    });
  },

  // Segurar: rajada em quem declara a tag
  aoComecarUso(p, item) {
    if (item?.hasTag(RAJADA)) atirando.set(p.id, item.typeId);
  },

  aoSoltarUso(p) {
    atirando.delete(p.id);
  },

  // rajada, zoom da mira e (a cada 10 ticks) contador de munição
  aCadaTick(p, id) {
    const arma = id ? FICHA.get(id) : undefined;
    const emRajada = atirando.get(p.id);
    if (emRajada) {
      if (id === emRajada && arma) atirar(p, arma);
      else atirando.delete(p.id);
    }
    atualizarMira(p, arma);
    const mostrar = system.currentTick % 10 === 0;
    if (mostrar && arma && !atirando.has(p.id)) mostrarMunicao(p, arma);
    else if (mostrar && !id) hud.esquecer(p.id);   // guardou a arma: próxima vez mostra de novo
  },

  aoSair(playerId) {
    atirando.delete(playerId);
    proximoTiro.delete(playerId);
    mira.esquecer(playerId);
  },
};
