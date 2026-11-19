# Modpack Expansível do João — add-on de Minecraft Bedrock

## Origem e visão geral

- O projeto nasceu como **"Armas do João"**, mas o objetivo real é um **Modpack/Add-on Expansível do João** para Minecraft Bedrock. O João joga principalmente **no celular** e às vezes no PC do Afonso.
- A ideia central é trazer para o Bedrock tudo o que o João gosta e que normalmente só existe com qualidade em mods do Minecraft **Java Edition**:
  - armas de fogo;
  - dinossauros (ex.: Jurassic World);
  - veículos;
  - armaduras;
  - animais;
  - qualquer outra mecânica ou criatura que ele pedir no futuro.
- Hoje existem 5 armas: Glock, AK-47, M4A4, AWP e a Besta Tranquilizante (que não mata: põe o bicho para dormir). Os nomes dos packs nos manifests ainda são "Armas do João". Renomear o nome exibido é permitido; **os UUIDs nunca mudam**.
- Quem desenvolve é o **Afonso**, tio do João e desenvolvedor.

## Perfil do João e padrão de qualidade (realismo estrito)

- O João é autista e tem um nível de **exigência e atenção aos detalhes altíssimo**.
- Ele já jogou e conhece vários mods/add-ons famosos (Aplok Guns, add-ons de Jurassic World etc.) e usa esses projetos como **régua de comparação direta**. Se ficar abaixo deles, ele percebe.
- **Regra de ouro visual e funcional**: nada pode parecer infantil, genérico, "blocudo" demais ou improvisado. Isso vale para tudo:
  - modelos 3D com proporções fiéis ao objeto ou animal real;
  - texturas bem pintadas, com sombreamento realista (desgaste, veio, gradiente, material);
  - animações e poses de 1ª e 3ª pessoa convincentes, no nível de FPS ou de mods do Java;
  - sons realistas;
  - mecânicas fluidas, sem travadas, atrasos estranhos ou comportamento "de protótipo".
- Na dúvida entre entregar rápido e entregar no padrão, **entregue no padrão** e avise o que ficou para a próxima iteração.
- Público infantil: **sem sangue nem gore**. Acerto em criatura = faíscas, som e empurrão.
- **Engenharia reversa de estudo**: é permitido dissecar add-ons de referência do mercado para entender como resolveram problemas complexos no Bedrock (raycast, poses, animação de entidades, física de veículos) e adaptar a **lógica** para os nossos geradores e scripts. **Nunca copie arquivos brutos de terceiros**: modelo, textura, som, animação ou código colado. Respeite as licenças; o Aplok Guns, por exemplo, é CC BY-NC-ND. Estude em pasta separada, fora de `packs/`, e não faça commit de material de terceiros.

## Comandos

```bash
python tools/build.py               # valida JSON (+ tsc se houver node_modules) e gera dist/*.mcaddon
python tools/build.py --gerar       # regenera RP (modelos/texturas/attachables/animações/sons/ícones) + previews/
python tools/build.py --versao X.Y.Z  # sobe a versão de TODOS os manifests e das dependências entre eles
python tools/build.py --deploy      # copia packs para development_*_packs do Minecraft no Windows
python tools/build.py --site        # gera o site de downloads em site/ (dist/*.mcaddon + CHANGELOG.md)
python tools/build.py --publicar    # gera o site e publica na Vercel (1ª vez: npx vercel login)
python tools/dominios/armas/ajuste.py              # resolve PLACE (posição em 1ª pessoa) a partir de alvos na tela
python tools/dominios/armas/calibrar.py print.png ...  # recalibra a câmera real (CALIB) a partir de um print da M4A4
python tools/dominios/armas/medir_mira.py awp=a.png glock=b.png ...  # mede a mira em prints do jogo e corrige os ângulos do CALIB
npm run check                       # tsc contra @minecraft/server 2.0.0
```

Depois de mudar qualquer coisa que o jogador vê: rode `--gerar` e **olhe as imagens em `previews/`**:
- `fp_*.png`: primeira pessoa simulada (`fp_mira_*` e `fp_transicao_*` para a mira);
- `detalhe_*.png`: 3/4 grande, para julgar peças pequenas e a paleta;
- `lado_*.png`: vista lateral, que vira o ícone;
- `tp_*.png`: terceira pessoa. Antes de entregar uma versão nova, use `--versao` (o Minecraft ignora um pack reimportado com a mesma versão).

## Fluxo de trabalho

1. Edite a **fonte**, nunca arquivo gerado (veja a seção abaixo).
2. `python tools/build.py --gerar`.
3. **Abra** as prévias afetadas em `previews/` com a ferramenta de leitura de imagem antes de dizer que ficou bom.
4. `python tools/build.py --deploy`: o Afonso testa no PC.
   - mudou só o script: `/reload` no jogo;
   - mudou modelo, textura, som, item ou entidade: sair e entrar no mundo.
