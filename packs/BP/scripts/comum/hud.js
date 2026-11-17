/**
 * Actionbar. O texto só é reenviado quando muda, senão fica plantado no meio da tela — atrapalhava
 * na mira da luneta.
 */

/** @type {Map<string, string>} último texto mostrado a cada jogador */
const ultimo = new Map();

/** @param {import("@minecraft/server").Player} p @param {string} texto @param {boolean} [forcar] */
export function barra(p, texto, forcar) {
  if (!forcar && texto === ultimo.get(p.id)) return;
  ultimo.set(p.id, texto);
  p.onScreenDisplay.setActionBar(texto);
}

/** Limpa a barra, se havia algo escrito. @param {import("@minecraft/server").Player} p */
export function limpar(p) {
  if (ultimo.get(p.id)) barra(p, "");
}

/** Esquece o que estava escrito, para a próxima mensagem igual aparecer de novo. @param {string} id */
export function esquecer(id) {
  ultimo.delete(id);
}
