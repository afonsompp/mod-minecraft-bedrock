# Changelog

Formato: versão — data — o que mudou. Marque **[testado no celular]** quando o Afonso confirmar no aparelho do João.

## 1.9.2 — 2026-11-19
- **Os ovos agora se distinguem de relance.** O Ovo de Velociraptor ficou com a casca verde-oliva e manchas fortes da cor do bicho; o Ovo Sintético continua branco e liso. No hotbar, com 16 pixels, os dois eram o mesmo oval claro — e com mais espécies a cor é o único sinal que o ícone tem.
- Fóssil, DNA ou Ovo Sintético usado longe de uma máquina agora **diz para que serve**, em vez de não reagir: "moa no Extrator de DNA", "leve à Incubadora". Item que não responde parece item quebrado.

## 1.9.1 — 2026-11-19
- Corrigido: **o Ovo de Velociraptor não fazia nada** quando o João clicava com ele na mão. O item estava certo, o bicho estava certo — faltava dizer ao jogo que o ovo é um item que *se usa*. Sem isso o Minecraft trata o toque como "mexer no bloco" e o add-on nunca é avisado. Agora o ovo choca tanto mirando o chão quanto apontando para o ar à frente, e tocar o Extrator ou a Incubadora com o ovo na mão continua mexendo na máquina, como se espera.

## 1.9.0 — 2026-11-18
- **O Velociraptor.** O ovo agora choca: use o Ovo de Velociraptor mirando no chão e nasce um **filhote**, que cresce sozinho. No criativo também dá para pegar o ovo de spawn dele direto.
  - cabeça com **olho de pupila em fenda**, garra em foice no pé, faixa escura no flanco e barriga clara;
  - anda, corre, caça, entra em pânico e **dorme de verdade** quando leva dardo da Besta Tranquilizante — deitado, de olhos fechados, não só parado no lugar. Era isso que a besta prometia desde a v1.7.0;
  - o filhote segue o adulto e aceita carne.
- Agora cada fóssil que você mói pode virar o DNA dele — e, quando houver mais espécies, a surpresa fica maior.

## 1.8.0 — 2026-11-18
- **O laboratório de dinossauros.** O caminho do filme, do osso ao ovo:
  - **cave fundo e você acha Fósseis.** Quebrando pedra, pedregulho, ardósia, cascalho ou argila abaixo do nível 24, de vez em quando sai um. Quanto mais fundo, mais aparecem;
  - o **Extrator de DNA** (ferro, vidro e um bloco de redstone) mói o fóssil e descobre **de qual dinossauro** aquele osso era. Isso é sorteado na hora: dois fósseis iguais podem dar bichos diferentes;
  - a **Incubadora** (ferro, vidro e uma lanterna) recebe o DNA e um **Ovo Sintético** (argila e slime, na bancada) e choca. O ovo fica **à vista no ninho**, embaixo da lâmpada, até você recolher;
  - no fim, você tem um **Ovo de Velociraptor**.
- **Ainda não dá para chocar o ovo** — o Velociraptor em si é a próxima entrega. Por enquanto o ovo é a prova de que o laboratório inteiro funciona, de ponta a ponta.
- Por dentro: acrescentar um dinossauro novo passou a ser **uma linha** num arquivo. Os itens, os ícones, as receitas e a tabela que o jogo lê saem todos dali.

## 1.7.1 — 2026-11-18
- Corrigido: **o dardo voava atravessado**, de lado, em vez de seguir reto na direção do tiro. Faltavam as duas coisas que a flecha do jogo faz e que ninguém vê: o dardo era desenhado apontando para trás, e nada girava o modelo durante o voo — ele ficava parado no eixo do mundo enquanto a trajetória ia para outro lado. Agora a agulha vai na frente e o dardo acompanha a subida e a descida do tiro.

## 1.7.0 — 2026-11-17
- **Besta Tranquilizante.** Arma nova, para pegar bicho vivo em vez de matar:
  - o **dardo voa de verdade**: você vê ele sair da besta, viajar e acertar. É a primeira coisa do add-on que não é tiro instantâneo;
  - **o bicho dorme.** Cada dardo é uma dose; bicho grande precisa de mais de uma (uma dose a cada 10 de vida, até cinco). Cheia a conta, ele para onde está, com um "zZz" em cima da cabeça, e acorda sozinho depois de um tempo. Se você demorar demais entre um dardo e outro, a dose passa e a conta recomeça;
  - a **corda dispara e volta sendo puxada** a cada tiro, e o dardo novo aparece na calha quando ela termina de armar. Um tiro a cada 0,75 s;
  - **luneta de média distância**, com retículo duplex e duas marcas de queda abaixo do centro — o dardo cai um pouco, diferente da bala. O tiro sai sempre do centro da tela;
  - som de **corda e manivela**, não de pólvora. Besta é arma silenciosa.
- **Dardo Tranquilizante**: munição nova, feita na bancada com ferro, pena e olho de aranha fermentado. A besta sai de ferro, palito e corda.
- Isso é a base para os **dinossauros**: o dardo já pergunta se o bicho é do modpack antes de agir, e nos nossos ele vai poder deitar de verdade.