5. Para o celular: `--versao X.Y.Z` e depois `--publicar`. O João baixa pelo site; a versão mais nova do CHANGELOG com `.mcaddon` em `dist/` vira o botão principal. Ao confirmar no aparelho, marque **[testado no celular]** no CHANGELOG e publique de novo: o site mostra o selo.

As prévias não têm a iluminação do jogo, e o FOV do celular varia. Quando mexer em posição, tamanho ou animação, **peça print ou vídeo do jogo** antes de dar como resolvido. No Windows, use `python` ou `py` no PowerShell. Os sons precisam de `ffmpeg` no PATH (`winget install Gyan.FFmpeg`).

## O que é gerado e o que é editado à mão

- **Editado à mão**: `packs/BP/**` **exceto as subpastas `dinossauros/`** (itens, receitas, scripts), `packs/RP/manifest.json`, `packs/RP/sounds/sound_definitions.json`, tudo em `tools/`.
- **Gerado por `build.py`**: `packs/RP/textures/item_texture.json`, montado com o que cada domínio declara (`TEXTURAS` nas armas, os ícones no de dinossauros). Era escrito à mão até a v1.7.1.
- **Gerado por `tools/dominios/dinossauros/`**: `packs/BP/items/dinossauros/*`, `packs/BP/recipes/dinossauros/*`, `packs/BP/blocks/dinossauros/*`, os modelos e texturas de bloco (`packs/RP/models/blocks/`, `textures/blocks/`, `terrain_texture.json`, `blocks.json`), os ícones de fóssil, ovo e DNA, e **`packs/BP/scripts/dinossauros/especies.js`** — a tabela que o script lê, escrita a partir do `especies.py` para a lista não existir em dois lugares. Tudo sai de `especies.py` — **acrescentar um dinossauro é uma linha lá**. O gerado mora em subpasta própria (o Bedrock varre subpastas) para nunca se misturar com o que é escrito à mão; marcar o arquivo com uma chave de comentário não serve, porque uma chave a mais num JSON de item faz o item sumir sem erro.
- **Gerado por `tools/dominios/armas/attachables.py` (não editar direto)**: `packs/RP/models/entity/joao/*`, `packs/RP/textures/entity/joao/*`, `packs/RP/attachables/*`, `packs/RP/animations/joao_armas.animation.json`, `packs/RP/render_controllers/*`, `packs/RP/textures/items/{glock,ak47,m4a4}.png`.
- Site de downloads: modelo em `tools/site/modelo.html` (editado à mão), gerador `tools/site_joao.py`; a pasta `site/` é gerada (não editar).
- Gerado por `sons.py` → `packs/RP/sounds/joao/*.ogg`; `municao.py` → ícones de munição; `icone.py` → `pack_icon.png`; `pose.py` → `packs/RP/entity/player.entity.json` e `animations/joao_mira.animation.json`; `dardo.py` → entidade do dardo em voo (`models/entity/joao/dardo.geo.json`, `entity/dardo.entity.json`, `render_controllers/joao_dardo.*`, `textures/particle/joao_sono.png`).
- **Editado à mão também**: `packs/BP/entities/*` (comportamento de entidade é dado, não geração) e `packs/RP/particles/*`.

## Arquitetura escalável e orientada a dados (multi-domínio)

**Objetivo**: adicionar um item, arma, dinossauro, veículo ou armadura novo **rapidamente**, sempre que o João pedir. Isso não pode exigir reescrever sistemas do zero nem transformar arquivos centrais em monólitos. Uma coisa nova = **dados novos + no máximo um módulo novo**. Não se edita `if/else` espalhado.

Domínios previstos: `armas`, `dinossauros`, `veiculos`, `armaduras`, `animais`, mais o que vier.

### Tags e dados no Behavior Pack (`packs/BP/`)

- **Itens**: classificação via componente `minecraft:tags`, por exemplo `"minecraft:tags": { "tags": ["joao:arma_fogo", "joao:disparo_rajada"] }`. O script consulta com `itemStack.hasTag()`/`getTags()`.
- **Parâmetros de item** (dano, alcance, cadência, munição, dispersão, som) ficam no **próprio JSON do item**, num componente customizado com parâmetros. Exemplo: `"joao:arma_fogo": { "dano": 8, "intervalo": 3, "alcance": 64, "municao": "joao:municao_fuzil", "som": "joao.ak47.tiro" }`. O componente é registrado em `system.beforeEvents.startup` com `itemComponentRegistry.registerCustomComponent(...)`, e o handler recebe os valores em `CustomComponentParameters.params` (API 2.0.0). O script **não** guarda tabelas por ID de item.
- **Entidades** (dinossauros, animais, veículos): classificação via `minecraft:type_family`, por exemplo `["joao", "joao:dino", "joao:dino_carnivoro", "mob"]`. O script consulta com `entity.matches({ families: [...] })` ou com o componente `minecraft:type_family`. Use `entity.addTag()` (tags de runtime) apenas para **estado** (ex.: `joao:montado`), não para classificação.
- Comportamento de entidade é feito primeiro com **componentes e eventos nativos** (`minecraft:behavior.*`, `minecraft:rideable`, `component_groups`). Script entra só no que o JSON não resolve.
- Taxonomia inicial (amplie e registre aqui quando criar uma tag nova):

