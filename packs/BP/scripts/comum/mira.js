/**
 * Zoom da mira (agachar). Fica em comum/ porque mais de um domínio mira: a arma de fogo e a besta.
 *
 * Cada domínio pede o zoom em nome próprio. Sem isso os dois brigavam a cada tick — com a besta na
 * mão, o domínio das armas mandava limpar o zoom e o do sedativo mandava aplicá-lo, e saía um
 * comando por tick. Quem não pediu o zoom que está valendo não pode tirá-lo.
 *
 * O FOV só vale entre 30 e 110 — fora disso o jogo recusa em silêncio — e o `/camera fov_set` exige
 * Cheats ligados no mundo. Sem o zoom, a mira continua centralizada; só não amplia.
 */
import { EasingType } from "@minecraft/server";

/** @type {Map<string, { fov: number, dono: string }>} zoom valendo em cada jogador */
const atual = new Map();
let avisou = false;

/** @param {import("@minecraft/server").Player} p @param {number | undefined} fov */
function aplicar(p, fov) {
  // camera.setFov só existe em versões da API acima da 2.0.0; por isso o acesso é dinâmico
  const cam = /** @type {any} */ (p.camera);
  try {
    if (typeof cam.setFov === "function") {
      if (fov === undefined) cam.clear();
      else cam.setFov({ fov, easeOptions: { easeTime: 0.2, easeType: EasingType.InOutSine } });
      return;
    }
  } catch {
    // cai para o comando
  }
  try {
    p.runCommand(fov === undefined
      ? "camera @s fov_clear 0.2 in_out_sine"
      : `camera @s fov_set ${fov} 0.2 in_out_sine`);
  } catch (e) {
    // sem zoom: a mira continua centralizada, só não amplia. Avisa na tela, uma vez por sessão.
    if (!avisou) {
      p.onScreenDisplay.setActionBar("§eZoom da mira indisponível (ligue os Cheats no mundo).");
      /** @type {any} */ (globalThis).console?.warn(`[joao] zoom da mira indisponível: ${e}`);
    }
    avisou = true;
  }
}

/** @param {import("@minecraft/server").Player} p @param {number | undefined} fov
 *  @param {string} dono nome do domínio que está pedindo */
export function zoom(p, fov, dono) {
  const a = atual.get(p.id);
  if (fov === undefined) {
    if (!a || a.dono !== dono) return;        // o zoom que está valendo é de outro domínio
    atual.delete(p.id);
    aplicar(p, undefined);
    return;
  }
  if (a && a.fov === fov && a.dono === dono) return;
  atual.set(p.id, { fov, dono });
  aplicar(p, fov);
}

/** @param {string} playerId */
export function esquecer(playerId) {
  atual.delete(playerId);
}