## 1.6.5 — 2026-11-16
- Corrigido: **a mira estava um pouco fora do centro em todas as armas** — o tiro saía um pouco à esquerda do que a alça e a massa mostravam, e na AWP o retículo ficava fora do meio. Faltava pouco mais de um grau, o bastante para errar de longe. A câmera do jogo foi medida de novo, em cinco prints.
- Corrigido: **sem munição, a arma continuava dando coice e soltando clarão** a cada toque, como se estivesse atirando. Agora a animação só acontece quando o tiro sai mesmo, e de quebra o coice do fuzil bate certinho com a cadência dos tiros.

## 1.6.4 — 2026-11-16
- **Um pacote de recursos só.** A pose de mira em 3ª pessoa era um segundo pacote para ativar no mundo; agora vem dentro do pacote principal. Se você tinha o **pose de mira (3ª pessoa)** instalado, pode apagar em Configurações > Armazenamento.
- Corrigido: em 3ª pessoa, o personagem **não apontava a AWP** com os dois braços como faz com os outros fuzis.

## 1.6.3 — 2026-11-16
- Corrigido: **a mira da luneta estava girada ~2°** (a cruz entrava torta na tela). Era um giro que sobrou da calibração da câmera e aparecia em todas as armas, mas só dava para notar no retículo, que atravessa a tela.
- Corrigido: **o clarão do tiro aparecia solto embaixo** quando se atirava pela luneta. Agora ele some junto com a arma.
- O **nome da arma e a munição** não ficam mais plantados no meio da tela: aparecem ao trocar de arma e ao atirar, e somem sozinhos. Mirando, a tela fica limpa.

## 1.6.2 — 2026-11-13
- Corrigido: **o tiro não saía no meio da mira da AWP** e a luneta parecia torta para um lado. O círculo estava 5° à direita e 8° acima do centro da tela, e o tiro sai sempre do centro. Agora o retículo fica no centro e o tiro sai nele.
- A mesma correção deixa a mira das outras três armas um pouco mais certa.

## 1.6.1 — 2026-11-13
- Corrigido: a **mira da AWP aparecia pequena e torta** no canto da tela, em vez de cobrir tudo. Eram duas coisas:
  - o zoom pedia um campo de visão que o jogo não aceita (o mínimo é 30), e era recusado em silêncio;
  - a mira ligava antes de a arma terminar de subir.
- Agora a mira cobre a tela com ou sem zoom. Para ter a ampliação, o mundo precisa estar com **Cheats ligados**; se não estiver, aparece um aviso na tela e a mira funciona sem ampliar.

## 1.6.0 — 2026-11-13
- **AWP**: sniper de ferrolho com luneta, no estilo do CS.
  - **Mira igual à do CS**: a tela fica preta com um círculo grande no meio e o retículo em cruz. A arma some enquanto você está na luneta.
  - Um tiro derruba zumbi, esqueleto e a maioria dos bichos; empurra forte.
  - Ferrolho lento: ~1,2 s entre tiros, um tiro por toque.
  - Sem a luneta o tiro é bem impreciso; mirando, acerta longe.
  - Munição de Sniper nova (ferro + pólvora, 4 por vez), com cartucho próprio.
  - Modelo verde da Accuracy International: cano longo canelado, freio de boca, coronha vazada, carregador reto e luneta com torres de ajuste.
- **Armas carregam mais rápido**: as texturas das quatro armas usam 4x menos memória, com o mesmo visual.

## 1.5.0 — 2026-11-13
- **AK-47 refeita peça por peça** (padrão AKM):
  - tampa com nervuras e botão de trava;
  - alça tangente com cursor de distância;
  - guarda-mãos com abraçadeiras de aço e abaulamento para a mão;
  - bloco de gás em dois níveis;
  - massa com orelhas e ressalto de baioneta;
  - freio de boca inclinado;
  - seletor grande do lado direito, retém do carregador, rebites e pinos;
  - coronha que engrossa para trás, com chapa da soleira e argola;
  - carregador com nervuras e base.
- **Glock refeita peça por peça** (Glock 17):
  - ferrolho chanfrado com serrilhas de trás e da frente, janela de ejeção com o cano aparecendo, extrator e placa traseira;
  - trilho com ranhuras;
  - gatilho com a trava no meio;
  - alavanca de desmontagem, retém do ferrolho e do carregador;
  - empunhadura com ressaltos para os dedos e base do carregador.

## 1.4.2 — 2026-11-13
- M4A4: ao mirar, a **alça traseira se recolhe** e não tapa mais a visão. Mira-se pela massa da frente, com o centro da tela livre. No quadril e em 3ª pessoa ela continua lá.

## 1.4.1 — 2026-11-13
- Texturas **mais limpas e com luz**: saiu o granulado que deixava as armas com aspecto pixelado e sujo. Agora a luz vem pintada:
  - laterais com degradê;
  - faixa de reflexo no metal;
  - quina de cima clara, quina de baixo escura.
- Menos sombra e sujeira entre as peças: deixavam tudo opaco.