| Tag / família | Aplica-se a | Significado |
|---|---|---|
| `joao:arma_fogo` | item | arma que dispara (usa o componente `joao:arma_fogo`) |
| `joao:disparo_rajada` / `joao:disparo_semi` | item | modo de disparo |
| `joao:municao` | item | qualquer munição |
| `joao:armadura` | item | peça de armadura do modpack |
| `joao:dino`, `joao:dino_carnivoro`, `joao:dino_herbivoro` | entidade (family) | dinossauros |
| `joao:animal` | entidade (family) | animais do modpack |
| `joao:veiculo`, `joao:veiculo_terrestre`, `joao:veiculo_aereo`, `joao:veiculo_aquatico` | entidade (family) | veículos |
| `joao:dardo` | entidade (family) | dardo tranquilizante em voo (`joao:dardo_voo`) |
| `joao:fossil` | item | o osso que sai de minerar fundo; vira DNA no extrator |
| `joao:dna` / `joao:ovo_dino` | item | tubo de DNA e ovo fecundado, um par por espécie |
| `joao:ovo_sintetico` | item | a casca vazia, da bancada |
| `joao:maquina` | **bloco** | componente customizado do extrator e da incubadora, com `{"tipo": ...}` |
| `joao:fase` | estado de bloco | 0 parada · 1 trabalhando · 2 pronta. É o que acende a luz e põe o ovo no ninho |
| `joao:sedavel` | entidade (family) | **dorme de verdade** com o dardo: o script dispara nela os eventos `joao:dormir` / `joao:acordar`, que o JSON do bicho tem de declarar (deitar, calar, desligar os `behavior.*`). Sem essa família, o script só congela o bicho com lentidão e fraqueza, que é o máximo que dá num mob do jogo |
| `joao:dormindo` | entidade (tag de runtime) | **estado**, não classificação: quem está adormecido agora |

### Script API modular (`packs/BP/scripts/`)

`main.js` é **apenas o ponto de entrada**. Ele assina os eventos de `@minecraft/server` uma única vez, roteia para os domínios por tag/família e registra os componentes customizados. Lógica de domínio não fica nele.

```
scripts/
  main.js                 # router: eventos → domínios; startup → registro de componentes
  comum/
    raycast.js            # tiro/visão: blocos + entidades, dispersão
    efeitos.js            # partículas e sons (com try/catch para área descarregada)
    hud.js                # actionbar / mensagens
    inventario.js         # contar/gastar itens
    tags.js               # constantes das tags e famílias (fonte única dos nomes)
    mira.js               # zoom (/camera fov_set), pedido em nome do domínio
  armas/
    index.js              # registra o componente joao:arma_fogo; tiro, rajada, munição
  sedativo/
    index.js              # besta: lança o dardo (entidade), doses e sono
  laboratorio/
    index.js              # extrator e incubadora: componente de BLOCO, estado em dynamic property
  dinossauros/
    especies.js           # GERADO do especies.py — a lista de espécies e o sorteio
  paleontologia/
    index.js              # o fóssil ao minerar (por script, não por feature_rules)
  dinossauros/            # comportamento que o JSON não cobre (ex.: rugido, montaria especial)
  veiculos/               # controle, física, combustível
  armaduras/              # efeitos de conjunto completo etc.
```

- Cada domínio exporta um objeto `dominio` com ganchos opcionais (`iniciar`, `aoUsar`, `aoComecarUso`, `aoSoltarUso`, `aCadaTick`, `aoSair`). O contrato está em `comum/dominio.js`; o `main.js` assina cada evento **uma vez** e repassa a quem declarou o gancho. Domínios **não importam uns aos outros**; o que for compartilhado vai para `comum/`.
- Um único `system.runInterval` por domínio, no máximo, e o laço por jogador é o do `main.js` (`aCadaTick`). Prefira eventos a polling.
- **Recurso compartilhado precisa de dono.** O zoom da mira é de dois domínios (arma de fogo e besta), então `comum/mira.js` guarda quem pediu e ignora um "limpar" de outro: sem isso, com a besta na mão, um domínio mandava tirar o zoom e o outro mandava pôr, a cada tick.
- `npm run check` precisa cobrir todos os arquivos (`jsconfig.json` já inclui `packs/BP/scripts/**/*.js`).

### Geradores modulares (`tools/`)

Mantém-se a geração procedural em Python (`build.py --gerar`) com **prévias automáticas em `previews/`** para validação visual antes do celular. A estrutura evolui para domínios:

