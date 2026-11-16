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
- Hoje existem 3 armas: Glock, AK-47 e M4A4. Os nomes dos packs nos manifests ainda são "Armas do João". Renomear o nome exibido é permitido; **os UUIDs nunca mudam**.
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
python tools/ajuste.py              # resolve PLACE (posição em 1ª pessoa) a partir de alvos na tela
python tools/calibrar.py print.png ...  # recalibra a câmera real (CALIB) a partir de um print da M4A4
python tools/medir_mira.py awp=a.png glock=b.png ...  # mede a mira em prints do jogo e corrige os ângulos do CALIB
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

- **Editado à mão**: `packs/BP/**` (itens, receitas, `scripts/main.js`), `packs/RP/manifest.json`, `packs/RP/textures/item_texture.json`, `packs/RP/sounds/sound_definitions.json`, tudo em `tools/`.
- **Gerado por `tools/gerar.py` (não editar direto)**: `packs/RP/models/entity/joao/*`, `packs/RP/textures/entity/joao/*`, `packs/RP/attachables/*`, `packs/RP/animations/joao_armas.animation.json`, `packs/RP/render_controllers/*`, `packs/RP/textures/items/{glock,ak47,m4a4}.png`.
- Site de downloads: modelo em `tools/site/modelo.html` (editado à mão), gerador `tools/site_joao.py`; a pasta `site/` é gerada (não editar).
- Gerado por `sons.py` → `packs/RP/sounds/joao/*.ogg`; `municao.py` → ícones de munição; `icone.py` → `pack_icon.png`; `pose.py` → `packs/RP/entity/player.entity.json` e `animations/joao_mira.animation.json`.

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
  armas/
    index.js              # registra o componente joao:arma_fogo; tiro, rajada, munição
  dinossauros/            # comportamento que o JSON não cobre (ex.: rugido, montaria especial)
  veiculos/               # controle, física, combustível
  armaduras/              # efeitos de conjunto completo etc.
```

- Cada domínio exporta uma função `registrar(contexto)` chamada pelo `main.js`. Domínios **não importam uns aos outros**; o que for compartilhado vai para `comum/`.
- Um único `system.runInterval` por domínio, no máximo. Prefira eventos a polling.
- `npm run check` precisa cobrir todos os arquivos (`jsconfig.json` já inclui `packs/BP/scripts/**/*.js`).

### Geradores modulares (`tools/`)

Mantém-se a geração procedural em Python (`build.py --gerar`) com **prévias automáticas em `previews/`** para validação visual antes do celular. A estrutura evolui para domínios:

```
tools/
  build.py                # orquestra: --gerar roda todos os domínios registrados
  nucleo/                 # compartilhado: bt.py (rotação), atlas/pintura/geometria, renderizador de prévias, sons base
  dominios/
    armas/                # modelos + attachable + pose 1ª/3ª pessoa (o que hoje é modelos.py/gerar.py)
    armaduras/            # attachable em ossos do jogador (cabeça, corpo, pernas)
    dinossauros/          # entity completa: geometria com ossos articulados, animações (andar, correr, atacar, idle), controllers, spawn
    animais/              # idem dinossauros
    veiculos/             # entity montável: geometria, assentos, rodas/hélices animadas
