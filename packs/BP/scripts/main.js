// Armas do João — script de tiro
// Glock (semiautomática), AK-47 e M4A4 (automáticas: segure para atirar em rajada).
// v1.1: modelos 3D (resource pack), sons próprios, sem chamas no chão.
// v1.2: mira (agachar = mirar, com zoom e menos dispersão; a pose fica no resource pack).
import { EasingType, EntityDamageCause, GameMode, system, world } from "@minecraft/server";

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

/**
 * Categoria de cooldown ligada a cada tiro de verdade. A animação da arma (attachable) lê isso com
 * `query.cooldown_time_remaining('joao_tiro')` para saber que o tiro saiu: antes ela seguia o dedo na
 * tela, e sem munição a arma dava coice e soltava clarão à toa. Nenhum item declara
 * `minecraft:cooldown` com essa categoria de propósito — assim o jogo não bloqueia o uso da arma,
 * que pararia a rajada; o cooldown é só um recado do script para o Molang.
 */
const COOLDOWN = "joao_tiro";

// Entidades que o tiro deve atravessar
const IGNORAR = new Set(["minecraft:item", "minecraft:xp_orb", "minecraft:arrow", "minecraft:snowball"]);

/** @type {Map<string, number>} próximo tick em que cada jogador pode atirar */
const proximoTiro = new Map();
/** @type {Map<string, string>} jogadores segurando o gatilho de uma arma automática */
const atirando = new Map();
/** @type {Map<string, number>} FOV de mira aplicado em cada jogador (ausente = FOV normal) */
const zoomAtual = new Map();
/** @type {Map<string, string>} último texto mostrado na actionbar, para não reenviar sempre */
const ultimoHud = new Map();
let avisouCamera = false;

/** @param {import("@minecraft/server").Player} p */
function itemNaMao(p) {
  const inv = p.getComponent("minecraft:inventory");
  return inv?.container?.getItem(p.selectedSlotIndex);
}

/** @param {import("@minecraft/server").Player} p */
function ehCriativo(p) {
  return p.getGameMode() === GameMode.Creative;
}

/** @param {import("@minecraft/server").Player} p @param {string} id */
function contarMunicao(p, id) {
  const c = p.getComponent("minecraft:inventory")?.container;
  if (!c) return 0;
  let total = 0;
  for (let i = 0; i < c.size; i++) {
    const it = c.getItem(i);
    if (it?.typeId === id) total += it.amount;
  }
  return total;
}

