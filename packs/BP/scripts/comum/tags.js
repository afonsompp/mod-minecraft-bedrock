/**
 * Nomes compartilhados entre o script, o Molang do resource pack e os JSONs do add-on.
 *
 * Fonte única de propósito: no Bedrock, um nome que não casa não dá erro — o efeito simplesmente não
 * acontece, ou o item some da tela. Mudar um nome aqui obriga a mudar o outro lado junto.
 */

/**
 * Categoria de cooldown ligada a cada tiro de verdade. A animação da arma (attachable) lê isso com
 * `query.cooldown_time_remaining('joao_tiro')` para saber que o tiro saiu: antes ela seguia o dedo na
 * tela, e sem munição a arma dava coice e soltava clarão à toa. Nenhum item declara
 * `minecraft:cooldown` com essa categoria de propósito — assim o jogo não bloqueia o uso da arma,
 * que pararia a rajada; o cooldown é só um recado do script para o Molang.
 */
export const COOLDOWN_TIRO = "joao_tiro";

/**
 * Tags que os itens declaram em `minecraft:tags`, no JSON deles.
 *
 * ARMA_FOGO é também o nome do **componente customizado** que carrega os números da arma (dano,
 * alcance, cadência, munição, som). O nome registrado no script e o nome no JSON do item têm de ser
 * idênticos: se não forem, o Bedrock não avisa — o item simplesmente some do inventário.
 */
export const ARMA_FOGO = "joao:arma_fogo";
export const RAJADA = "joao:disparo_rajada";
export const SEMI = "joao:disparo_semi";
export const MUNICAO = "joao:municao";

/** Itens e blocos do laboratório. O nome do componente de bloco tem de bater com o JSON, como nas armas. */
export const FOSSIL = "joao:fossil";
export const OVO_SINTETICO = "joao:ovo_sintetico";
export const DNA = "joao:dna";
export const MAQUINA = "joao:maquina";
/** Ovo fecundado: usar no chão choca o bicho. */
export const OVO_DINO = "joao:ovo_dino";
/** Estado de bloco das máquinas: 0 parada · 1 trabalhando · 2 pronta (gerado por blocos.py). */
export const ESTADO_FASE = "joao:fase";

/** Entidades que um tiro atravessa: não são alvo. */
export const ATRAVESSA = new Set([
  "minecraft:item",
  "minecraft:xp_orb",
  "minecraft:arrow",
  "minecraft:snowball",
]);

/**
 * Família que um bicho declara (no JSON dele, em `minecraft:type_family`) para dormir de verdade
 * com o dardo: o script dispara nele os eventos abaixo em vez de só congelá-lo com efeitos.
 * É o gancho dos dinossauros — nenhuma entidade do modpack a declara ainda.
 */
export const SEDAVEL = "joao:sedavel";
export const EVENTO_DORMIR = "joao:dormir";
export const EVENTO_ACORDAR = "joao:acordar";

/** Marca de runtime em quem está dormindo. Serve para o laço achar quem acordar. */
export const DORMINDO = "joao:dormindo";