## 1.4.0 — 2026-11-13
- **M4A4 refeita com muito mais detalhe:**
  - trilhos Picatinny com dentes em cima, nos lados e embaixo;
  - massa de mira em "A" com orelhas e ressalto de baioneta;
  - alça rebatível com orelhas de proteção;
  - defletor de cartucho, forward assist, tampa da janela com dobradiça;
  - retém do ferrolho e do carregador, pinos, seletor;
  - coronha M4 com alavanca;
  - empunhadura com ressalto para o dedo;
  - carregador com base.
- **Cores mais claras nas três armas:** com a luz do Minecraft, o preto puro virava só silhueta. Agora dá para ver cada face e cada peça.
- Empunhaduras com textura quadriculada, no lugar do pontilhado que parecia chuvisco.

## 1.3.2 — 2026-11-13
- AK-47: a **alça e a massa de mira ficaram mais altas**, como na AK real. Mirando, a tampa da caixa fica abaixo da mira e não esconde mais o entalhe.
- Glock: na mira ela fica **mais perto e maior**, no mesmo padrão do fuzil.

## 1.3.1 — 2026-11-13
- Teste no celular (prints mirando): Glock pequena e distante comparada ao fuzil; na AK, a tampa escondia a alça (corrigido na 1.3.2).
- Atirando em pé, a arma **volta a vir para o meio da tela** (na Glock, um pouco menos, para não tapar a visão). Ela fica no meio por meio segundo depois de soltar o dedo, então tocar várias vezes na Glock não faz a arma ir e voltar.

## 1.3.0 — 2026-11-13
- **Texturas mais realistas**:
  - o veio da madeira e as manchas do metal agora continuam de uma peça para a outra, como numa arma de verdade, em vez de cada lado pintado separado;
  - sujeira e sombra onde as peças se encontram;
  - desgaste irregular só nas quinas que ficam expostas, no lugar do contorno claro em volta de tudo;
  - aço com leve tom azulado e riscos finos;
  - madeira com anéis de crescimento.
- Ícones das armas refeitos (mostravam o lado de dentro das peças).

## 1.2.2 — 2026-11-13
- Corrigido: na mira, a arma **subia sozinha** e saía do alinhamento. O balanço de respiração e o de caminhada do jogo agora são descontados, e o recuo é só para trás, sem levantar a arma.
- Atirar em pé **não move mais a arma** para o centro. Ela fica no lugar, e quem quer mirar agacha.
- Glock: segurar o dedo na tela não fica mais repetindo a animação de tiro sem som e sem bala. É um tiro por toque, como uma pistola de verdade.

## 1.2.1 — 2026-11-10
- Teste no celular (vídeo): mira agachada centralizada, mas a arma subia aos poucos; Glock alta ao atirar em pé e com animação contínua ao segurar (corrigido na 1.2.2).
- Corrigido: na **mira agachada**, a arma ficava colada no rosto e no canto esquerdo da tela, em vez de centralizada com a alça e a massa alinhadas. Agachado, o jogo mexe a câmera; agora a posição de mira compensa isso.

## 1.2.0 — 2026-11-10
- Teste no celular: na mira agachada, a arma ficou grande e para a esquerda (corrigido na 1.2.1).
- **Mira (ADS)**: agachar faz a arma vir para o centro da tela, com a alça e a massa alinhadas, um zoom leve e tiro mais preciso. Atirando sem agachar, a arma sobe parcialmente para o centro. A transição é suave.
- Miras mais realistas: alça com entalhe na Glock e na AK-47, alça com orifício e massa fina na M4A4.
- Base pronta para fuzil com luneta (mesmo sistema, com mais zoom).

## 1.1.1 — 2026-11-10
- Corrigido: a **Glock não aparecia** em 1ª pessoa, e a M4A4 e a AK-47 ficavam gigantes no canto da tela. A posição das armas foi recalculada com a câmera real do jogo, calibrada a partir de um print do celular.

## 1.1.0 — 2026-11-09 **[testado no celular]**
- Armas em **3D**: modelos gerados por código, com texturas realistas (metal com desgaste, madeira com veio, polímero).
- Pose de **FPS** em 1ª pessoa, com mãos de luva; recuo e clarão do cano na rajada.
- Pose em 3ª pessoa: arma na mão apontando para a frente. Pack opcional `POSE_RP` faz o personagem mirar com os dois braços (jogo 1.26+).
- **Sons próprios** de tiro (3 variações por arma) e clique de arma vazia.
- Removidas as chamas que apareciam na frente do jogador ao atirar.
- Ícones novos (armas renderizadas dos modelos, munições realistas).
- Teste no celular: tiros ok; Glock invisível e fuzis grandes demais em 1ª pessoa (corrigido na 1.1.1).

## 1.0.0 — 2026-11-09 **[testado no celular]**
- Glock (semi), AK-47 e M4A4 (automáticas), munição de pistola e de fuzil, receitas na bancada.
- Tiro por raycast com rastro, dano creditado ao jogador, contador de munição na tela.
- Problema encontrado no teste: arma em 2D, gigante e segurada na diagonal (corrigido na 1.1.0).
