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

Desde a v1.7.2 a lista de armas mora num lugar só — `tools/dominios/armas/registro.py`. O que sobrou
para fazer à mão são os arquivos que **não** derivam dela:

1. `tools/dominios/armas/modelos.py`: a função do modelo (`def nome()`). Modele **peça por peça**, sem teto de cubos: a M4A4 da v1.4 (~150 cubos) é a referência de nível. Ajudantes:
   - `dentes_z()`: trilhos Picatinny;
   - `chain()` + `nervuras_carregador()` + `base_carregador()`: carregador curvo completo;
   - dois cubos cruzados: peças "redondas" (tubos);
   - dois cubos sobrepostos girando no mesmo pivô com ângulos diferentes: peça que afina, como a coronha da AK.

   Peças finas e salientes (janelas, chapas) precisam de pelo menos 0,1 de espessura, senão cintilam (z-fighting). O `info` precisa de:
   - `grip`: ponto do punho;
   - `muzzle`: boca do cano;
   - `visada`: (ponto de trás, ponto da frente) da linha de mira (veja as regras abaixo);
2. **`tools/dominios/armas/registro.py`: uma linha em `ARMAS`** — id, nome, tipo, a função do modelo, o `place` (valores na tabela abaixo), o alvo da traseira para o `ajuste.py` e a ordem no site. Daqui saem sozinhos o laço da geração, os nomes na tela, a pose de 3ª pessoa e o suporte de armas do site.
3. `tools/dominios/armas/sons.py`: 3 variações de tiro. Também `packs/RP/sounds/sound_definitions.json` (`joao.<nome>.tiro`).
4. **`packs/BP/items/<nome>.json`: é aqui que a arma ganha os números.** Copie de uma arma do mesmo tipo e preencha:
   - `minecraft:tags`: `joao:arma_fogo` mais `joao:disparo_rajada` **ou** `joao:disparo_semi`;
   - o componente `joao:arma_fogo`: `nome`, `dano`, `alcance`, `intervalo` (igual ao do `place`), `municao`, `municao_nome`, `som`, `tom`, `dispersao`, `mira_fov`, `mira_dispersao` e, se empurrar mais que o normal, `empurrao`.

   Mantenha `minecraft:use_modifiers` (sem isso, "segurar para atirar" não funciona no celular). Faça também `packs/BP/recipes/<nome>.json`. **Nenhum script muda**: `packs/BP/scripts/armas/index.js` não conhece arma nenhuma pelo nome desde a v1.7.2.
5. `packs/RP/textures/item_texture.json`: `joao_<nome>` → `textures/items/<nome>` (o ícone é gerado).

## Valores de referência

| Parâmetro | Fuzil com alça no meio (AK) | Fuzil com alça atrás (M4) | Pistola (Glock) | Sniper (AWP) | Besta |
|---|---|---|---|---|---|
| `olho` (un. de câmera, 1/16 bloco) | 7,5 | 3,5 | 2,5 | 2,0 | 2,0 |
| `atirando` (fração do caminho até a mira) | 0,45 | 0,45 | 0,3 | 0,3 | 0,3 |
| `intervalo` (ticks entre tiros) | 3 | 3 | 5 | 25 | 15 |
| `mira.fov` / `mira.dispersao` | 52 / 0,3 | 52 / 0,3 | 58 / 0,4 | 30 / 0,04 | 40 / 0,25 |
| `yaw` / `pitch` / `roll` no quadril | 5,7 / 1 / −4 | 5,7 / 1 / −4 | 5,8 / 1 / −3 | 5,7 / 1 / −4 | 11,5 / 1 / −4 |

A besta foge do padrão de propósito: ela é **larga**, e com o yaw dos fuzis os arcos — que são a cara
dela — ficavam fora da tela. O `yaw` maior traz a frente para dentro do quadro. `tools/dominios/armas/ajuste.py` tem
alvos de tela próprios para o tipo `"besta"`.

- `olho` é a distância do olho ao ponto de trás da visada na mira. A alça no meio da arma pede olho mais longe, senão o olho entra na caixa. Alça traseira e pistola ficam perto; com olho grande, a pistola parece pequena e distante (v1.3.1).
- `atirando` alto na pistola faz ela tapar a tela (v1.2.1).
- Luneta: `visada` = centro da ocular → centro da objetiva; `olho` = alívio de olho; `mira.fov` bem menor (~20).

## Nível de detalhe e cores (padrão da v1.4)

- Referência: add-ons de arma do mercado com 150 a 300 cubos por arma. O realismo vem da **geometria**: cada peça real que se vê de 1 m vira cubo (reténs, pinos, seletor, dobradiças, anéis, orelhas, dentes de trilho). Textura limpa, sem ruído fino. A luz é pintada automaticamente (degradê, reflexo, quinas) pelo `acabamento()`.
- Medidas reais: defina a escala (cm por unidade) a partir do comprimento total e confira as proporções principais (cano, caixa, carregador, coronha). A M4A4 usa ~1,3 cm/un.
- Cores: use os materiais existentes. Eles estão em cinzas médios de propósito, porque preto de verdade vira silhueta no jogo. Diferencie peças por material (ex.: `aco` na massa e nos pinos, `anodizado` no receptor, `carregador_m4` mais claro).

## Tipos de arma

`modelos.ARMAS[id] = (função, tipo)`. Hoje o tipo decide as **mãos** e o tamanho do recuo:

| Tipo | Mãos | Recuo |
|---|---|---|
| `"fuzil"` | duas mãos, a esquerda no guarda-mão | normal |
| `"pistola"` | duas mãos juntas na empunhadura | menor |
| `"sniper"` | igual ao fuzil | bem maior |
| `"besta"` | igual ao fuzil | bem menor (tranco, não coice) |

