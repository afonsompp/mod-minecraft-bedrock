# Arma nova — passo a passo e valores de referência

Fluxo atual (antes da migração para `joao:arma_fogo` + tags). Detalhes técnicos de pose, mira e textura em `docs/modelos-e-pose.md`.

## O que já vem pronto (não refazer)

- **Câmera do jogo:** `CALIB` (em pé) e `AGACHADO` (deslocamento ao agachar) valem para qualquer arma, porque são do jogo, não da arma. As duas foram confirmadas com prints do celular na v1.3.1.
- **Sistema de mira:** basta a `visada` do modelo. `pose_mira()` centraliza a arma, `caminho_mira()` faz o trajeto quadril → mira, e o puxão ao atirar em pé usa `atirando`.
- **Comportamento em 1ª pessoa:**
  - compensação dos balanços vanilla (respiração e caminhada);
  - recuo só para trás;
  - animação de tiro por tipo: `pistola` = 1 ciclo por toque, `fuzil` = cicla enquanto segura.
- **Texturas:** a pintura 3D (oclusão, desgaste em quina exposta, veio contínuo) funciona para qualquer modelo que use os materiais de `geometria.py`. Material novo = um ramo em `base_3d()` (e em `detalhes_2d()` se tiver padrão usinado).

## Onde mexer

A lista de armas está repetida em vários lugares, então siga a lista inteira:

1. `tools/modelos.py`: função do modelo (`def nome()`) e entrada em `ARMAS` com o tipo (`"pistola"` ou `"fuzil"`). Modele **peça por peça**, sem teto de cubos: a M4A4 da v1.4 (~150 cubos) é a referência de nível. Ajudantes:
   - `dentes_z()`: trilhos Picatinny;
   - `chain()` + `nervuras_carregador()` + `base_carregador()`: carregador curvo completo;
   - dois cubos cruzados: peças "redondas" (tubos);
   - dois cubos sobrepostos girando no mesmo pivô com ângulos diferentes: peça que afina, como a coronha da AK.

   Peças finas e salientes (janelas, chapas) precisam de pelo menos 0,1 de espessura, senão cintilam (z-fighting). O `info` precisa de:
   - `grip`: ponto do punho;
   - `muzzle`: boca do cano;
   - `visada`: (ponto de trás, ponto da frente) da linha de mira (veja as regras abaixo);
2. `tools/gerar.py`:
   - `PLACE[nome]`: `grip`, `yaw`, `pitch`, `roll`, `intervalo`, `olho` e `atirando` (valores na tabela abaixo);
   - `NOMES`;
   - a tupla do laço em `main()`.
3. `tools/ajuste.py`: entrada no laço, se for usar o ajuste automático de posição no quadril.
4. `tools/sons.py`: 3 variações de tiro. Também `packs/RP/sounds/sound_definitions.json` (`joao.<nome>.tiro`).
5. `tools/pose.py`: o item entra na condição `joao_mira_fuzil` ou `joao_mira_pistola` (3ª pessoa com `POSE_RP`).
6. `tools/site_joao.py`: `ARMAS` (suporte de armas do site).
7. `packs/BP/items/<nome>.json`: copie de uma arma do mesmo tipo. Mantenha `minecraft:use_modifiers` (sem isso, "segurar para atirar" não funciona no celular). Faça também `packs/BP/recipes/<nome>.json`.
8. `packs/BP/scripts/main.js`: entrada em `ARMAS` com `dano`, `alcance`, `intervalo` (igual ao do `PLACE`), `automatica`, `municao`, `som`, `dispersao` e `mira: { fov, dispersao }`.
9. `packs/RP/textures/item_texture.json`: `joao_<nome>` → `textures/items/<nome>` (o ícone é gerado).

## Valores de referência

| Parâmetro | Fuzil com alça no meio (AK) | Fuzil com alça atrás (M4) | Pistola (Glock) | Sniper (AWP) |
|---|---|---|---|---|
| `olho` (un. de câmera, 1/16 bloco) | 7,5 | 3,5 | 2,5 | 2,0 |
| `atirando` (fração do caminho até a mira) | 0,45 | 0,45 | 0,3 | 0,3 |
| `intervalo` (ticks entre tiros) | 3 | 3 | 5 | 25 |
| `mira.fov` / `mira.dispersao` | 52 / 0,3 | 52 / 0,3 | 58 / 0,4 | 18 / 0,04 |
| `yaw` / `pitch` / `roll` no quadril | 5,7 / 1 / −4 | 5,7 / 1 / −4 | 5,8 / 1 / −3 | 5,7 / 1 / −4 |

- `olho` é a distância do olho ao ponto de trás da visada na mira. A alça no meio da arma pede olho mais longe, senão o olho entra na caixa. Alça traseira e pistola ficam perto; com olho grande, a pistola parece pequena e distante (v1.3.1).
- `atirando` alto na pistola faz ela tapar a tela (v1.2.1).
- Luneta: `visada` = centro da ocular → centro da objetiva; `olho` = alívio de olho; `mira.fov` bem menor (~20).

