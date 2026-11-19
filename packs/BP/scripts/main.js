// Modpack Expansível do João — ponto de entrada.
//
// Este arquivo não tem lógica de jogo: ele assina os eventos de @minecraft/server uma vez só e repassa
// para os domínios (armas, e o que vier: sedativo, dinossauros, veículos). Domínio novo = uma linha em
// DOMINIOS. O contrato está em comum/dominio.js.
//
// **Por que cada assinatura tem try/catch.** Um evento que não existe no runtime do aparelho lança na
// hora da carga, e aí o módulo inteiro morre — não é só aquele recurso que para, é o add-on todo,
// armas inclusive, sem mensagem nenhuma. Isolando cada assinatura, o que falha fica sendo só ela, e o
// nome dela aparece no anúncio de carga.
import { system, world } from "@minecraft/server";
import { itemNaMao } from "./comum/inventario.js";
import * as hud from "./comum/hud.js";
import { VERSAO } from "./comum/versao.js";
import { aviso } from "./comum/log.js";
import { dominio as armas } from "./armas/index.js";
import { dominio as laboratorio } from "./laboratorio/index.js";
import { dominio as dinossauros } from "./dinossauros/index.js";
import { dominio as paleontologia } from "./paleontologia/index.js";
import { dominio as sedativo } from "./sedativo/index.js";

/** @type {import("./comum/dominio.js").Dominio[]} */
const DOMINIOS = [armas, sedativo, laboratorio, paleontologia, dinossauros];

/** Eventos que não puderam ser assinados neste aparelho. Entram no anúncio de carga. */
/** @type {string[]} */
const falhas = [];

/**
 * Assina um evento isolando a falha.
 * @param {string} nome
 * @param {{ subscribe: (cb: any) => unknown } | undefined} sinal
 * @param {(ev: any) => void} cb
 */
function assinar(nome, sinal, cb) {
  try {
    if (!sinal) throw new Error("evento não existe neste runtime");
    sinal.subscribe(cb);
  } catch (e) {
    falhas.push(nome);
    aviso(`não consegui assinar ${nome}: ${e}`);
  }
}

// Componentes customizados só podem ser registrados aqui, e antes de qualquer item ser carregado.
system.beforeEvents.startup.subscribe((ev) => {
  for (const d of DOMINIOS) {
    try {
      d.componentes?.(ev);
    } catch (e) {
      falhas.push(`componentes:${d.nome}`);
      aviso(`componentes de ${d.nome}: ${e}`);
    }
  }
});

for (const d of DOMINIOS) {
  try {
    d.iniciar?.();
  } catch (e) {
    falhas.push(`iniciar:${d.nome}`);
    aviso(`iniciar de ${d.nome}: ${e}`);
  }
}

assinar("itemUse", world.afterEvents.itemUse, ({ source, itemStack }) => {
  for (const d of DOMINIOS) d.aoUsar?.(source, itemStack);
});

// Tocar um **bloco** com o item na mão não passa por `itemUse`, e `itemUseOn` deixou de existir na
// API 2.0 — virou este evento. Sem ele, item que se usa mirando o chão não chegaria a domínio nenhum.
assinar("playerInteractWithBlock", world.afterEvents.playerInteractWithBlock, (ev) => {
  if (!ev.isFirstEvent) return; // segurar o toque repete o evento a cada tick
  const item = ev.beforeItemStack ?? ev.itemStack;
  if (!item) return;
  for (const d of DOMINIOS) d.aoUsarEmBloco?.(ev.player, item, ev.block);
});

assinar("itemStartUse", world.afterEvents.itemStartUse, ({ source, itemStack }) => {
  for (const d of DOMINIOS) d.aoComecarUso?.(source, itemStack);
});
assinar("itemStopUse", world.afterEvents.itemStopUse, ({ source }) => {
  for (const d of DOMINIOS) d.aoSoltarUso?.(source);
});
assinar("itemReleaseUse", world.afterEvents.itemReleaseUse, ({ source }) => {
  for (const d of DOMINIOS) d.aoSoltarUso?.(source);
});
assinar("playerLeave", world.afterEvents.playerLeave, ({ playerId }) => {
  for (const d of DOMINIOS) d.aoSair?.(playerId);
  hud.esquecer(playerId);
});

// O anúncio de carga. Serve para responder, de dentro do jogo, a pergunta que nenhum print responde:
// o script está rodando, e é o desta versão? O Minecraft guarda os packs antigos, então um pack velho
// carregado é indistinguível de um recurso quebrado.
assinar("playerSpawn", world.afterEvents.playerSpawn, ({ player, initialSpawn }) => {
  if (!initialSpawn) return;
  system.runTimeout(() => {
    try {
      const aviso = falhas.length ? ` §c(falhou: ${falhas.join(", ")})` : "";
      player.sendMessage(`§7Modpack do João §fv${VERSAO} §7ativo — ${DOMINIOS.length} domínios${aviso}`);
    } catch { /* jogador saiu antes */ }
  }, 40);
});

// Um único laço por tick para todos os domínios: cada um recebe o jogador e o que ele tem na mão.
system.runInterval(() => {
  for (const p of world.getAllPlayers()) {
    const id = itemNaMao(p)?.typeId;
    for (const d of DOMINIOS) d.aCadaTick?.(p, id);
  }
}, 1);
