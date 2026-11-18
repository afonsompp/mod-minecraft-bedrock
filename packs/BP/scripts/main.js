// Modpack Expansível do João — ponto de entrada.
//
// Este arquivo não tem lógica de jogo: ele assina os eventos de @minecraft/server uma vez só e repassa
// para os domínios (armas, e o que vier: sedativo, dinossauros, veículos). Domínio novo = uma linha em
// DOMINIOS. O contrato está em comum/dominio.js.
import { system, world } from "@minecraft/server";
import { itemNaMao } from "./comum/inventario.js";
import * as hud from "./comum/hud.js";
import { dominio as armas } from "./armas/index.js";
import { dominio as laboratorio } from "./laboratorio/index.js";
import { dominio as paleontologia } from "./paleontologia/index.js";
import { dominio as sedativo } from "./sedativo/index.js";

/** @type {import("./comum/dominio.js").Dominio[]} */
const DOMINIOS = [armas, sedativo, laboratorio, paleontologia];

// Componentes customizados só podem ser registrados aqui, e antes de qualquer item ser carregado.
system.beforeEvents.startup.subscribe((ev) => {
  for (const d of DOMINIOS) d.componentes?.(ev);
});

for (const d of DOMINIOS) d.iniciar?.();

world.afterEvents.itemUse.subscribe(({ source, itemStack }) => {
  for (const d of DOMINIOS) d.aoUsar?.(source, itemStack);
});

world.afterEvents.itemStartUse.subscribe(({ source, itemStack }) => {
  for (const d of DOMINIOS) d.aoComecarUso?.(source, itemStack);
});
world.afterEvents.itemStopUse.subscribe(({ source }) => {
  for (const d of DOMINIOS) d.aoSoltarUso?.(source);
});
world.afterEvents.itemReleaseUse.subscribe(({ source }) => {
  for (const d of DOMINIOS) d.aoSoltarUso?.(source);
});
world.afterEvents.playerLeave.subscribe(({ playerId }) => {
  for (const d of DOMINIOS) d.aoSair?.(playerId);
  hud.esquecer(playerId);
});

// Um único laço por tick para todos os domínios: cada um recebe o jogador e o que ele tem na mão.
system.runInterval(() => {
  for (const p of world.getAllPlayers()) {
    const id = itemNaMao(p)?.typeId;
    for (const d of DOMINIOS) d.aCadaTick?.(p, id);
  }
}, 1);
