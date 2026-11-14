# Modelos, texturas e pose — referência técnica

Leia antes de mexer em `tools/modelos.py`, `tools/geometria.py` ou na pose em `tools/gerar.py`. Para criar uma arma, comece por `docs/nova-arma.md`.

## Unidades e eixos

- Unidade de modelagem = **1/64 de bloco**. O osso raiz `arma` recebe `scale: 0.25` na animação; o resultado fica em pixels de modelo (1/16 de bloco).
- Eixos Bedrock da arma:
  - **+Z = cano** (frente);
  - **+Y = cima**;
  - **+X = lado direito da arma** (onde ficam a janela de ejeção e a alavanca da AK).
- Em `modelos.py`, as coordenadas de cada função (`ak47()`, `m4a4()`, `glock()`) são de "projeto". `build()` subtrai `info["grip"]`, deixando o **punho na origem**. O `gerar.py` então soma o pivô `[0, 24, 0]`.
- Cubo: `dict(o=origem, s=tamanho, m=material, r=rotação opcional, p=pivô)`. Ajudantes:
  - `sym()`: cubo simétrico em X;
  - `box()`: cubo livre;
  - `chain()`: carregador curvo em segmentos;
  - `braco()`: antebraço com luva, apontado numa direção;
  - `dentes_z()`: dentes de trilho Picatinny ao longo de Z (passo 1, dente de 0,5).
- Rotação de cubo em X: **rx positivo leva a parte de baixo para +Z** (para a frente). As empunhaduras usam rx negativo, inclinadas para trás.

## Ossos da geometria

| Osso | Pai | Função |
|---|---|---|
| `arma` | — (`binding: q.item_slot_to_bone_name(c.item_slot)`) | raiz; recebe pose, escala e recuo |
| `corpo` | `arma` | a arma |
| `maos` | `arma` | luvas e mangas; `scale 0` fora da 1ª pessoa |
| `alca` (opcional) | `arma` | alça que some na mira (M4: orifício + base + orelhas); `scale` = `ALCA_NA_MIRA` na 1ª pessoa, pivô em `info["alca_pivo"]` (no trilho, para "rebater") |
| `flash` | `arma` | clarão (material `entity_beam_additive`); visível com `v.mostra_clarao` |

Ossos com `binding` ganham um **offset de −24 em Y** (comportamento do jogo, confirmado no preview do Blockbench). Por isso o pivô é `[0, 24, 0]`.

## Texturas

- Atlas **por face**: cada face de cada cubo ganha um retângulo próprio, a **4 texels por unidade**, com 2 px de margem esticada. As faces são empacotadas em prateleiras **ordenadas por altura** (`Atlas.empacotar()`); na ordem de chegada, uma face alta esticava a prateleira inteira e o atlas da AWP ia a 1024x2048, 8x a área necessária. Com a ordenação, as quatro armas cabem em 1024x512. Por isso medidas múltiplas de 0.25 caem em pixels inteiros. Espessuras menores (rebites, inlays) arredondam para 1 px e funcionam por causa da margem. A geometria declara `texture_width = largura_px / 4`, e as UVs ficam nessa escala.
- A pintura (`paint()` em `geometria.py`) é procedural e **em 3D** (v1.3):
  - `contexto_face()` dá a cada texel seu ponto 3D na arma, a normal da face, a distância à borda e a oclusão ambiente.
  - `base_3d()` pinta com ruído 3D (`Ruido3D`), então manchas, veio da madeira e escovado do metal continuam de uma face para a outra e entre cubos vizinhos. O veio e o escovado seguem o **eixo longo do cubo** (com rotação).
  - `detalhes_2d()` aplica os padrões no referencial da face: fendas do quebra-chama, serrilha, nervura do carregador, furos do guarda-mão, trilho, trama da luva, costura da manga.
  - `acabamento()` cuida da luz do céu, do desgaste em manchas e do chanfro de 1 texel só nas quinas **expostas**, além de sujeira e sombra de contato onde as peças se encontram.
  - A oclusão é calculada por SDF dos cubos do mesmo osso: amostras a 0,35, 0,9 e 2 unidades acima da superfície, e qualquer cubo mais perto que a altura da amostra escurece o texel. As mãos não sombreiam a arma, porque somem fora da 1ª pessoa.
  - Detalhes que dependem de posição, como o serrilhado da Glock, continuam sendo **cubos separados**.
