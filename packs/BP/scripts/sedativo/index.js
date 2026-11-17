/**
 * Besta de dardos tranquilizantes, e o sono que ela causa.
 *
 * Diferente das armas de fogo em duas coisas que importam:
 *  - o dardo é uma ENTIDADE que voa (`joao:dardo_voo`), não um raycast instantâneo. Quem avisa que
 *    ele acertou é o evento `projectileHitEntity` do jogo, então nada aqui fica seguindo o dardo;
 *  - o acerto não vale pelo dano (é 1, simbólico) e sim pela DOSE. Bicho grande precisa de mais de
 *    um dardo; a conta sai da vida máxima dele, sem tabela por mob — assim um dinossauro de 200 de
 *    vida já entra certo no dia em que existir.
 */
import { system, world } from "@minecraft/server";
import { COOLDOWN_TIRO, DORMINDO, EVENTO_ACORDAR, EVENTO_DORMIR, SEDAVEL } from "../comum/tags.js";
import { contar, ehCriativo, gastar } from "../comum/inventario.js";
import { particula } from "../comum/efeitos.js";
import { espalhar } from "../comum/raycast.js";
import * as hud from "../comum/hud.js";
import * as mira from "../comum/mira.js";

const BESTA = "joao:besta";
const DARDO = "joao:dardo";
const PROJETIL = "joao:dardo_voo";

const INTERVALO = 15;        // ticks entre tiros; tem de bater com PLACE["besta"]["intervalo"]
const FOV_MIRA = 40;         // luneta de média distância; tem de bater com PLACE["besta"]["fov_mira"]
const VELOCIDADE = 2.4;      // igual ao "power" de packs/BP/entities/dardo_voo.json
const DISPERSAO = 0.012;     // besta é precisa; mirando, menos ainda
const DISPERSAO_MIRA = 0.25;
const VALIDADE = 20 * 20;    // ticks que uma dose isolada dura antes de o bicho metabolizar
const SONO_BASE = 30;        // segundos de sono, mais 10 por dose aplicada

/** @type {Map<string, number>} próximo tick em que cada jogador pode atirar */
const proximoTiro = new Map();
/** @type {Map<string, { doses: number, ate: number }>} doses em cada bicho, por id */
const doses = new Map();
/** @type {Map<string, number>} tick em que cada bicho adormecido acorda */
const acordaEm = new Map();

/** Quantos dardos esse bicho aguenta antes de apagar: um a cada 10 de vida, de 1 a 5.
 * @param {import("@minecraft/server").Entity} e */
function limiar(e) {
  const vida = e.getComponent("minecraft:health")?.effectiveMax ?? 10;
  return Math.max(1, Math.min(5, Math.ceil(vida / 10)));
}

/** @param {import("@minecraft/server").Entity} e */
function nome(e) {
  return e.nameTag || e.typeId.replace(/^minecraft:/, "").replace(/_/g, " ");
}

/** @param {import("@minecraft/server").Player} p */
function atirar(p) {
  const agora = system.currentTick;
  if ((proximoTiro.get(p.id) ?? 0) > agora) return;
  proximoTiro.set(p.id, agora + INTERVALO);

  if (!ehCriativo(p) && !gastar(p, DARDO)) {
    p.playSound("joao.vazio");
    p.onScreenDisplay.setActionBar("§cSem Dardo Tranquilizante! Faça mais na bancada.");
    return;
  }
  // a partir daqui o dardo sai: o cooldown avisa a animação (a corda dispara e volta no ritmo dele)
  try {
    p.startItemCooldown(COOLDOWN_TIRO, INTERVALO);
  } catch {
    /* mundo descarregado ou jogador saindo: a animação só perde um quadro */
  }

  const dim = p.dimension;
  const olho = p.getHeadLocation();
  const dir = espalhar(p.getViewDirection(), DISPERSAO * (p.isSneaking ? DISPERSAO_MIRA : 1));
  // nasce um pouco à frente do olho, senão o dardo acerta o próprio jogador ao sair
  const saida = { x: olho.x + dir.x * 0.8, y: olho.y + dir.y * 0.8, z: olho.z + dir.z * 0.8 };
  try {
    const d = dim.spawnEntity(PROJETIL, saida);
    const proj = d.getComponent("minecraft:projectile");
    if (proj) {
      proj.owner = p;      // sem dono, o acerto não é creditado a quem atirou
      proj.shoot({ x: dir.x * VELOCIDADE, y: dir.y * VELOCIDADE, z: dir.z * VELOCIDADE });
    }
  } catch (e) {
    /** @type {any} */ (globalThis).console?.warn(`[joao] dardo não saiu: ${e}`);
  }

  dim.playSound("joao.besta.tiro", olho, { volume: 1, pitch: 0.97 + Math.random() * 0.06 });
  // a meio do ciclo, o som da manivela puxando a corda de volta
  system.runTimeout(() => {
    try {
      p.playSound("joao.besta.recarga", { volume: 0.5 });
    } catch {
      /* jogador saiu */
    }
  }, 5);
  mostrarDardos(p, true);
}

/** @param {import("@minecraft/server").Player} p @param {boolean} [forcar] */
function mostrarDardos(p, forcar) {
  if (p.isSneaking) {              // na mira a tela fica limpa
    hud.limpar(p);
    return;
  }
  const qtd = ehCriativo(p) ? "∞" : String(contar(p, DARDO));
  hud.barra(p, `§eBesta Tranquilizante §7| §fDardos: §a${qtd}`, forcar);
}

