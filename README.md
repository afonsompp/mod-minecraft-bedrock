# Armas do João — add-on de Minecraft Bedrock

Add-on feito para o João: **Glock**, **AK-47**, **M4A4** e **AWP** em 3D, com pose de FPS, munição, receitas na bancada e sons próprios.

## Instalar no celular

1. Gere o pacote (veja abaixo) ou pegue o `.mcaddon` mais recente em `dist/`.
2. Abra o arquivo no celular → ele abre no Minecraft e importa sozinho.
3. Nas configurações do mundo → **Pacotes de Comportamento** → ative **Armas do João** (o pacote de recursos vem junto).

Desde a v1.6.4 há **um pacote de recursos só**: a pose de mira em 3ª pessoa virou parte dele. Quem tinha o `POSE_RP` separado instalado pode apagá-lo.

## Como jogar

| Arma | Modo | Dano | Munição |
|---|---|---|---|
| Glock | toque = 1 tiro | 3 corações | Munição de Pistola |
| AK-47 | segure = rajada | 4 corações | Munição de Fuzil |
| M4A4 | segure = rajada | 3,5 corações | Munição de Fuzil |

No criativo a munição é infinita. A munição aparece na tela enquanto você segura a arma.

### Receitas (bancada)

- **Glock**: `F F F` / `_ P F` — F = lingote de ferro, P = pólvora
- **AK-47**: `F F F` / `G P G` / `G _ _` — G = graveto
- **M4A4**: `F F F` / `C P C` / `C _ _` — C = carvão
- **Munição de Pistola** ×16: pepita de ferro + pólvora
- **Munição de Fuzil** ×16: lingote de cobre + pólvora

## Desenvolvimento

Pré-requisitos: Python 3.10+, `ffmpeg` (para os sons) e, opcionalmente, Node.js (checagem do script).

```bash
pip install -r requirements.txt
npm install                         # opcional: checa o script contra a API do Minecraft

python tools/build.py               # valida e gera dist/Armas_do_Joao_vX.Y.Z.mcaddon
python tools/build.py --gerar       # regenera modelos, texturas, ícones e sons (prévias em previews/)
python tools/build.py --versao 1.2.0
python tools/build.py --deploy      # PC com Windows: copia para as pastas de desenvolvimento do jogo
```

### Testar rápido no PC

`--deploy` copia os packs para `development_behavior_packs` / `development_resource_packs` do Minecraft no Windows. Ative-os num mundo de teste:

- mudou só o **script** → digite `/reload` no jogo;
- mudou **modelo, textura, som ou item** → saia e entre de novo no mundo.

### Estrutura

```
packs/
  BP/        comportamento: itens, receitas, scripts/main.js (tiro, munição, rajada)
  RP/        recursos: modelos 3D, texturas, attachables, animações, sons, ícones (quase tudo GERADO)
             inclui entity/player.entity.json: a pose de mira em 3ª pessoa (GERADO por pose.py)
tools/
  build.py      build / versão / deploy
  modelos.py    os cubos de cada arma e das mãos  ← editar aqui para mudar o formato
  geometria.py  pintura das texturas, atlas, exportação da geometria, renderizador de prévias
  gerar.py      monta tudo e calcula a pose em 1ª/3ª pessoa (PLACE = posição na tela)
  ajuste.py     calcula PLACE a partir de onde o cano e a traseira devem aparecer na tela
  sons.py       sintetiza os sons de tiro
  municao.py    ícones das munições
  icone.py      pack_icon.png
  pose.py       pose de mira em 3ª pessoa (reescreve packs/RP/entity/player.entity.json)
  bt.py         matemática de rotação do Bedrock
docs/
  modelos-e-pose.md   referência técnica: unidades, texturas, rotação, pose em 1ª/3ª pessoa
.claude/
  commands/     comandos do Claude Code: /nova-arma, /ajustar-posicao, /lancar-versao
  settings.json permissões pré-aprovadas para build, checagem e git
CLAUDE.md       contexto para o Claude Code
CHANGELOG.md    histórico de versões
```

Arte, modelos e sons são todos originais (gerados por código). O Aplok Guns serviu só como referência de estilo; nenhum arquivo dele foi usado (licença CC BY-NC-ND).