```
tools/
  build.py                # orquestra: --gerar roda todos os domínios de DOMINIOS, na ordem
  icone.py                # pack_icon.png (depende das prévias laterais das armas, então roda por último)
  site_joao.py            # site de downloads
  nucleo/
    bt.py                 # rotação Bedrock ↔ Blockbench
    geometria.py          # build_geometry, pintura 3D, atlas, renderizador de prévias
    jsonc.py              # JSON tolerante a comentários (validação do build)
  dominios/
    armas/                # as 5 armas + a besta
      __init__.py         #   gerar(rp, bp, previews) — o contrato que o build.py chama
      modelos.py          #   as formas (cubos e ossos de cada arma)
      attachables.py      #   geometria, attachable, animações, pose 1ª/3ª pessoa, ícones, prévias
      dardo.py            #   a entidade do dardo em voo
      pose.py sons.py municao.py
      ajuste.py calibrar.py medir_mira.py   # calibração, rodados à mão
    dinossauros/          # entity completa: ossos articulados, animações, controllers, laboratório
    armaduras/ animais/ veiculos/           # quando chegarem
```

**Armadilha de nome:** o `__init__.py` de um domínio define a função `gerar`, então **nenhum módulo
dentro dele pode se chamar `gerar.py`** — o atributo do pacote sombreia o submódulo e o import devolve
a função. Foi por isso que o montador das armas virou `attachables.py`.

- **Dois tipos de saída no RP**:
  - armas e armaduras = **attachable** (segue o osso do jogador);
  - dinossauros, animais e veículos = **client entity** completa (`entity/`, `animations/`, `animation_controllers/`, `render_controllers/`), com o par no BP (`entities/`).
- Cada domínio expõe a mesma interface para o `build.py`, por exemplo `gerar(rp, bp, previews)`. Ele escreve só nas suas próprias pastas (`.../joao/<dominio>/...`) e produz prévias com prefixo do domínio (`previews/<dominio>_*.png`).
- Entidades precisam de prévias de **pose e animação** (quadros-chave lado a lado), não só da pose estática.

### Estado atual × alvo (migração)

- **Feito na v1.7.0**: o script está modular (`main.js` só roteia; `comum/`, `armas/`, `sedativo/`), em commit próprio e sem mudar comportamento.
- **Feito na v1.7.2**: os geradores em Python estão em `nucleo/` + `dominios/armas/`, e o `build.py` varre a tupla `DOMINIOS`. A lista de armas, que se repetia em sete lugares, virou `dominios/armas/registro.py` — uma entrada por arma, de onde saem o laço da geração, os nomes, o `PLACE`, a pose de 3ª pessoa, a ordem do site e os alvos do `ajuste.py`. As duas mudanças são movimentação pura: `--gerar` saiu byte-idêntico (só os `.ogg` mudam, porque o sintetizador não os reproduz bit a bit).
- **Feito na v1.7.2**: as armas são `minecraft:tags` + o componente customizado `joao:arma_fogo`, registrado em `system.beforeEvents.startup`. Os números (dano, alcance, cadência, munição, som, dispersão, mira) estão no JSON de cada item e chegam ao script pelo `params`; `armas/index.js` não conhece nenhuma arma pelo nome. Os IDs não mudaram. **Confirmado no jogo**: as armas aparecem e atiram, então componentes customizados funcionam nesta versão — é o mesmo mecanismo que os blocos do laboratório usam.
- **Consequência conhecida**: o jogo só entrega o `params` quando o componente dispara, e não há gancho de "equipou". A ficha da arma entra em cache no primeiro uso, então pegar uma arma e agachar **antes** de atirar mira sem ampliação (a pose vem do resource pack e funciona; o zoom depende de Cheats de qualquer jeito). Do primeiro tiro em diante, normal.

## Convenções

- Namespace `joao:`. IDs: `joao:glock`, `joao:ak47`, `joao:m4a4`, `joao:awp`, `joao:besta`, `joao:municao_pistola`, `joao:municao_fuzil`, `joao:municao_sniper`, `joao:dardo`. Entidades: `joao:dardo_voo`. Sons `joao.*`, geometrias `geometry.joao.*`, animações `animation.joao.*`, partículas `joao:*`.
- Script API `@minecraft/server` **2.0.0** (jogo ≥ 1.21.90). `min_engine_version` [1,21,90] no BP e no RP.
- Tiro = raycast instantâneo (`getBlockFromRay` + `getEntitiesFromRay`) a partir da cabeça; dano via `applyDamage` creditado ao jogador. Rajada: `itemStartUse`/`itemStopUse` + `runInterval`; o `itemUse` sempre dá 1 tiro (fallback se a rajada não funcionar no celular). Itens têm `minecraft:use_modifiers` (use_duration 3600) para permitir segurar.
- Para adicionar uma arma, siga **`docs/nova-arma.md`**. Ele traz:
  - a entrada no `registro.py` e os poucos arquivos que ainda se escrevem à mão;
  - os valores de referência de `olho`, `atirando`, `fov` e pose;
  - as regras de desenho da mira;
  - a validação.

  Câmera, sistema de mira, compensações e pintura já vêm prontos. Esse é o fluxo atual; depois da migração, vira item JSON com tags + `joao:arma_fogo` + módulo do gerador.