- **Renderizador de prévias:** ordena **pedaços** de face (subdivididos), não faces inteiras, e descarta só os pedaços atrás do plano perto. Com a câmera colada na arma (mira), a ordem por face inteira punha faces de trás na frente. O referencial da câmera (direita, cima, frente) é um espelho do bb. A visibilidade usa `n·centro > 0`. Até a v1.2.2 o teste estava invertido e as prévias e os ícones mostravam o verso das faces.
- **Estilo limpo com luz pintada (v1.4.1):**
  - **Sem ruído fino.** O jogo desenha textura sem suavização: com a arma perto do olho, cada texel de granulado vira um quadradinho, e o resultado parece pixelado e sujo. Manchas só em baixa frequência e baixa amplitude.
  - **Luz pintada.** O Minecraft não tem brilho especular em entidade, então ela vem pintada em `acabamento()`:
    - laterais com degradê vertical (`alt` = altura do texel no cubo) e faixa de reflexo perto do topo nos metais;
    - quina de cima clara e nítida e quina de baixo escura (`d_topo`/`d_base`);
    - face de cima mais clara e face de baixo mais escura.
  - **Sombra de contato leve** (`0,78 + 0,22·ao`). Forte demais, numa arma cheia de peças, deixava tudo opaco.
- **Paleta (v1.4):** os materiais metálicos e de polímero ficam em cinzas médios (base ~#40–#60, `METAIS`/`POLIMEROS`). Até a v1.3 eram ~#1e–#45, e sob a luz chapada do Minecraft a arma virava silhueta.
- **Prévia de detalhe:** `detalhe_<arma>.png` (1600x800, perspectiva 3/4 elevada) é a que mostra peça pequena e paleta. A lateral de 512 px é pequena demais para isso.
- Sementes fixas (`rng = default_rng(7)`): regenerar dá exatamente as mesmas texturas.

## Convenção de rotação (Bedrock → matemática)

Verificada no código do Blockbench (`js/formats/bedrock/*`, que converte Bedrock ↔ three.js):

- Espaço "bb" (destro): `x_bb = -x_bedrock` para posições, pivôs e offsets de animação.
- Rotação Bedrock `[rx, ry, rz]` em graus → `R = Rz(rz) · Ry(-ry) · Rx(-rx)`, com matrizes de rotação comuns.
- Ponto num osso: `p' = P + T + R · s · (p − P)`, depois aplica o pai. `P` = pivô, `T` = posição da animação (no espaço do pai), `s` = escala.
- Funções prontas em `tools/bt.py`: `rot_bb`, `vec_bb`, `bone_matrix`, e `euler_from_bb`, que é a inversa (matriz → `[rx, ry, rz]` Bedrock).

## Primeira pessoa

O referencial é o do preview de attachable do Blockbench (`js/formats/bedrock/attachable_preview.js`), usado por quem faz add-ons de armas:

- O modelo vinculado fica em `TB = (-20, 21, 0)`, com rotação ZYX `(-95°, 45°, 115°)`. Isso equivale a `rot_bb([95, -45, 115])`, o braço vanilla em 1ª pessoa, `animation.player.first_person.empty_hand`.
- Câmera do Blockbench (`CAM_BB`, `BC_BB`): em `(0, 19, -40)`, olhando para `(0, 16, 0)`, FOV vertical ≈ 57,4°. Na tela, a direita corresponde a −X bb.
- **Essa câmera não bate com o jogo.** No celular, a arma aparecia ~2x maior e a Glock ficava atrás do plano da câmera (invisível). `CALIB` em `gerar.py` corrige isso: deslocamento `(1,69, −0,15, 5,43)`, rotação pequena e **FOV vertical 67,5°**. Foi obtido ajustando a silhueta renderizada da M4A4 a um print do jogo (1600x738). `CAM`, `BC` e `VFOV` (usados por `first_person`, pela prévia e pelo `ajuste.py`) já são os calibrados. Para recalibrar com um print novo da M4A4, use `python tools/calibrar.py print.png BOCA_X BOCA_Y MASSA_X MASSA_Y`. Ele ajusta pelo IoU da máscara escura + 2 pontos de referência e imprime o `CALIB` novo.
- `first_person(cfg)` em `gerar.py` resolve a rotação e a posição do osso `arma`. O objetivo é colocar o punho em `cfg["grip"] = (direita, cima, profundidade)` no espaço da câmera, com a arma apontando para a frente mais `yaw` (para o centro), `pitch` e `roll` (inclinação lateral).
- `tools/ajuste.py` acha `grip`, `yaw` e `pitch` por otimização, a partir de onde o **cano** e a **traseira** devem aparecer na tela (frações da largura e da altura).
- Recuo: `v.kick` (dente de serra na cadência da arma) desloca a arma **só para trás, no eixo da câmera**. Para cima tirava a mira do lugar, porque a câmera não acompanha. Automáticas ciclam enquanto `q.main_hand_item_use_duration > 0`. A pistola faz **um ciclo por aperto** (`disparo_molang()`: borda de subida do uso), igual ao script, que dá 1 tiro por `itemUse`.
- **Balanços vanilla de 1ª pessoa** (`player_firstperson.animation.json`): respiração no `rightitem` (`sin(q.life_time*45)*0.5`, ciclo de 8 s) e caminhada no `rightarm` (`hand_bob`). Na mira, a respiração fazia a arma subir sozinha por ~2 s (vídeo da v1.2.1). `compensacao_bob()` desconta a respiração sempre e a caminhada × `v.ads`. A caminhada fica no espaço do corpo e vai para o referencial do braço com `R_BASE^T`. As queries do attachable são as do jogador, então `q.life_time`/`q.walk_distance`/`q.position_delta` batem com as do vanilla. Supõe o "balanço da visão" ligado (`v.bob_animation` não é legível); com ele desligado, a compensação vira um balanço próprio de 0,5 un.

## Mira (ADS)

- **Ativação:**
  - agachado: mira completa (`v.ads` → 1);
  - atirando em pé: a arma vai parte do caminho até o centro (`PLACE[...]["atirando"]`: 0,45 nos fuzis e 0,3 na Glock, que perto do olho tapa a tela) e continua puxada por `SOLTA_COMBATE` (0,5 s) depois de soltar, para não ir e voltar a cada toque.

  `v.ads` segue o alvo com suavização por tempo real (`q.delta_time * MIRA_VELOCIDADE`), então não depende do FPS. Histórico: o puxão saiu na v1.2.2, porque a arma "subia" ao atirar. A causa era a respiração vanilla; com ela compensada, o puxão voltou na v1.3.1.
- **Linha de visada:** `info["visada"] = (trás, frente)` em `modelos.py`. Na Glock e na AK vai do topo do entalhe da alça à ponta da massa; na M4, do centro do orifício (peep) à ponta do poste. A linha precisa passar **bem acima** de tudo entre o olho e a alça: na v1.3.1, a tampa da AK escondia o entalhe (regras em `docs/nova-arma.md`). `pose_mira()` põe essa linha **sobre o eixo da câmera** (centro da tela), com a arma reta e o ponto de trás a `PLACE[...]["olho"]` do olho. A inclinação entre visada e cano é compensada no pitch. O alinhamento no centro não depende do FOV do aparelho.
- **Alça que some na mira:** cubos marcados com `osso("alca", cubo)` em `modelos.py` vão para o osso `alca`, que encolhe até o pivô entre `v.ads` 0,55 e 0,75 (`ALCA_NA_MIRA` em `gerar.py`). Na M4, o orifício (peep) ficava a ~3,5 un. do olho, e a moldura e a base tapavam o centro da tela (v1.4.1). Com a alça recolhida, mira-se pela massa. Atirando em pé (`v.ads` 0,45) ela continua visível. As prévias de mira já a escondem. A oclusão das texturas trata `corpo` e `alca` juntos.
- **Luneta (AWP, v1.6):** `visada` = centro da ocular → centro da objetiva; `olho` = alívio de olho; no script, `mira.fov` bem menor (18). Mas uma luneta em escala real vira um canudo: o furo útil fica com ~2° de campo e não se enxerga nada. Por isso a mira é feita como nos FPS:
  - na mira completa (`NA_LUNETA`: `v.ads > 0,93`) os ossos `corpo` e `maos` recebem `scale 0` — **a arma some**;
  - entra o osso `luneta`, um painel logo atrás da ocular, preto, com um furo circular e o retículo em cruz;
  - o painel é **geometria** (`painel_luneta_cubos()` em `geometria.py`: faixas pretas que contornam o círculo, mais 4 barras da cruz), e não textura, porque uma máscara de 512x256 estourava o atlas;
  - `painel_luneta()` em `gerar.py` dimensiona tudo pelo **FOV normal** (`VFOV`), não pelo do zoom. O painel tem 1,5x a meia-altura da tela de folga, e o furo tem `MIRA_CIRCULO` (0,86) da altura da tela.
  - **Por que pelo FOV normal:** o `/camera fov_set` exige cheats e só aceita 30 a 110 (a v1.6.0 pedia 18 e era recusada), e a arma em 1ª pessoa parece ter FOV próprio — a calibração deu 67,5, diferente do FOV do mundo. Assim o painel cobre a tela com zoom ou sem. Se um print mostrar a vinheta sumindo ao agachar, o zoom também amplia a arma e aí é só dimensionar por `FOV_ZOOM`.
  - O painel entra só em `v.ads > 0.995`: ligado antes, a arma ainda está a caminho e ele aparece torto e fora do centro (foi o que o vídeo da v1.6.0 mostrou).
  - A prévia `fp_mira_<arma>.png` de uma arma com luneta usa o FOV normal com o **fundo ampliado** por `FOV_ZOOM`, que é o que o jogador vê.
- **Caminho quadril → mira:** interpolar direto os ângulos de Euler do osso não anda reto na tela (a arma cresce e desce em vez de ir ao centro). Por isso `caminho_mira()` interpola **no espaço da câmera** (punho, yaw, pitch, roll, com suavização nas pontas) e resolve `QUADROS_MIRA` + 1 quadros-chave exatos. A animação `primeira_pessoa` usa `"anim_time_update": "v.ads"` (tempo da animação = `v.ads`) e `animation_length` 1,05 para nunca terminar. O recuo é somado em cada quadro e cai para `RECUO_MIRA` na mira.
- **Câmera agachada (`AGACHADO` em `gerar.py`):** agachado, a câmera do jogo se desloca em relação ao braço em **(+1,187 direita, −1,283 cima, +1,521 frente)** no espaço da câmera, com o mesmo FOV. O valor atual (v1.6.2) foi medido com `tools/calibrar_mira.py`, pelo painel da luneta da AWP: ele fica a ~1,7 un do olho (contra 7,5 da AK), então amplia o resíduo umas 4x, e 6 quadros do vídeo com o jogador parado deram o mesmo valor. O valor anterior (1,346, −1,009, 1,757), ajustado por silhueta na v1.2.1, deixava o retículo 8° fora do centro — e o tiro sai sempre do centro da tela. Isso foi medido na v1.2.0: nos prints de mira do celular a arma ficou paralela à mira, mas para a esquerda, para cima e colada na câmera. Ajustando só uma translação da câmera, os 3 prints (M4, AK e Glock) encaixam com erro de silhueta ~0,08. O print de quadril da v1.1.0 rejeita esse deslocamento (erro de 0,11 para 0,24), então ele só vale agachado. `caminho_mira()` soma `peso_agachado(t) * AGACHADO` ao punho: o peso é 0 até a fração `atirando` (em pé, câmera normal) e sobe até 1 na mira completa. As prévias de mira são renderizadas com a câmera agachada. Na v1.3.1, dois prints mirando (Glock e AK) encaixaram na câmera calibrada com correção ~0 (translação < 0,3 un.), o que confirmou `CALIB` + `AGACHADO`. Se um print novo mostrar a mira deslocada, refaça esse ajuste antes de mexer no `PLACE`: silhueta do print × modelo na pose `1.0000`, variando só a translação da câmera. O script usado ficou fora do repositório; ele é uma variação do `tools/calibrar.py` (máscara escura + madeira, áreas do HUD descartadas, Nelder-Mead nos 3 eixos).
- **Prévias:** `fp_mira_<arma>.png` (a cruz deve cair na ponta da massa) e `fp_transicao_<arma>.png` (quadril, meio caminho, mira), feitas com a mesma interpolação do jogo (`mistura()`).
- **Script:** `ARMAS[id].mira = { fov, dispersao }`. Agachado com arma: `/camera @s fov_set <fov> 0.2 in_out_sine`; ao sair, `fov_clear`. O comando só é enviado quando o estado muda e fica em `try/catch`: sem o comando, a mira funciona sem zoom. A dispersão é multiplicada por `mira.dispersao`.
- **Plano de corte da câmera:** na mira, a coronha e as mangas passam por trás da câmera. O renderizador de prévias descarta só os pedaços de face atrás do plano (`perto` = 0,05); o jogo corta no plano dele. Até agora não apareceu problema no aparelho.

## Terceira pessoa

- Com o `POSE_RP` ativo, o jogador declara a variável pública `v.joao_mira = 1`. O attachable lê `c.owning_entity->v.joao_mira` e usa a animação `terceira_mira`, calculada para o braço em `[-90, -5.73, 0]`, que acompanha o pitch da mira.
- Sem o `POSE_RP`, a animação é `terceira_baixo`, para o braço quase pendurado (`[-18, 0, 0]`), com a arma apontando para a frente.
- Pivô do braço direito em bb: `(5, 22, 0)`. O item fica em `(1, −7, 1)` em relação ao braço.

## Rajada e animações no attachable

`pre_animation` do attachable (gerado por `disparo_molang()` e pelo `main()` do `gerar.py`):

- **Fuzil (automática):** `v.atirando = q.main_hand_item_use_duration > 0`; `v.ciclo = math.mod(q.life_time * 20, intervalo) / intervalo`. Cicla enquanto o dedo está na tela, como a rajada do script.
- **Pistola (semi):** `v.t_tiro` zera na borda de subida do uso (`v.usando && !v.usou`) e conta o tempo; `v.ciclo = min(v.t_tiro * 20 / intervalo, 1)`. **Um ciclo por toque**, como o script, que dá 1 tiro por `itemUse`. Antes, segurar a Glock repetia a animação sem som nem tiro.
- `v.kick = v.atirando ? 1 − v.ciclo : 0`; `v.mostra_clarao = v.atirando && v.ciclo < 0,34`.
- Mira: `v.uso`, `v.t_solto`, `v.alvo_ads`, `v.ads` (ver "Mira (ADS)").
- Balanços: `v.respira`, `v.mao_bob`, `v.passo_x`, `v.passo_y` (ver "Primeira pessoa").

As queries (`q.*`) no attachable são as do **jogador** (`q.is_sneaking`, `q.life_time`, `q.walk_distance`, `q.main_hand_item_use_duration`). As variáveis (`v.*`) são do próprio attachable e persistem entre quadros (confirmado com `v.ads`). Variáveis do jogador só são legíveis se forem públicas: `c.owning_entity->v.joao_mira`, declarada pelo `POSE_RP`.

O clarão e o recuo são **visuais e sincronizados por tempo**, não pelo tiro real do script. O tiro real é o `system.runInterval` no `main.js`.
