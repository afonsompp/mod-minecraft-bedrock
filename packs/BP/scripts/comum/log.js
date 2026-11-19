/**
 * Aviso para o Content Log do jogo (Configurações > Criador > Content Log).
 *
 * O `console` existe no runtime do Bedrock mas não na tipagem de `@minecraft/server`, e o projeto
 * compila com `npm run check` — então o acesso passa por `globalThis`, que o tsc conhece. Sem isto,
 * usar `console` direto quebra a checagem; e sem log nenhum, um erro de carga do script é invisível.
 */
/** @param {string} msg */
export function aviso(msg) {
  try {
    /** @type {any} */ (globalThis).console?.warn(`[joao] ${msg}`);
  } catch {
    /* sem console: o anúncio de carga ainda mostra a falha ao jogador */
  }
}