/** Um dardo acertou: soma a dose e, se encheu, apaga o bicho.
 * @param {import("@minecraft/server").Entity} alvo
 * @param {import("@minecraft/server").Entity | undefined} atirador */
function aplicarDose(alvo, atirador) {
  const agora = system.currentTick;
  const antes = doses.get(alvo.id);
  const n = (antes && antes.ate > agora ? antes.doses : 0) + 1;   // dose antiga já metabolizada: recomeça
  const falta = limiar(alvo);
  doses.set(alvo.id, { doses: n, ate: agora + VALIDADE });

  const loc = alvo.getHeadLocation();
  particula(alvo.dimension, "minecraft:villager_happy", loc);
  const dono = /** @type {import("@minecraft/server").Player | undefined} */ (
    atirador?.typeId === "minecraft:player" ? atirador : undefined);

  if (n < falta) {
    dono?.onScreenDisplay.setActionBar(`§b${nome(alvo)} §7— dose §f${n}§7 de §f${falta}`);
    return;
  }
  dormir(alvo, n);
  dono?.onScreenDisplay.setActionBar(`§b${nome(alvo)} §7— §adormindo`);
}

/** @param {import("@minecraft/server").Entity} alvo @param {number} n doses aplicadas */
function dormir(alvo, n) {
  doses.delete(alvo.id);
  const segundos = SONO_BASE + 10 * n;
  acordaEm.set(alvo.id, system.currentTick + segundos * 20);
  try {
    alvo.addTag(DORMINDO);
    if (alvo.matches({ families: [SEDAVEL] })) {
      // bicho nosso (dinossauro): o JSON dele deita, cala e desliga os comportamentos
      alvo.triggerEvent(EVENTO_DORMIR);
    } else {
      // bicho do jogo: não existe pose de dormir para ele, e nenhum script inventa uma.
      // Lentidão e fraqueza no máximo é o mais perto que dá: ele para onde está e não machuca.
      alvo.addEffect("slowness", segundos * 20, { amplifier: 9, showParticles: false });
      alvo.addEffect("weakness", segundos * 20, { amplifier: 9, showParticles: false });
    }
    alvo.dimension.playSound("joao.dardo.acerto", alvo.location, { pitch: 0.8, volume: 0.8 });
  } catch {
    /* entidade saiu da área carregada entre o acerto e isto */
  }
}

/** @param {import("@minecraft/server").Entity} e */
function acordar(e) {
  acordaEm.delete(e.id);
  try {
    e.removeTag(DORMINDO);
    if (e.matches({ families: [SEDAVEL] })) {
      e.triggerEvent(EVENTO_ACORDAR);
    } else {
      e.removeEffect("slowness");
      e.removeEffect("weakness");
    }
    particula(e.dimension, "minecraft:villager_happy", e.getHeadLocation());
  } catch {
    /* já morreu ou descarregou */
  }
}

/** @type {import("../comum/dominio.js").Dominio} */
export const dominio = {
  nome: "sedativo",

  iniciar() {
    world.afterEvents.projectileHitEntity.subscribe((ev) => {
      if (ev.projectile?.typeId !== PROJETIL) return;
      const alvo = ev.getEntityHit()?.entity;
      if (alvo && alvo.id !== ev.source?.id) aplicarDose(alvo, ev.source);
    });
    // bicho morreu ou descarregou: esquece as doses dele, senão os mapas só crescem
    world.afterEvents.entityRemove.subscribe(({ removedEntityId }) => {
      doses.delete(removedEntityId);
      acordaEm.delete(removedEntityId);
    });
    world.afterEvents.projectileHitBlock.subscribe((ev) => {
      if (ev.projectile?.typeId !== PROJETIL) return;
      particula(ev.dimension, "minecraft:basic_smoke_particle", ev.location);
    });

    // Um laço só, de segundo em segundo: acorda quem já dormiu o bastante e solta o "zZz".
    // Varre apenas quem está marcado, e só nas dimensões com jogador.
    system.runInterval(() => {
      const agora = system.currentTick;
      const vistas = new Set();
      for (const p of world.getAllPlayers()) {
        const dim = p.dimension;
        if (vistas.has(dim.id)) continue;
        vistas.add(dim.id);
        for (const e of dim.getEntities({ tags: [DORMINDO] })) {
          const ate = acordaEm.get(e.id);
          // sem registro = o mundo foi recarregado desde o dardo. Acorda, em vez de dormir para sempre.
          if (ate === undefined || ate <= agora) acordar(e);
          else particula(dim, "joao:sono", e.getHeadLocation());
        }
      }
    }, 20);
  },

  aoUsar(p, item) {
    if (item.typeId === BESTA) atirar(p);
  },

  aCadaTick(p, id) {
    if (id !== BESTA) {
      mira.zoom(p, undefined, "sedativo");     // guardou a besta: devolve o FOV normal
      return;
    }
    mira.zoom(p, p.isSneaking ? FOV_MIRA : undefined, "sedativo");
    if (system.currentTick % 10 === 0) mostrarDardos(p);
  },

  aoSair(playerId) {
    proximoTiro.delete(playerId);
    mira.esquecer(playerId);
  },
};
