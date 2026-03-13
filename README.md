# UGC Creator Squad — Claude Agent Squad

Squad de agentes IA para criação de vídeos UGC (User Generated Content) do zero, com aprovação humana em cada etapa. Funciona 100% via [Claude Code](https://claude.ai/code) com o Agent SDK.

---

## O que é

Um pipeline de 5 agentes especializados que transforma uma ideia em vídeo UGC completo:

```
Roteirista → Diretor → Fotógrafo → Produtor → Copywriter
```

Cada agente entrega um output, você aprova (ou pede ajuste), e o próximo agente começa. Fluxo com aprovação humana obrigatória entre todas as etapas.

---

## Dois modos de operação

| Modo | Quando usar | O que acontece |
|------|-------------|----------------|
| **Automático** | Você fornece apenas a ideia | 5 agentes completos: script → direção → fotos (Gemini) → vídeos (VEO3) → copy |
| **Manual** | Você fornece uma foto base do personagem | 4 agentes: script → direção (analisa sua foto) → JSONs VEO3 → copy. Sem geração de foto/vídeo via API. |

---

## Estrutura do projeto

```
ugc-squad/
├── .claude/
│   └── agents/                         # Definições dos agentes (Claude Agent SDK)
│       ├── ugc-coordinator.md          # Orquestrador principal
│       ├── ugc-scriptwriter.md         # Roteirista
│       ├── ugc-director.md             # Diretor de cena
│       ├── ugc-photographer.md         # Fotógrafo (geração de imagens)
│       ├── ugc-producer.md             # Produtor de vídeo
│       └── util-copywriter.md          # Copywriter (legenda + ad copy)
│
├── scripts/
│   ├── generate_image.py               # Gera imagens via Gemini API
│   ├── generate_video.py               # Gera vídeos via VEO3 (Gemini API)
│   ├── save_output.py                  # Salva outputs no Supabase
│   └── utils/
│       ├── gemini_client.py            # Client reutilizável Gemini (imagem + vídeo)
│       └── supabase_client.py          # Client Supabase (banco + storage)
│
├── knowledge/
│   ├── squads/
│   │   └── ugc-creator/                # Conhecimento do squad
│   │       ├── PRD.md                  # Requisitos e fluxo detalhado
│   │       ├── ugc-best-practices.md   # O que funciona em UGC
│   │       ├── video-formats.md        # Specs técnicas de vídeo
│   │       └── reference-styles.md     # Template de estilos visuais por marca
│   ├── agents/
│   │   ├── ugc-scriptwriter/           # Padrões de gancho e estrutura de roteiro
│   │   ├── ugc-director/               # Template de direção de cena
│   │   ├── ugc-photographer/           # Guia de prompt para imagens
│   │   ├── ugc-producer/               # Schema JSON para VEO3
│   │   └── util-copywriter/            # Style guide de copy + guia de carrossel
│   └── brands/
│       └── _example/                   # Template de brand (copie e preencha)
│           ├── product.md
│           ├── audience.md
│           └── angles.md
│
├── supabase/
│   └── migrations/
│       └── 20260310_outputs_schema.sql # Schema do banco de dados
│
├── .env.example                        # Variáveis de ambiente necessárias
├── requirements.txt                    # Dependências Python
└── README.md
```

---

## Pré-requisitos

- [Claude Code](https://claude.ai/code) instalado
- Python 3.10+
- Conta Google com acesso à [Gemini API](https://aistudio.google.com/)
- Projeto [Supabase](https://supabase.com/) (banco de dados + storage)

---

## Setup

### 1. Clone o repositório

```bash
git clone https://github.com/gugalhardo/ugc-squad.git
cd ugc-squad
```

### 2. Instale as dependências Python

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Preencha o `.env` com suas credenciais:

```env
# Gemini (geração de imagem e vídeo)
GOOGLE_API_KEY=sua_chave_aqui

# Supabase (banco + storage)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sua_service_role_key
```

### 4. Configure o banco de dados no Supabase

Execute a migration SQL no seu projeto Supabase:

```bash
# Via Supabase CLI
supabase db push

# Ou cole o conteúdo de supabase/migrations/20260310_outputs_schema.sql
# diretamente no SQL Editor do painel do Supabase
```

Crie também o bucket de storage público chamado `outputs` no painel do Supabase (Storage → New bucket → nome: `outputs`, público: sim).

### 5. Crie a brand da sua empresa

Copie o template e preencha com os dados do seu produto/marca:

```bash
cp -r knowledge/brands/_example knowledge/brands/minha-marca
```

Edite os 3 arquivos:
- `product.md` — produto, oferta, conceito central, tom de voz
- `audience.md` — público-alvo, dores, desejos, linguagem usada
- `angles.md` — ângulos de comunicação mapeados

---

## Como usar

Abra o Claude Code na pasta do projeto e chame o coordinator:

```
@ugc-coordinator cria um vídeo para a marca minha-marca sobre [sua ideia]
```

Ou seja mais específico:

```
@ugc-coordinator
Marca: minha-marca
Nome do anúncio: black-friday-2025
Ideia: mostrar como nosso produto resolve [dor específica]
Dor/problema: [descrição da dor]
Tom de voz: direto, empático, sem exagero
```

### Modo manual (com foto base)

Envie uma foto junto com a descrição:

```
@ugc-coordinator modo manual
[anexe a foto]
Marca: minha-marca
Ideia: [sua ideia]
Dor: [dor a trabalhar]
```

---

## Fluxo detalhado

### Etapa 1 — Roteirista (`ugc-scriptwriter`)

**Modelo:** Claude Opus | **Turns:** 20

1. Lê os docs da marca (`product.md`, `audience.md`, `angles.md`)
2. Gera **10 opções de gancho/headline** → você escolhe um
3. Escreve o **roteiro completo**: 5–8 cenas, ~140–150 chars por cena (8s cada)
4. Salva no Supabase (tipo: `hooks` + `script`)

**Regras críticas:**
- Cada cena: exatamente 140–150 caracteres (8s de vídeo)
- Sem traço (`-` ou `—`) nas falas — causa bug no VEO3
- Linguagem coloquial, frases curtas

---

### Etapa 2 — Diretor (`ugc-director`)

**Modelo:** Claude Sonnet | **Turns:** 20

Recebe o roteiro aprovado e cria a **direção de atuação** (não de câmera):

**Bloco 1 — Personagem e Ambiente** (constante em todas as cenas):
- Gênero, faixa etária, aparência, roupa, acessórios
- Cenário, atmosfera, arco emocional do vídeo

**Bloco 2 — Direção por cena** (varia a cada cena):
- Expressão facial inicial (estado exato de entrada na cena)
- Gesto corporal (simples e natural — ex: "mostra 5 dedos" quando fala "5 erros")
- Tom de voz (1–2 palavras: "firme e direto", "leve e empático")
- Energia (1 palavra: Baixa / Moderada / Alta / Crescente)

> No **modo manual**, o Diretor analisa a foto base enviada e extrai as características reais do personagem e ambiente — sem inventar.

---

### Etapa 3 — Fotógrafo (`ugc-photographer`)

**Modelo:** Claude Sonnet | **Turns:** 30 | *Apenas modo automático*

Gera uma imagem por cena via **Gemini API**:

1. Gera a **Cena 01** → você aprova individualmente
2. Usa a Cena 01 como referência (`--ref`) para manter consistência nas cenas seguintes
3. Gera as demais cenas em lote → aprovação em lote

Cada prompt segue a estrutura de 2 blocos do `image-prompt-guide.md`:
- **Bloco de Cena**: personagem + expressão/gesto da cena + enquadramento (close-up / medium / wide)
- **Bloco Base**: constante — define estilo UGC, câmera de telefone, lighting natural

Imagens salvas no Supabase Storage (path: `{run_id}/media/scene-0X.png`).

---

### Etapa 4 — Produtor (`ugc-producer`)

**Modelo:** Claude Sonnet | **Turns:** 50

**Modo automático:** Para cada cena, monta o JSON VEO3 + gera o vídeo via API.

**Modo manual:** Monta todos os JSONs VEO3 e salva no Supabase (sem gerar vídeo via API — você usa os JSONs para gerar manualmente ou via outra pipeline).

#### Schema JSON VEO3 (5 blocos obrigatórios):

```json
{
  "scene": {
    "description": "Mulher jovem, escritório moderno, iluminação natural..."
  },
  "camera": {
    "framing": "medium shot",
    "angle": "eye level",
    "movement": "static"
  },
  "sequence": [
    {
      "timestamp": "0.0s-4.0s",
      "action": "She raises hand showing five open fingers. She says: 'São cinco erros...'",
      "emotion": "assertive"
    },
    {
      "timestamp": "4.0s-8.0s",
      "action": "She lowers hand, looks directly at camera. She says: '...que todo mundo comete.'",
      "emotion": "direct"
    }
  ],
  "dialogue": {
    "text": "São cinco erros que todo mundo comete.",
    "tone": "assertive and direct",
    "language": "pt-BR"
  },
  "lighting": {
    "type": "natural",
    "source": "window light",
    "mood": "bright and clean"
  }
}
```

Vídeos salvos no Supabase Storage (`{run_id}/media/scene-0X.mp4`).

---

### Etapa 5 — Copywriter (`util-copywriter`)

**Modelo:** Claude Opus | **Turns:** 25

Recebe marca + roteiro aprovado + ângulo e gera:

1. **Legenda do post** (Instagram feed) — narrativa, não descrição
2. **Ad copy para Meta Ads** — headline + texto primário + descrição (3 variações)

Salvo no Supabase (tipos: `caption` + `ad_copy`).

---

## Aprovação humana — 6 opções

Em cada etapa, você escolhe:

```
1. Aprovar — seguir para o próximo passo
2. Pedir ajuste — diga o que quer mudar (pode enviar novas referências)
3. Ajustar manualmente — você edita o output e o agente segue com a versão editada
4. Refazer do zero — o agente gera um output completamente novo
5. Pular etapa — seguir sem o output dessa etapa
6. Parar fluxo — encerrar aqui (outputs até agora ficam salvos)
```

Ciclos de ajuste: ilimitados.

---

## Scripts Python

### `scripts/generate_image.py`

```bash
# Gera imagem e salva no Supabase Storage
python scripts/generate_image.py \
  --prompt "Descrição do personagem e cena" \
  --run-id $RUN_ID \
  --agent ugc-photographer \
  --scene 1
# → retorna URL pública da imagem

# Com imagem de referência (para consistência entre cenas)
python scripts/generate_image.py \
  --prompt "..." \
  --ref /tmp/scene-01.png \
  --run-id $RUN_ID \
  --agent ugc-photographer \
  --scene 2
```

### `scripts/generate_video.py`

```bash
# Gera vídeo a partir de JSON payload + imagem inicial
python scripts/generate_video.py \
  --payload /tmp/scene-01.json \
  --image /tmp/scene-01.png \
  --run-id $RUN_ID \
  --agent ugc-producer \
  --scene 1
# → retorna URL pública do vídeo

# Modo legado (arquivo local)
python scripts/generate_video.py \
  --prompt "Descrição da cena" \
  --output /tmp/video.mp4
```

### `scripts/save_output.py`

```bash
# Criar uma sessão de run
RUN_ID=$(python scripts/save_output.py create-run \
  --brand minha-marca \
  --squad ugc \
  --slug "AD001-nome-do-anuncio")

# Salvar artefato de texto
python scripts/save_output.py save \
  --run-id $RUN_ID \
  --type script \
  --agent ugc-scriptwriter \
  --format md \
  --content "CONTEUDO DO ROTEIRO"

# Salvar artefato de arquivo
python scripts/save_output.py save \
  --run-id $RUN_ID \
  --type veo3_payload \
  --agent ugc-producer \
  --format json \
  --file /tmp/scene-01.json \
  --scene 1

# Finalizar run
python scripts/save_output.py update-status \
  --run-id $RUN_ID \
  --status approved
```

---

## Banco de dados (Supabase)

### Tabelas principais

| Tabela | Descrição |
|--------|-----------|
| `output_runs` | Sessão de execução do squad (brand, squad, slug, status) |
| `output_artifacts` | Artefatos gerados por agente (texto, JSON, URLs de mídia) |

### Tipos de artefato (`type` em `output_artifacts`)

| Tipo | Gerado por | Formato |
|------|-----------|---------|
| `hooks` | ugc-scriptwriter | md |
| `script` | ugc-scriptwriter | md |
| `direction` | ugc-director | md |
| `image` | ugc-photographer | url (Storage) |
| `veo3_payload` | ugc-producer | json |
| `video` | ugc-producer | url (Storage) |
| `caption` | util-copywriter | md |
| `ad_copy` | util-copywriter | md |

---

## Adicionando uma nova marca

```bash
cp -r knowledge/brands/_example knowledge/brands/nome-da-marca
```

Preencha os 3 arquivos:

**`product.md`** — O produto
```markdown
## Produto
Nome: ...
Categoria: ...
Proposta de valor: ...

## Oferta
Preço: ...
CTA principal: ...

## Tom de voz
Direto e empático. Sem exagero. Linguagem de WhatsApp.
```

**`audience.md`** — O público
```markdown
## Perfil
Gênero: ...
Faixa etária: ...
Ocupação: ...

## Dores principais
- ...

## Desejos
- ...

## Como falam
Exemplos de linguagem que o público usa...
```

**`angles.md`** — Ângulos de comunicação
```markdown
## Ângulos mapeados

### 1. [Nome do ângulo]
Descrição...
Exemplo de gancho: "..."

### 2. [Nome do ângulo]
...
```

---

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `GOOGLE_API_KEY` | ✅ | Google AI Studio — para Gemini (imagem + VEO3) |
| `SUPABASE_URL` | ✅ | URL do projeto Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Service Role Key (não a anon key) |

---

## Tecnologias

| Tecnologia | Uso |
|-----------|-----|
| [Claude Code](https://claude.ai/code) | Runtime dos agentes |
| [Claude Opus 4](https://anthropic.com) | Roteirista + Copywriter (agentes criativos) |
| [Claude Sonnet 4](https://anthropic.com) | Coordinator + Diretor + Fotógrafo + Produtor |
| [Google Gemini](https://aistudio.google.com/) | Geração de imagens |
| [Google VEO 3](https://deepmind.google/technologies/veo/) | Geração de vídeos |
| [Supabase](https://supabase.com) | Banco de dados + Storage de mídia |

---

## Licença

MIT
