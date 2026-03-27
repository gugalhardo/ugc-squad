# Squad UGC Creator — PRD

## Proposito

Transformar uma ideia de video UGC em roteiro + direcao de cena + JSONs VEO3 + copy, com aprovacao humana em cada etapa. O usuario fornece uma foto base do personagem.

## Fluxo (Modo Manual)

Roteirista -> Diretor -> Produtor -> Copywriter

O usuario fornece a foto base. Nao ha geracao de fotos ou videos via API. O Produtor gera apenas JSONs VEO3.

## Agentes

| # | Agente (arquivo) | Papel | Tools | Model | MaxTurns |
|---|-------------------|-------|-------|-------|----------|
| 1 | `ugc-scriptwriter` | Script puro: o que sera falado/escrito | Read, Write | opus | 20 |
| 2 | `ugc-director` | Direcao de cena (atuacao, expressao, gesto, tom) | Read, Write | sonnet | 20 |
| 3 | `ugc-producer` | Monta JSONs VEO3 (sem geracao de video) | Read, Write | sonnet | 50 |
| 4 | `util-copywriter` | Legenda + ad copy para Meta Ads | Read, Write | opus | 25 |

Coordenador: `ugc-coordinator` (sonnet, 100 turns)

## Input do Usuario

- **Marca/produto** (obrigatorio) — ex: "minha-marca"
- **Nome do anuncio** (obrigatorio) — slug para nome da pasta
- **Descricao da ideia** (obrigatorio)
- **Dor/problema ou angulo** (obrigatorio)
- **Foto base do personagem** (obrigatorio)
- Tom de voz desejado (opcional)

## Contexto por Agente

| Agente | Recebe |
|--------|--------|
| Roteirista | Input original (ideia, dor, tom, ref visual) |
| Diretor | Input original + roteiro aprovado + foto base |
| Produtor | Script completo + direcao de cena + foto base |
| Copywriter | Input original + roteiro + briefing do coordenador |

## Convencao de Output (Local)

```
outputs/{brand}/ugc_{DD-MM-AA}_AD00X-{slug}/
├── 01-script/        # hooks.md + script.md
├── 02-direction/     # direction.md
├── 03-photography/   # base-photo.{ext} (foto do usuario)
├── 04-production/    # scene-01.json ... scene-08.json (JSONs VEO3)
└── 05-copy/          # caption.md + ad-copy.md
```

## Knowledge Docs

- **Squad**: `knowledge/squads/ugc-creator/*` (ugc-best-practices, video-formats, reference-styles)
- **Agente**: `knowledge/agents/{agente}/*`
- **Brand**: `knowledge/brands/{marca}/*`

## Fluxo Detalhado

### Roteirista
- Etapa 1: Gera 10 opcoes de gancho/headline -> humano escolhe
- Etapa 2: Escreve roteiro completo (5-8 cenas, ~140 chars cada = 8s por cena)
- Output: hooks.md + script.md

### Diretor
- Analisa foto base do usuario
- Cria direcao de cena em 2 blocos:
  - Bloco Geral: personagem (extraido da foto), ambiente (extraido da foto), arco emocional
  - Bloco por Cena: expressao, gesto, tom de voz, energia
- Output: direction.md

### Produtor
- Monta JSONs VEO3 para todas as cenas (5 blocos: scene/camera/sequence/dialogue/lighting)
- NAO gera videos via API
- Output: scene-01.json ... scene-XX.json

### Copywriter
- Legenda do post + ad copy para Meta Ads (3 variacoes)
- Output: caption.md + ad-copy.md