- **Nunca mude os UUIDs** dos manifests nem os IDs de itens/entidades já entregues.
- O RP substitui o `player.entity.json` do jogo (pose de mira em 3ª pessoa). Até a v1.6.3 isso era um pack separado (`POSE_RP`), opcional; na v1.6.4 virou parte do RP, porque eram **dois** resource packs para ativar no mundo e o Afonso queria um só. Consequências a lembrar:
  - **o `min_engine_version` do RP fica em [1,21,90]**, nunca [1,26,0]: o `format_version` do arquivo é 1.26.0, e num jogo anterior o jogo ignora o arquivo e cai no fallback `terceira_baixo` (perde só a pose). Com min_engine 1.26, o add-on **inteiro** ficaria incompatível e as armas sumiriam;
  - qualquer outro pack que mexa no jogador (skin 3D, animação) conflita com o nosso, e agora não dá para desligar só a pose.
- Não copie arquivos de outros add-ons (o Aplok Guns é CC BY-NC-ND). Estudar a técnica pode; reutilizar modelo/textura/som, não.
- Celular primeiro. Aparelhos de referência: **Redmi Note 8** (o mais fraco; o desempenho se mede por ele) e Galaxy S24.
  - arma ou armadura: **sem teto fixo de cubos**. Use quantos o realismo pedir (a M4A4 da v1.4 tem ~150). Em 1ª pessoa só uma arma é desenhada por vez;
  - criatura ou veículo: até ~150 cubos por enquanto (podem existir várias no mundo ao mesmo tempo);
  - atlas de até 1024 px;
  - poucas partículas por evento;
  - nada de `runInterval` pesado por entidade.
- Ao terminar uma mudança que o João vai ver, adicione uma linha no `CHANGELOG.md` e atualize a seção **Estado** abaixo.
- Commits: mensagens em português, curtas.

## Como os modelos funcionam (ler antes de mexer em pose/posição)