/** @param {import("@minecraft/server").Player} p @param {string} id */
function gastarMunicao(p, id) {
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

/** @param {import("@minecraft/server").Vector3} v @param {number} s */
function espalhar(v, s) {
  const x = v.x + (Math.random() - 0.5) * 2 * s;
  const y = v.y + (Math.random() - 0.5) * 2 * s;
  const z = v.z + (Math.random() - 0.5) * 2 * s;
  const len = Math.hypot(x, y, z) || 1;
  return { x: x / len, y: y / len, z: z / len };
}

/** @param {import("@minecraft/server").Vector3} o @param {import("@minecraft/server").Vector3} d @param {number} t */
function ponto(o, d, t) {
  return { x: o.x + d.x * t, y: o.y + d.y * t, z: o.z + d.z * t };
}

/** @param {import("@minecraft/server").Dimension} dim @param {string} efeito @param {import("@minecraft/server").Vector3} loc */
function particula(dim, efeito, loc) {
  try {
    dim.spawnParticle(efeito, loc);
  } catch {
    // fora da área carregada — ignora
  }
}

/** @param {import("@minecraft/server").Player} p @param {string} id */
/** Mostra arma e munição na actionbar, mas só quando algo muda: trocar de arma, atirar, acabar a bala.
 * Assim o texto some sozinho em vez de ficar plantado no meio da tela — atrapalhava na mira da luneta.
 * Mirando, nunca mostra, e limpa o que estiver na tela.
 * @param {import("@minecraft/server").Player} p @param {string} id @param {boolean} [forcar] */
function mostrarMunicao(p, id, forcar) {
  const arma = ARMAS[id];
  if (p.isSneaking) {                      // na mira a tela fica limpa
    if (ultimoHud.get(p.id)) {
      p.onScreenDisplay.setActionBar("");
      ultimoHud.set(p.id, "");
    }
    return;
  }
  const qtd = ehCriativo(p) ? "∞" : String(contarMunicao(p, arma.municao));
  const texto = `§e${arma.nome} §7| §f${NOME_MUNICAO[arma.municao]}: §a${qtd}`;
  if (!forcar && texto === ultimoHud.get(p.id)) return;
  ultimoHud.set(p.id, texto);
  p.onScreenDisplay.setActionBar(texto);
}

/** @param {import("@minecraft/server").Player} p @param {string} id */
function atirar(p, id) {
  const arma = ARMAS[id];
  if (!arma) return;

  const agora = system.currentTick;
  if ((proximoTiro.get(p.id) ?? 0) > agora) return;
  proximoTiro.set(p.id, agora + arma.intervalo);

  if (!ehCriativo(p) && !gastarMunicao(p, arma.municao)) {
    p.playSound("joao.vazio");
    p.onScreenDisplay.setActionBar(`§cSem ${NOME_MUNICAO[arma.municao]}! Faça mais na bancada.`);
    atirando.delete(p.id);
    return;
  }
  // a partir daqui o tiro sai: avisa a animação da arma
  try {
    p.startItemCooldown(COOLDOWN, arma.intervalo);
  } catch {
    /* mundo descarregado ou jogador saindo: a animação só perde um quadro */
  }

  const dim = p.dimension;
  const origem = p.getHeadLocation();
  const dir = espalhar(p.getViewDirection(), arma.dispersao * (p.isSneaking ? arma.mira.dispersao : 1));

  // Até onde o tiro vai antes de bater num bloco
  let distancia = arma.alcance;
  const bloco = dim.getBlockFromRay(origem, dir, { maxDistance: arma.alcance });
  if (bloco) {
    const b = bloco.block.location;
    const f = bloco.faceLocation;
    const hit = { x: b.x + f.x, y: b.y + f.y, z: b.z + f.z };
    distancia = Math.hypot(hit.x - origem.x, hit.y - origem.y, hit.z - origem.z);
  }

  // Primeiro bicho/jogador no caminho
  const alvo = dim
    .getEntitiesFromRay(origem, dir, { maxDistance: distancia })
    .find((h) => h.entity.id !== p.id && !IGNORAR.has(h.entity.typeId) && h.distance <= distancia);

  if (alvo) {
    distancia = alvo.distance;
    try {
      alvo.entity.applyDamage(arma.dano, { cause: EntityDamageCause.entityAttack, damagingEntity: p });
      const emp = arma.empurrao ?? 0.4;
      alvo.entity.applyKnockback({ x: dir.x * emp, z: dir.z * emp }, 0.1 * emp / 0.4);
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
  for (let t = 3; t < distancia; t += 2) {
    particula(dim, "minecraft:basic_crit_particle", ponto(origem, dir, t));
  }

  mostrarMunicao(p, id, true);
}

/** Zoom da mira: agachado segurando arma = FOV da arma; senão, FOV normal. Só age quando o estado muda.
 * Usa a API da câmera (não precisa de cheats) e cai para o comando /camera se ela não existir.
 * @param {import("@minecraft/server").Player} p @param {string | undefined} id */
function atualizarMira(p, id) {
  const arma = id ? ARMAS[id] : undefined;
  const alvo = arma && p.isSneaking ? arma.mira.fov : undefined;
  if (alvo === zoomAtual.get(p.id)) return;
  if (alvo === undefined) zoomAtual.delete(p.id);
  else zoomAtual.set(p.id, alvo);

  // camera.setFov só existe em versões da API acima da 2.0.0; por isso o acesso é dinâmico
  const cam = /** @type {any} */ (p.camera);
  try {
    if (typeof cam.setFov === "function") {
      if (alvo === undefined) cam.clear();
      else cam.setFov({ fov: alvo, easeOptions: { easeTime: 0.2, easeType: EasingType.InOutSine } });
      return;
    }
  } catch {
    // cai para o comando
  }
  try {
    p.runCommand(alvo === undefined
      ? "camera @s fov_clear 0.2 in_out_sine"
      : `camera @s fov_set ${alvo} 0.2 in_out_sine`);
  } catch (e) {
    // sem zoom: a mira continua centralizada, só não amplia. Avisa na tela, uma vez por sessão.
    if (!avisouCamera) {
      p.onScreenDisplay.setActionBar("§eZoom da mira indisponível (ligue os Cheats no mundo).");
      /** @type {any} */ (globalThis).console?.warn(`[joao] zoom da mira indisponível: ${e}`);
    }
    avisouCamera = true;
  }
}

// Toque/clique: um tiro (vale para as três armas)
world.afterEvents.itemUse.subscribe(({ source, itemStack }) => {
  if (ARMAS[itemStack.typeId]) atirar(source, itemStack.typeId);
});

// Segurar: rajada nas automáticas
world.afterEvents.itemStartUse.subscribe(({ source, itemStack }) => {
  if (itemStack && ARMAS[itemStack.typeId]?.automatica) atirando.set(source.id, itemStack.typeId);
});
world.afterEvents.itemStopUse.subscribe(({ source }) => atirando.delete(source.id));
world.afterEvents.itemReleaseUse.subscribe(({ source }) => atirando.delete(source.id));
world.afterEvents.playerLeave.subscribe(({ playerId }) => {
  atirando.delete(playerId);
  proximoTiro.delete(playerId);
  zoomAtual.delete(playerId);
  ultimoHud.delete(playerId);
});

// Um único laço por tick: rajada, zoom da mira e (a cada 10 ticks) contador de munição
system.runInterval(() => {
  const mostrar = system.currentTick % 10 === 0;
  for (const p of world.getAllPlayers()) {
    const id = itemNaMao(p)?.typeId;
    const arma = atirando.get(p.id);
    if (arma) {
      if (id === arma) atirar(p, arma);
      else atirando.delete(p.id);
    }
    atualizarMira(p, id);
    if (mostrar && id && ARMAS[id] && !atirando.has(p.id)) mostrarMunicao(p, id);
    else if (mostrar && !id) ultimoHud.delete(p.id);     // guardou a arma: próxima vez mostra de novo
  }
}, 1);
