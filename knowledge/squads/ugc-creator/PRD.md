# Squad UGC Creator — PRD

## Proposito

Transformar uma ideia de video UGC em video(s) produzido(s) via IA, com aprovacao humana em cada etapa.

## Fluxo

Roteirista -> Diretor -> Fotografo -> Produtor -> Copywriter

**Modo Automatico**: Fluxo completo com geracao de fotos e videos por IA.
**Modo Manual**: Usuario fornece foto base. Pula Fotografo. Produtor gera apenas JSONs VEO3.

## Agentes

| # | Agente (arquivo) | Papel | Tools | Model | MaxTurns |
|---|-------------------|-------|-------|-------|----------|
| 1 | `ugc-scriptwriter` | Script puro: o que sera falado/escrito | Read, Write | opus | 20 |
| 2 | `ugc-director` | Direcao de cena (atuacao, expressao, gesto, tom) | Read, Write | sonnet | 20 |
| 3 | `ugc-photographer` | Gera imagem por cena via API Gemini | Read, Bash, Write | sonnet | 30 |
| 4 | `ugc-producer` | Gera video por cena via API Gemini (VEO3) | Read, Write, Bash | sonnet | 50 |
| 5 | `util-copywriter` | Legenda + ad copy para Meta Ads | Read, Write | opus | 25 |

Coordenador: `ugc-coordinator` (sonnet, 100 turns)

## Input do Usuario

- **Marca/produto** (obrigatorio) — ex: "tailor"
- **Nome do anuncio** (obrigatorio) — slug para nome da pasta
- **Descricao da ideia** (obrigatorio)
- **Dor/problema ou angulo** (obrigatorio)
- Tom de voz desejado
- Referencia visual / foto base (opcional — se enviada, ativa modo manual)

## Contexto por Agente

| Agente | Recebe |
|--------|--------|
| Roteirista | Input original (ideia, dor, tom, ref visual) |
| Diretor | Input original + roteiro aprovado |
| Fotografo | Input original + roteiro visual do diretor (+ ref visual) |
| Produtor | Por cena: script + direcao visual + imagem |
| Copywriter | Input original + roteiro + briefing do coordenador |

## Convencao de Output

```
outputs/{brand}/ugc_{DD-MM-AA}_{slug}/
├── 01-script/        # hooks.md + script.md
├── 02-direction/     # visual-direction.md
├── 03-photography/   # scene-01.png ... scene-08.png
├── 04-production/    # JSONs VEO3 + videos .mp4
└── 05-copy/          # legenda.md + ad-copy.md
```

## Knowledge Docs

- **Global**: `knowledge/global/*`
- **Squad**: `knowledge/squads/ugc-creator/*` (ugc-best-practices, video-formats, reference-styles)
- **Agente**: `knowledge/agents/{agente}/*`
- **Brand**: `knowledge/brands/{marca}/*`

## Fluxo Detalhado

### Roteirista
- Etapa 1: Gera 10 opcoes de gancho/headline -> humano escolhe
- Etapa 2: Escreve roteiro completo (5-8 cenas, ~140 chars cada = 8s por cena)
- Output: hooks.md + script.md

### Diretor
- Cria direcao visual em 2 blocos:
  - Bloco Geral: personagem, ambiente, iluminacao, mood
  - Bloco por Cena: angulo, expressao, movimento, acao, tom de voz, camera
- Output: visual-direction.md

### Fotografo
- Etapa 1: Gera imagem da cena 01 -> humano aprova individualmente
- Etapa 2: Usa cena 01 como referencia, gera cenas 02-08 -> humano aprova lote
- Chama: `python scripts/generate_image.py`

### Produtor
- Para cada cena: monta JSON -> gera video -> humano aprova
- Ajustes simples: resolve sozinho e reenvia
- Chama: `python scripts/generate_video.py`

### Copywriter
- Legenda do post + ad copy para Meta Ads
- Segue style guide de `knowledge/agents/util-copywriter/`

## Scripts Python

- `scripts/generate_image.py` — CLI para gerar imagens via API Gemini
- `scripts/generate_video.py` — CLI para gerar videos via API Gemini (VEO3)
- `scripts/utils/gemini_client.py` — Client reutilizavel
