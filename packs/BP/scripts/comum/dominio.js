/**
 * Contrato entre o `main.js` (roteador) e cada domínio do modpack (armas, sedativo, e o que vier).
 *
 * O `main.js` assina os eventos de `@minecraft/server` uma vez só e repassa a quem declarar o gancho.
 * Domínios não importam uns aos outros: o que é compartilhado mora em `comum/`.
 *
 * @typedef {import("@minecraft/server").Player} Jogador
 * @typedef {import("@minecraft/server").ItemStack} Item
 *
 * @typedef {Object} Dominio
 * @property {string} nome
 * @property {() => void} [iniciar]            laços e assinaturas próprias (no máximo um runInterval)
 * @property {(ev: import("@minecraft/server").StartupEvent) => void} [componentes]
 *            registra componentes customizados de item e de bloco. Só pode acontecer no
 *            `system.beforeEvents.startup`, e o nome tem de bater com o do JSON (ver comum/tags.js)
 * @property {(p: Jogador, item: Item) => void} [aoUsar]                toque/clique com o item na mão
 * @property {(p: Jogador, item: Item, bloco: import("@minecraft/server").Block) => void} [aoUsarEmBloco]
 *            o mesmo toque, mas mirando um bloco — que **não** passa por `aoUsar`. Um toque pode
 *            chegar pelos dois ganchos no mesmo tick: quem age nos dois precisa de guarda
 * @property {(p: Jogador, item: Item | undefined) => void} [aoComecarUso]  começou a segurar
 * @property {(p: Jogador) => void} [aoSoltarUso]                       soltou
 * @property {(p: Jogador, id: string | undefined) => void} [aCadaTick] uma vez por tick, por jogador
 * @property {(playerId: string) => void} [aoSair]                      saiu do mundo
 */

export {};