- Unidade de modelagem = **1/64 de bloco**; o osso raiz `arma` tem `scale 0.25` na animação. Eixos Bedrock da arma: **+Z = cano**, +Y = cima, **+X = lado direito da arma**. Coordenadas em `modelos.py` são relativas ao **punho** (`info["grip"]`), e o gerador soma o pivô [0,24,0].
- Ossos: `arma` (raiz, `binding: q.item_slot_to_bone_name(c.item_slot)`, pivô [0,24,0]) → `corpo`, `maos` (luvas/mangas, escondidas fora da 1ª pessoa) e `flash` (clarão, material `entity_beam_additive`, aparece com `v.mostra_clarao`).
- Texturas: atlas por face (cada face de cada cubo tem seu retângulo), **4 texels por unidade**; a geometria declara `texture_width = largura_px / 4`. Todas as medidas de cubo devem ser múltiplos de 0.25. Estilo **limpo com luz pintada** (sem ruído fino, que pixela de perto; degradê, reflexo e quinas claras em `acabamento()`) e paleta em **cinzas médios** (`METAIS`/`POLIMEROS` em `geometria.py`, base ~#40–#60): arma preta real, sob a luz chapada do Minecraft, precisa disso para mostrar volume. A pintura é **3D**:
  - cada texel sabe seu ponto na arma, então manchas e veio continuam entre faces e peças;
  - a oclusão ambiente sai da geometria (SDF dos cubos);
  - o desgaste fica só em quina exposta.

  Material novo = ramo em `base_3d()` de `geometria.py`.
- **Convenção de rotação** (verificada no código do Blockbench, `js/formats/bedrock/*`): converter Bedrock → espaço "bb" (destro) com `x_bb = -x`; rotação Bedrock `[rx, ry, rz]` vira `R = Rz(rz)·Ry(-ry)·Rx(-rx)`. Ponto no osso: `p' = P + T + R·s·(p - P)`. Ver `tools/nucleo/bt.py` (`rot_bb`, `euler_from_bb`). Ossos com `binding` ganham um **offset de -24 em Y** (por isso o pivô 24).
- **1ª pessoa**: usa o referencial do preview de attachable do Blockbench (`attachable_preview.js`): o modelo vinculado fica em `(-20, 21, 0)` com rotação ZYX `(-95°, 45°, 115°)` (= braço vanilla `[95,-45,115]`), câmera do Blockbench em `(0,19,-40)` olhando para `(0,16,0)`, FOV ~57°. **Essa câmera não é a do jogo**: `CALIB` em `attachables.py` (calibrada com print do celular) aproxima a câmera ~5,4 unidades e usa FOV vertical 67,5°. Sem isso, a Glock ficava atrás do plano da câmera e sumia. Agachado, a câmera do jogo ainda se desloca em relação ao braço (`AGACHADO`, medido com prints). `CALIB` + `AGACHADO` foram confirmados com prints na v1.3.1 e valem para qualquer arma. Em `attachables.py`, `first_person()` resolve a rotação/posição do osso para colocar o punho em `PLACE[...]["grip"]` = (direita, cima, profundidade) no espaço da câmera, com `yaw`/`pitch`/`roll` em graus. No jogo o braço direito fica oculto em 1ª pessoa quando segura item, por isso as mãos vêm dentro do modelo. A animação desconta os balanços vanilla de 1ª pessoa (`compensacao_bob()`; ver Armadilhas).
- **Mira (ADS)**:
  - agachar = mira completa;
  - atirar em pé puxa a arma parte do caminho ao centro (`PLACE[...]["atirando"]`) e ela fica lá 0,5 s depois de soltar;
  - `pose_mira()` põe a `visada` do modelo no eixo da câmera, com o ponto de trás a `olho` do olho;
  - `caminho_mira()` gera quadros-chave no espaço da câmera, percorridos com `anim_time_update: "v.ads"`;
  - recuo só para trás, no eixo da câmera, para não tirar a mira;
  - pistola anima 1 tiro por toque, fuzil cicla enquanto segura;
  - alça perto do olho (peep da M4) fica no osso `alca` e se recolhe na mira, porque senão tapa o centro da tela;
  - arma com luneta (`info["luneta"]`): na mira completa a **arma some** e entra o osso `luneta`, um painel preto com furo circular e retículo, como nos FPS. Ele é dimensionado para `FOV_MIRA`, então **depende do zoom funcionar**;
  - zoom via `/camera fov_set` no script;
  - luneta futura = mesma coisa, com `visada` no eixo do tubo e `fov` menor.

  **A linha de mira tem que passar bem acima de tudo entre o olho e a alça** (na AK, a tampa escondia o entalhe). Detalhes em `docs/modelos-e-pose.md`.
- **3ª pessoa**: o `player.entity.json` do RP põe o braço em `[-90 + pitch, -5.73, 0]` e o attachable lê `c.owning_entity->v.joao_mira` (variável pública) para escolher `terceira_mira`; se o jogo ignorar esse arquivo, usa `terceira_baixo` (braço ~[-18,0,0]).
- O renderizador de prévias (`geometria.render`) ordena por **pedaço** de face e mostra a face certa (até a v1.3.1 errava de perto e mostrava o verso das faces). Desde a v1.3.2, as prévias de mira reproduzem os prints do jogo. Ele não tem a iluminação do jogo, então contraste e brilho só se julgam no aparelho. Peça ao Afonso um print ou vídeo do jogo quando mexer em posição.

Detalhamento (helpers de `modelos.py`, atlas, pintura 3D, recuo, clarão, mira e `pre_animation`): `docs/modelos-e-pose.md`. Observação: espessuras finas de detalhes salientes (rebites 0.15, janela da Glock 0.1) fogem da regra dos 0.25 e funcionam porque o atlas tem margem.

## Pronto quando

- [ ] `python tools/build.py --gerar` roda sem erro e a checagem passa (JSON + `npm run check`).
- [ ] Você **abriu** as prévias afetadas e elas estão no padrão de realismo descrito acima.
- [ ] Nenhum ID ou UUID existente mudou; versão subida, se for para entregar.
- [ ] `CHANGELOG.md` e a seção **Estado** atualizados.
- [ ] Commit com mensagem curta em português.

## Armadilhas do Bedrock

- **Erros de Molang e JSON costumam ser silenciosos**: o item ou a entidade some ou fica invisível. Peça ao Afonso para ativar o **Content Log** nas configurações de Criador do jogo.
- Em `@minecraft/server` 2.x, callbacks `beforeEvents` são somente leitura. Mudanças de mundo vão em `afterEvents` ou `system.run`. Componentes customizados só podem ser registrados em `system.beforeEvents.startup`.
- **Item sem componente de uso não "usa".** `minecraft:use_modifiers` não serve só para segurar no celular: sem ele (ou outro componente de uso), `itemUse` **não dispara** e o item parece inerte — foi o que aconteceu com o Ovo de Velociraptor na v1.9.0, com o item, a tag e a entidade todos corretos. Não remova isso das armas, e dê a todo item que faz algo ao ser usado.
- **`itemUseOn` não existe mais na API 2.0**: virou `world.afterEvents.playerInteractWithBlock`. Tocar um **bloco** com um item na mão não passa por `itemUse`, e mirar o chão é o gesto natural no celular — então item que se usa no chão precisa dos **dois** eventos (`aoUsar` + `aoUsarEmBloco` no `main.js`). Os dois podem disparar no mesmo tick, então quem atende os dois precisa de guarda por tick, senão um toque gasta dois itens. Filtre `isFirstEvent`: segurar o toque repete o evento.
- Em 1ª pessoa, o braço do jogador some quando ele segura um item. Por isso as mãos fazem parte do modelo da arma (osso `maos`).
- Importar uma versão nova (mesmo UUID, versão maior) **não substitui** a antiga no aparelho: o Minecraft guarda as duas. Por isso o `--versao` põe `vX.Y.Z` no **nome** dos packs, logo depois de "Armas do João", e o site explica como apagar a antiga em Configurações > Armazenamento. Não tente resolver trocando UUID: isso desliga o pack dos mundos do João.
- O jogo aplica **balanços no item em 1ª pessoa** (`player_firstperson.animation.json`):
  - respiração de ±0,5 un. em 8 s, no `rightitem`;
  - caminhada com `hand_bob`, no `rightarm`.

  Na mira, isso parece a arma "subindo sozinha". `compensacao_bob()` desconta os dois. Supõe o "balanço da visão" ligado, porque `v.bob_animation` não é legível.
- No attachable, `q.*` são as queries do **jogador** e `v.*` são variáveis do próprio attachable, que persistem entre quadros. Variável do jogador só é legível se for pública (`c.owning_entity->v.joao_mira`).
- **Os três ângulos do `CALIB` não saem de ajuste por silhueta.** A silhueta de um fuzil é alongada e quase não muda quando a câmera gira um grau, então o otimizador da v1.1.1 pôs ruído nos três: roll 1,963° (zerado na v1.6.3) e yaw 1,132° (medido em 0,387 na v1.6.5). Menos de um grau some nas miras de ferro, mas o retículo da luneta atravessa a tela e denuncia. Meça com `tools/dominios/armas/medir_mira.py`, que lê o retículo da AWP (linhas de 1 px, ~0,07°) e confere nas outras armas. **A prévia nunca mostra esse tipo de erro**, porque renderiza com a mesma câmera que posiciona a arma — câmera errada dá prévia certa e jogo errado.
- **Erro de ÂNGULO da câmera e erro de POSIÇÃO (`AGACHADO`) parecem a mesma coisa numa arma só.** O de ângulo desvia todas as armas igual; o de posição desvia proporcionalmente a 1/distância do olho, então a AWP (olho 2,0) erraria quase 4x mais que a AK (olho 7,5). Na v1.6.2 os dois foram confundidos e o `AGACHADO` absorveu um erro que era de ângulo. Meça sempre com duas armas ou mais.
- **Peça saliente tem de ENTRAR na peça de trás, nunca encostar.** Duas faces no mesmo plano brigam pelo z-buffer e o jogo pisca entre elas; na prévia aparece como serrilha preta na borda. 0,15 de sobreposição resolve. Foi o que os painéis e visores dos blocos do laboratório ensinaram.
- **"Vidro" aqui é opaco.** O material `boca` é cinza quase preto: serve de visor pequeno e não serve de cúpula — numa superfície grande vira um buraco preto. A primeira incubadora tinha uma redoma de vidro e parecia uma caixa fechada. Equipamento de laboratório de verdade é metal com janela, e um **furo** no bloco (moldura de quatro peças) mostra o que está dentro muito melhor que qualquer vidro.
- **Furo em bloco se faz com moldura**, e em todas as camadas: deixar o furo só no tampo não adianta se o gabinete por baixo é um cubo inteiro — ele tapa o fundo e de cima vê-se uma chapa lisa.
- **O referencial de câmera do renderizador de prévias é espelhado** (a direita da tela é −X do espaço bb). Uma câmera nova escrita com a convenção destra passa no teste de visibilidade ao contrário e mostra o objeto **por dentro**: faces de cima escuras, interiores à mostra.
- Rotação no Bedrock **não** é a convenção matemática comum. Use `tools/nucleo/bt.py`; não chute sinais.
- **As prévias não interpretam Molang.** Um osso que só fica certo pela animação (a corda da besta) aparece na prévia do jeito que foi *desenhado*. Por isso `info["ossos"]` tem `repouso`: a pose parada, que as prévias aplicam e que o jogo mostra se a animação falhar. Desenhe sempre uma pose que seja válida sozinha.
- **Projétil de verdade é território pouco documentado.** `minecraft:projectile` em *item* de add-on não funciona (MCPE-170972); o caminho que funciona é entidade + `spawnEntity` + `getComponent("minecraft:projectile").shoot()` pelo script, com `owner` para o acerto ser creditado. O dardo não usa `stick_in_ground` de propósito: com `runtime_identifier: "minecraft:arrow"`, um projétil cravado no chão pode virar uma flecha na mão de quem passa por cima.
- **`runtime_identifier` dá a física do projétil, não a orientação dele.** O renderizador não passa a rotação da entidade para o modelo: sem animação, o dardo fica parado no eixo do mundo e voa de lado para toda direção que não seja o norte (v1.7.1). Duas regras, as duas copiadas do `arrow` vanilla (a lógica, não o arquivo):
  - a geometria aponta para **-Z**, que é a frente de qualquer entidade no Bedrock (a flecha tem as penas em +Z);
  - o osso raiz leva uma animação com `rotation: ["-query.target_x_rotation", "-query.target_y_rotation", 0]`, declarada em `animations` + `scripts.animate` do client entity.

  Se um dia o dardo girar **demais** (duas vezes o ângulo), é porque esse runtime passou a aplicar a rotação também: aí a animação sai. Se continuar preso, troque `target_*` por `body_*`. Nada disso aparece na prévia — ela desenha o modelo, não o voo.

## Estado (v1.9.2)

Histórico completo no `CHANGELOG.md`. Resumo do que importa para continuar:

- **Confirmado no celular:**
  - tiro, rastro, munição;
  - armas 3D no quadril;
  - mira agachada centralizada (prints da v1.2.1/v1.3.1);
  - câmera calibrada (`CALIB` + `AGACHADO`, encaixe ~0 na v1.3.1);
  - `v.ads` persiste e `q.is_sneaking` funciona no attachable.
- **Entregue e ainda não visto no aparelho:**
  - **todo o laboratório da v1.8.0** (fóssil ao minerar, extrator, incubadora, os quatro itens). Os blocos são os primeiros do projeto: se um deles aparecer como o quadriculado roxo ou sumir, é o JSON do bloco ou o `terrain_texture.json`;
  - **o Velociraptor da v1.9.0** (e o ovo que o choca, que só passou a reagir ao toque na v1.9.1): 20 ossos, 85 cubos, 1,96 x 3,93 blocos, atlas 512. É a primeira entidade com comportamento e o primeiro esqueleto articulado (5 níveis). Estreia a família `joao:sedavel` — e o `minecraft:is_sleeping` do grupo do sono existe **para o cliente**, porque o script marca tag de runtime e Molang não lê tag;
  - **tudo da v1.7.0 e da v1.7.1** (besta, dardo, sono) — só o voo do dardo foi visto, e estava de lado;
  - a mira no centro e a animação presa ao tiro real (v1.6.5);
  - as cinco armas no padrão novo, peça por peça: M4A4 com 142 cubos, AK com 88, Glock com 55, AWP com 89 + 74 do painel da luneta, besta com 130;
  - atlas 4x menor em todas as armas (v1.6.0); paleta clara e estilo limpo (v1.4.x); pintura 3D (v1.3.0).
- **A confirmar, em ordem de risco:**
  - **o dardo em voo.** É a primeira entidade do add-on. Na v1.7.0 ele voou **de lado**: faltava apontar a geometria para -Z e animar a rotação (ver Armadilhas). Corrigido na v1.7.1, **ainda sem ver no jogo**. Se ainda sair torto, o vídeo dirá qual dos dois casos é: preso no eixo do mundo (animação ignorada) ou girando o dobro (rotação aplicada duas vezes);
  - **a corda da besta.** Ela gira e encurta por Molang (`math.lerp` com `v.ciclo`). Se o Molang falhar, ela fica parada na pose armada, que é a de repouso — repare se ela se mexe ao atirar;
  - **a partícula `joao:sono`** (o "zZz"): JSON de partícula é novo no projeto e erro de partícula é silencioso;
  - **se o zoom funciona com Cheats ligados.** O `/camera fov_set` exige cheats e só aceita FOV de 30 a 110. Pendência desde a v1.6.0;
  - **se o zoom amplia também a arma.** Se um print mostrar a vinheta sumindo ao agachar, o painel precisa ser dimensionado por `FOV_ZOOM`;
  - se a compensação de balanço faz a arma balançar com o "balanço da visão" desligado;
  - como fica no PC (16:9).
- **Pendências e ideias:**
  - **dardo cravado no bicho**: não existe nativamente. Quando os dinos chegarem, vira um osso no modelo deles, que é como os add-ons de referência fazem;
  - migrar as armas para `minecraft:tags` + componente `joao:arma_fogo` (ver "Estado atual × alvo");
  - mãos visíveis segurando a Glock na mira;
  - som de ferrolho da AWP entre os tiros;
  - marcações gravadas (seletor, inscrições);
  - amostras de material geradas por IA (Nano Banana) lidas pela `paint()`;
  - coice de câmera no tiro (`camerashake`), se o João sentir falta.
- **Próximos dinossauros**: uma linha em `tools/dominios/dinossauros/especies.py` mais o módulo do modelo. Tiranossauro e Triceratops são os pedidos óbvios; híbridos (Indominus) entram pelo campo `genes`, que a incubadora já sabe ler.
- **O que o João pode pedir:** mais dinossauros (Jurassic World é o favorito dele) — a besta já é a metade do caminho, porque o jeito de fazer dormir está pronto e esperando a família `joao:sedavel`. Também: recarga com animação, mais armas, veículos.

## Referências

- `docs/modelos-e-pose.md`: referência técnica detalhada de modelo, textura e pose.
- `CHANGELOG.md`: histórico de versões.
- `docs/nova-arma.md`: passo a passo de arma nova, valores de referência e regras de mira.
- Comandos do Claude Code: ainda não existem (não há `.claude/commands/`). O equivalente está em:
  - `docs/nova-arma.md`;
  - Fluxo de trabalho, para lançar versão;
  - `tools/dominios/armas/ajuste.py`, para posição.
- Documentação: https://learn.microsoft.com/minecraft/creator/ · https://wiki.bedrock.dev · arquivos vanilla em https://github.com/Mojang/bedrock-samples
