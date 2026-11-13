# Changelog

Formato: versão — data — o que mudou. Marque **[testado no celular]** quando o Afonso confirmar no aparelho do João.

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