## Nível de detalhe e cores (padrão da v1.4)

- Referência: add-ons de arma do mercado com 150 a 300 cubos por arma. O realismo vem da **geometria**: cada peça real que se vê de 1 m vira cubo (reténs, pinos, seletor, dobradiças, anéis, orelhas, dentes de trilho). Textura limpa, sem ruído fino. A luz é pintada automaticamente (degradê, reflexo, quinas) pelo `acabamento()`.
- Medidas reais: defina a escala (cm por unidade) a partir do comprimento total e confira as proporções principais (cano, caixa, carregador, coronha). A M4A4 usa ~1,3 cm/un.
- Cores: use os materiais existentes. Eles estão em cinzas médios de propósito, porque preto de verdade vira silhueta no jogo. Diferencie peças por material (ex.: `aco` na massa e nos pinos, `anodizado` no receptor, `carregador_m4` mais claro).

## Tipos de arma

`modelos.ARMAS[id] = (função, tipo)`. O tipo decide a animação de disparo e as mãos:

| Tipo | Disparo | Mãos |
|---|---|---|
| `"fuzil"` | cicla enquanto o dedo está na tela (rajada) | duas mãos, a esquerda no guarda-mão |
| `"pistola"` | 1 ciclo por toque | duas mãos juntas na empunhadura |
| `"sniper"` | 1 ciclo por toque, com recuo bem maior | igual ao fuzil |

## Arma com luneta

- Ponha `luneta=True` no `info` e a `visada` no **eixo óptico** (centro da ocular → centro da objetiva).
- Na mira completa (`v.ads` > 0,93), o gerador faz a **arma sumir** e mostra o osso `luneta`: um painel preto com furo circular e retículo em cruz, como nos FPS. Sem isso, o tubo da luneta taparia a visão.
- O painel é **geometria** (faixas pretas), não textura: em textura precisaria de ~512x256 e estourava o atlas.
- Ele é dimensionado para `FOV_MIRA` (`gerar.py`), que tem de ser **igual** ao `mira.fov` do `main.js`. Se o zoom não funcionar no aparelho, o painel aparece pequeno no meio da tela.
- A luneta em si pode ser modelada sólida e realista: na mira ela não aparece.

## Regras de desenho da mira (lições das versões anteriores)

- **A linha de mira precisa passar bem acima de tudo que fica entre o olho e a alça.** Na v1.3.1, a visada da AK passava só 1,25 un. de modelo acima da tampa da caixa. Na mira, a tampa ficava colada embaixo do entalhe e escondia a alça. A correção foi subir a alça e a massa (visada em y 10,25). Confira em `fp_mira_<nome>.png`: o entalhe e a massa precisam estar visíveis e destacados do que está atrás.
- **Alça perto do olho (orifício/peep, como na M4) tapa a visão na mira.** Marque os cubos dela com `osso("alca", ...)` e defina `info["alca_pivo"]` no topo do trilho: ela se recolhe ao mirar. Alça no meio da arma (AK) ou de pistola não precisa.
- A alça tem que ser um **entalhe de verdade** (U ou V, com orelhas) ou um orifício (peep), e a massa precisa aparecer **dentro** dele com folga dos dois lados. Dê zoom no centro da prévia para conferir.
- O ponto de trás da `visada` é o **topo** do entalhe (o nível das orelhas), e o da frente é a ponta da massa, na mesma altura. `pose_mira()` compensa a inclinação entre a visada e o cano no pitch.
- Pistola vista de trás vira uma coluna estreita no meio da tela. Se parecer "torre solta", a solução é mostrar as mãos na empunhadura, não baixar a arma: o topo precisa estar no centro, que é onde o tiro vai.

## Validação

1. `python tools/build.py --gerar` e abra:
   - `fp_<nome>.png`: quadril;
   - `fp_transicao_<nome>.png`: quadril, atirando em pé e mira;
   - `fp_mira_<nome>.png`: a cruz cai na ponta da massa, dentro do entalhe;
   - `detalhe_<nome>.png`: 3/4 grande; confira se cada peça pequena se lê e se a paleta não virou silhueta;
   - `lado_<nome>.png`: proporções, e vira o ícone;
   - `tp_<nome>.png`: 3ª pessoa.
2. Desde a v1.3.2, o renderizador de prévias é confiável de perto: ordena por pedaço de face e mostra a face certa. Só não tem a luz do jogo.
3. `--versao`, `--deploy` e `--publicar`. Peça ao Afonso prints **mirando agachado**, **em pé** e **atirando em pé**.
4. Se o print mirando não bater com `fp_mira_<nome>.png`, meça antes de mexer no `PLACE`. Ajuste a silhueta do print contra o modelo na pose `1.0000`, variando só a translação da câmera (ver "Câmera agachada" em `docs/modelos-e-pose.md`). Na v1.3.1 o ajuste deu ~0, ou seja, a câmera estava certa e o problema era de desenho.