Um tipo novo tem de ser registrado nos **três** lugares onde o tipo é testado, e não há outros:
`maos()` em `modelos.py`, o dicionário do recuo em `attachables.py` e os alvos de tela em `ajuste.py`.
A pose de 3ª pessoa saiu dessa lista na v1.7.2: ela agora lê `registro.do_tipo(...)`. Era justamente
ali que a AWP ficava de fora até a v1.6.3, por ser uma lista escrita à mão.

A **animação de disparo é igual para todos** desde a v1.6.5: um ciclo por tiro de verdade, disparado pelo cooldown `joao_tiro` que o `main.js` liga ao atirar. Quem decide se a arma solta rajada é o `automatica` no `main.js`, não o tipo.

## Ossos que se mexem (corda da besta, dardo na calha)

`info["ossos"]` leva um dicionário `nome -> dict(pivo, anim, repouso)`. Cada entrada vira um osso
filho de `arma`, com os cubos marcados por `osso("<nome>", cubo)` em `modelos.py`:

- **`pivo`**: ponto em volta do qual o osso gira ou escala, nas coordenadas do modelo;
- **`anim`**: o que entra na animação de 1ª pessoa (`rotation`, `position`, `scale`), em Molang. É
  aqui que se usa `v.ciclo`, que vai de 0 (saiu o tiro) a 1 (arma pronta de novo) no intervalo da
  arma — ele já existe e já é disparado pelo tiro de verdade;
- **`repouso`**: a pose parada. **É obrigatória quando a pose desenhada não é a pose correta.** As
  prévias não interpretam Molang, e é também o que o jogo mostra se a animação falhar: sem isso, a
  corda da besta aparecia reta, do jeito que foi desenhada, em vez de formar o V.

A alça rebatível da M4 usa o mesmo mecanismo por outro caminho (`alca_pivo` no `info`).

Na mira com luneta, esses ossos recebem `scale 0` junto com a arma.

## Arma com luneta

- Ponha `luneta=True` no `info` e a `visada` no **eixo óptico** (centro da ocular → centro da objetiva).
- Na mira completa (`v.ads` > 0,93), o gerador faz a **arma sumir** e mostra o osso `luneta`: um painel preto com furo circular e retículo em cruz, como nos FPS. Sem isso, o tubo da luneta taparia a visão.
- O painel é **geometria** (faixas pretas), não textura: em textura precisaria de ~512x256 e estourava o atlas.
- Ele é dimensionado pelo FOV normal, então cobre a tela com zoom ou sem.
- `mira.fov` no `main.js` só vale entre **30 e 110**: fora disso o jogo recusa o zoom em silêncio. E o `/camera fov_set` exige **Cheats ligados** no mundo.
- A luneta em si pode ser modelada sólida e realista: na mira ela não aparece.
- O painel é ajustável por arma, no `info`: `luneta_furo` (fração da altura da tela; 0,86 na AWP,
  0,93 na besta, que é de média distância e tem campo mais largo), `luneta_duplex` (retículo de
  rifle, fino no centro e com posto grosso nas bordas) e `luneta_marcas` (tracinhos de queda abaixo
  do centro). O zoom por arma é `fov_mira` no `PLACE`, e **tem de ser igual** ao `mira.fov` do script.

## Besta: a direção dos arcos

**Os arcos abrem para TRÁS.** O riser fica na ponta da frente e as roldanas ficam atrás dele, perto do
atirador — é o que as fotos de qualquer besta mostram, e foi o primeiro erro que o João viu na v1.7.
Em `trecho_arco()`, isso é `ry` **positivo** para o lado direito (negativo levaria a ponta para a
frente). Como consequência, a corda solta para na linha das roldanas: é por isso que
`SERVING_SOLTA_Z` fica logo atrás delas, e não num ponto qualquer.

A besta também é **quase tão larga quanto comprida**: 53 cm de ponta a ponta dos arcos contra 76 de
comprimento (a EK Cobra R9 das fotos é 67 x 58 cm). Com os arcos em metade disso, o João olhou e disse
na hora que o T estava pequeno — a besta lia como um fuzil com dois apêndices. Com a posição de tela dos fuzis, os arcos saíam do quadro em 1ª pessoa, e a besta virava um
fuzil com luneta — daí o `yaw` maior no `PLACE`, que cruza a arma no campo de visão em vez de deixá-la
apontada para longe. **`yaw` menor mostra menos**, não mais: a arma fica de enfiada e só se vê a
coronha.

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
   - `lado_<nome>.png`: proporções, e vira o ícone. Arma larga pode pedir `vista_icone="topo"` no
     `info`: de lado, a besta vira uma barra igual a um fuzil, e de cima vê-se o T dos arcos e a
     corda em V;
   - `tp_<nome>.png`: 3ª pessoa.
2. Desde a v1.3.2, o renderizador de prévias é confiável de perto: ordena por pedaço de face e mostra a face certa. Só não tem a luz do jogo.
3. `--versao`, `--deploy` e `--publicar`. Peça ao Afonso prints **mirando agachado**, **em pé** e **atirando em pé**.
4. Se o print mirando não bater com `fp_mira_<nome>.png`, meça antes de mexer no `PLACE`. Ajuste a silhueta do print contra o modelo na pose `1.0000`, variando só a translação da câmera (ver "Câmera agachada" em `docs/modelos-e-pose.md`). Na v1.3.1 o ajuste deu ~0, ou seja, a câmera estava certa e o problema era de desenho.