```

- **Dois tipos de saída no RP**:
  - armas e armaduras = **attachable** (segue o osso do jogador);
  - dinossauros, animais e veículos = **client entity** completa (`entity/`, `animations/`, `animation_controllers/`, `render_controllers/`), com o par no BP (`entities/`).
- Cada domínio expõe a mesma interface para o `build.py`, por exemplo `gerar(rp, bp, previews)`. Ele escreve só nas suas próprias pastas (`.../joao/<dominio>/...`) e produz prévias com prefixo do domínio (`previews/<dominio>_*.png`).
- Entidades precisam de prévias de **pose e animação** (quadros-chave lado a lado), não só da pose estática.

### Estado atual × alvo (migração)

- **Hoje** (v1.6.5): só existe o domínio armas. O `main.js` ainda guarda o objeto `ARMAS` por ID, e os geradores estão em arquivos únicos (`modelos.py`, `gerar.py`, `geometria.py`, `sons.py`).
- **Quando**: migre para a estrutura acima **ao entrar a segunda categoria** (provavelmente o primeiro dinossauro), ou antes, se uma mudança em armas já pedir isso.
- **Como**: faça a migração em commit próprio, **sem mudar comportamento**. Verifique que `--gerar` produz arquivos idênticos aos de antes (exceto `.ogg`) e que `npm run check` passa. Só então comece o conteúdo novo.
- Na migração das armas para `joao:arma_fogo` + tags, **mantenha os IDs dos itens** (`joao:glock`, `joao:ak47`, `joao:m4a4`, munições). Mudar ID apaga os itens do inventário do João.

## Convenções

- Namespace `joao:`. IDs: `joao:glock`, `joao:ak47`, `joao:m4a4`, `joao:municao_pistola`, `joao:municao_fuzil`. Sons `joao.*`, geometrias `geometry.joao.*`, animações `animation.joao.*`.
- Script API `@minecraft/server` **2.0.0** (jogo ≥ 1.21.90). `min_engine_version` [1,21,90] no BP e no RP.
- Tiro = raycast instantâneo (`getBlockFromRay` + `getEntitiesFromRay`) a partir da cabeça; dano via `applyDamage` creditado ao jogador. Rajada: `itemStartUse`/`itemStopUse` + `runInterval`; o `itemUse` sempre dá 1 tiro (fallback se a rajada não funcionar no celular). Itens têm `minecraft:use_modifiers` (use_duration 3600) para permitir segurar.
- Para adicionar uma arma, siga **`docs/nova-arma.md`**. Ele traz:
  - os 9 lugares onde a lista de armas se repete;
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
- **Convenção de rotação** (verificada no código do Blockbench, `js/formats/bedrock/*`): converter Bedrock → espaço "bb" (destro) com `x_bb = -x`; rotação Bedrock `[rx, ry, rz]` vira `R = Rz(rz)·Ry(-ry)·Rx(-rx)`. Ponto no osso: `p' = P + T + R·s·(p - P)`. Ver `tools/bt.py` (`rot_bb`, `euler_from_bb`). Ossos com `binding` ganham um **offset de -24 em Y** (por isso o pivô 24).
- **1ª pessoa**: usa o referencial do preview de attachable do Blockbench (`attachable_preview.js`): o modelo vinculado fica em `(-20, 21, 0)` com rotação ZYX `(-95°, 45°, 115°)` (= braço vanilla `[95,-45,115]`), câmera do Blockbench em `(0,19,-40)` olhando para `(0,16,0)`, FOV ~57°. **Essa câmera não é a do jogo**: `CALIB` em `gerar.py` (calibrada com print do celular) aproxima a câmera ~5,4 unidades e usa FOV vertical 67,5°. Sem isso, a Glock ficava atrás do plano da câmera e sumia. Agachado, a câmera do jogo ainda se desloca em relação ao braço (`AGACHADO`, medido com prints). `CALIB` + `AGACHADO` foram confirmados com prints na v1.3.1 e valem para qualquer arma. Em `gerar.py`, `first_person()` resolve a rotação/posição do osso para colocar o punho em `PLACE[...]["grip"]` = (direita, cima, profundidade) no espaço da câmera, com `yaw`/`pitch`/`roll` em graus. No jogo o braço direito fica oculto em 1ª pessoa quando segura item, por isso as mãos vêm dentro do modelo. A animação desconta os balanços vanilla de 1ª pessoa (`compensacao_bob()`; ver Armadilhas).
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
- No celular, "segurar para usar" só funciona porque os itens têm `minecraft:use_modifiers`. Não remova isso das armas.
- Em 1ª pessoa, o braço do jogador some quando ele segura um item. Por isso as mãos fazem parte do modelo da arma (osso `maos`).
- Importar uma versão nova (mesmo UUID, versão maior) **não substitui** a antiga no aparelho: o Minecraft guarda as duas. Por isso o `--versao` põe `vX.Y.Z` no **nome** dos packs, logo depois de "Armas do João", e o site explica como apagar a antiga em Configurações > Armazenamento. Não tente resolver trocando UUID: isso desliga o pack dos mundos do João.
- O jogo aplica **balanços no item em 1ª pessoa** (`player_firstperson.animation.json`):
  - respiração de ±0,5 un. em 8 s, no `rightitem`;
  - caminhada com `hand_bob`, no `rightarm`.

  Na mira, isso parece a arma "subindo sozinha". `compensacao_bob()` desconta os dois. Supõe o "balanço da visão" ligado, porque `v.bob_animation` não é legível.
- No attachable, `q.*` são as queries do **jogador** e `v.*` são variáveis do próprio attachable, que persistem entre quadros. Variável do jogador só é legível se for pública (`c.owning_entity->v.joao_mira`).
- **Os três ângulos do `CALIB` não saem de ajuste por silhueta.** A silhueta de um fuzil é alongada e quase não muda quando a câmera gira um grau, então o otimizador da v1.1.1 pôs ruído nos três: roll 1,963° (zerado na v1.6.3) e yaw 1,132° (medido em 0,387 na v1.6.5). Menos de um grau some nas miras de ferro, mas o retículo da luneta atravessa a tela e denuncia. Meça com `tools/medir_mira.py`, que lê o retículo da AWP (linhas de 1 px, ~0,07°) e confere nas outras armas. **A prévia nunca mostra esse tipo de erro**, porque renderiza com a mesma câmera que posiciona a arma — câmera errada dá prévia certa e jogo errado.
- **Erro de ÂNGULO da câmera e erro de POSIÇÃO (`AGACHADO`) parecem a mesma coisa numa arma só.** O de ângulo desvia todas as armas igual; o de posição desvia proporcionalmente a 1/distância do olho, então a AWP (olho 2,0) erraria quase 4x mais que a AK (olho 7,5). Na v1.6.2 os dois foram confundidos e o `AGACHADO` absorveu um erro que era de ângulo. Meça sempre com duas armas ou mais.
- Rotação no Bedrock **não** é a convenção matemática comum. Use `tools/bt.py`; não chute sinais.

## Estado (v1.6.5)

Histórico completo no `CHANGELOG.md`. Resumo do que importa para continuar:

- **Confirmado no celular:**
  - tiro, rastro, munição;
  - armas 3D no quadril;
  - mira agachada centralizada (prints da v1.2.1/v1.3.1);
  - câmera calibrada (`CALIB` + `AGACHADO`, encaixe ~0 na v1.3.1);
  - `v.ads` persiste e `q.is_sneaking` funciona no attachable.
- **Entregue e ainda não visto no aparelho:**
  - as quatro armas no padrão novo, peça por peça: M4A4 com 142 cubos (v1.4.0), AK com 88, Glock com 55 (v1.5.0) e AWP com 89 + 74 do painel da luneta (v1.6.0);
  - AWP: sniper de ferrolho com mira estilo CS (painel preto com furo circular), dano 30, munição própria. Os vídeos confirmaram o painel, o furo e o retículo no jogo; a v1.6.2 centralizou o retículo;
  - atlas 4x menor em todas as armas (empacotamento por altura, v1.6.0);
  - paleta clara e estilo limpo com luz pintada (v1.4.0/v1.4.1);
  - alça da M4 que se recolhe na mira (v1.4.2);
  - pintura 3D das texturas (v1.3.0): julgar contraste no jogo;
  - puxão ao atirar em pé (v1.3.1);
  - AK com alça e massa mais altas e Glock mais perto na mira (v1.3.2).

  Pedir prints mirando (AK e Glock), em pé e atirando em pé.
- **A confirmar:**
  - **se o zoom funciona com Cheats ligados.** O `/camera fov_set` exige cheats e só aceita FOV de 30 a 110 (a v1.6.0 pedia 18 e era recusada em silêncio — foi o que apareceu no vídeo da AWP). `camera.setFov()` não existe na API 2.0.0, então o comando é o único caminho hoje;
  - **se o zoom amplia também a arma.** O painel da luneta é dimensionado pelo FOV normal (`VFOV`), supondo que a arma em 1ª pessoa tem FOV próprio. Se um print mostrar a vinheta sumindo ao agachar, o zoom afeta a arma e o painel precisa ser dimensionado por `FOV_ZOOM`;
  - **se o retículo da AWP ficou reto e no centro.** O giro foi resolvido na v1.6.3 (os prints da v1.6.4 mediram 0,05°, contra ~2° antes). O centro foi corrigido na v1.6.5, com os ângulos do `CALIB` medidos em 5 prints (`tools/medir_mira.py`): faltava 1,2° à direita e 1,1° acima. O tiro sai sempre do centro da tela, então retículo fora do lugar = tiro fora da mira;
  - **se a arma parou de animar sem munição** (v1.6.5) e se a rajada continua lisa: a animação agora segue o cooldown `joao_tiro` que o script liga a cada tiro, em vez do dedo na tela;
  - se a compensação de balanço faz a arma balançar com o "balanço da visão" desligado;
  - como fica no PC (16:9).
- **Pendências e ideias:**
  - mãos visíveis segurando a Glock na mira (hoje parece uma coluna solta);
  - som de ferrolho da AWP entre os tiros (hoje só o estampido);
  - marcações gravadas (seletor, inscrições);
  - amostras de material geradas por IA (Nano Banana) lidas pela `paint()`;
  - coice de câmera no tiro (`camerashake`), se o João sentir falta;
  - site ainda não publicado na Vercel (`--publicar`, 1ª vez `npx vercel login`).
- **O que o João pode pedir:** fuzil com luneta (já previsto na mira), recarga com animação, mais armas, dinossauros (Jurassic World é o favorito dele).

## Referências

- `docs/modelos-e-pose.md`: referência técnica detalhada de modelo, textura e pose.
- `CHANGELOG.md`: histórico de versões.
- `docs/nova-arma.md`: passo a passo de arma nova, valores de referência e regras de mira.
- Comandos do Claude Code: ainda não existem (não há `.claude/commands/`). O equivalente está em:
  - `docs/nova-arma.md`;
  - Fluxo de trabalho, para lançar versão;
  - `tools/ajuste.py`, para posição.
- Documentação: https://learn.microsoft.com/minecraft/creator/ · https://wiki.bedrock.dev · arquivos vanilla em https://github.com/Mojang/bedrock-samples
