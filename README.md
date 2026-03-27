# UGC Creator Squad — Claude Agent Squad

Squad de agentes IA para criacao de videos UGC (User Generated Content) no modo manual, com aprovacao humana em cada etapa. Funciona 100% via [Claude Code](https://claude.ai/code) com o Agent SDK.

---

## O que e

Um pipeline de 4 agentes especializados que transforma uma ideia + foto base em material completo para producao de video UGC:

```
Roteirista → Diretor → Produtor → Copywriter
```

Cada agente entrega um output, voce aprova (ou pede ajuste), e o proximo agente comeca. Fluxo com aprovacao humana obrigatoria entre todas as etapas.

---

## Como funciona

Voce fornece uma **foto base do personagem** junto com a ideia do video. O squad gera:

1. **Roteiro** — 10 opcoes de gancho + roteiro completo (5-8 cenas)
2. **Direcao de cena** — atuacao, expressao, gesto e tom para cada cena (baseada na foto)
3. **JSONs VEO3** — payloads prontos para gerar videos via Google VEO 3
4. **Copy** — legenda do Instagram + 3 variacoes de ad copy para Meta Ads

Todos os outputs sao salvos como arquivos locais `.md` e `.json` organizados por marca e data.

---

## Estrutura do projeto

```
ugc-squad/
├── .claude/
│   └── agents/                         # Definicoes dos agentes (Claude Agent SDK)
│       ├── ugc-coordinator.md          # Orquestrador principal
│       ├── ugc-scriptwriter.md         # Roteirista
│       ├── ugc-director.md             # Diretor de cena
│       ├── ugc-producer.md             # Produtor (JSONs VEO3)
│       └── util-copywriter.md          # Copywriter (legenda + ad copy)
│
├── knowledge/
│   ├── squads/
│   │   └── ugc-creator/                # Conhecimento do squad
│   │       ├── PRD.md                  # Requisitos e fluxo detalhado
│   │       ├── ugc-best-practices.md   # O que funciona em UGC
│   │       ├── video-formats.md        # Specs tecnicas de video
│   │       └── reference-styles.md     # Template de estilos visuais por marca
│   ├── agents/
│   │   ├── ugc-scriptwriter/           # Padroes de gancho e estrutura de roteiro
│   │   ├── ugc-director/               # Template de direcao de cena
│   │   ├── ugc-producer/               # Schema JSON para VEO3
│   │   └── util-copywriter/            # Style guide de copy + guia de carrossel
│   └── brands/
│       └── _example/                   # Template de brand (copie e preencha)
│           ├── product.md
│           ├── audience.md
│           └── angles.md
│
├── outputs/                            # Outputs organizados por marca (gitignored)
│   └── {brand}/
│       └── ugc_{DD-MM-AA}_AD00X-{slug}/
│           ├── 01-script/              # hooks.md + script.md
│           ├── 02-direction/           # direction.md
│           ├── 03-photography/         # base-photo (foto do usuario)
│           ├── 04-production/          # scene-01.json ... scene-XX.json
│           └── 05-copy/               # caption.md + ad-copy.md
│
├── .gitignore
└── README.md
```

---

## Pre-requisitos

- [Claude Code](https://claude.ai/code) instalado
- Isso e tudo. Nao precisa de APIs, banco de dados ou dependencias Python.

---

## Setup

### 1. Clone o repositorio

```bash
git clone https://github.com/gugalhardo/ugc-squad.git
cd ugc-squad
```

### 2. Crie a brand da sua empresa

Copie o template e preencha com os dados do seu produto/marca:

```bash
cp -r knowledge/brands/_example knowledge/brands/minha-marca
```

Edite os 3 arquivos:
- `product.md` — produto, oferta, conceito central, tom de voz
- `audience.md` — publico-alvo, dores, desejos, linguagem usada
- `angles.md` — angulos de comunicacao mapeados

---

## Como usar

Abra o Claude Code na pasta do projeto e chame o coordinator enviando uma foto junto:

```
@ugc-coordinator
[anexe a foto do personagem]
Marca: minha-marca
Nome do anuncio: black-friday
Ideia: mostrar como nosso produto resolve [dor especifica]
Dor: [descricao da dor]
Tom de voz: direto, empatico, sem exagero
```

---

## Fluxo detalhado

### Etapa 1 — Roteirista (`ugc-scriptwriter`)

**Modelo:** Claude Opus

1. Le os docs da marca (`product.md`, `audience.md`, `angles.md`)
2. Gera **10 opcoes de gancho/headline** → voce escolhe um
3. Escreve o **roteiro completo**: 5-8 cenas, ~140-150 chars por cena (8s cada)
4. Salva em `01-script/hooks.md` + `01-script/script.md`

**Regras criticas:**
- Cada cena: exatamente 140-150 caracteres (8s de video)
- Sem traco (`-` ou `—`) nas falas — causa bug no VEO3
- Linguagem coloquial, frases curtas

---

### Etapa 2 — Diretor (`ugc-director`)

**Modelo:** Claude Sonnet

Recebe o roteiro aprovado + foto base e cria a **direcao de atuacao**:

**Bloco 1 — Personagem e Ambiente** (extraido da foto base):
- Genero, faixa etaria, aparencia, roupa, acessorios
- Cenario, atmosfera, arco emocional do video

**Bloco 2 — Direcao por cena** (varia a cada cena):
- Expressao facial inicial
- Gesto corporal (simples e natural)
- Tom de voz (1-2 palavras)
- Energia (1 palavra)

Salva em `02-direction/direction.md`

---

### Etapa 3 — Produtor (`ugc-producer`)

**Modelo:** Claude Sonnet

Monta todos os JSONs VEO3 com 5 blocos obrigatorios:

```json
{
  "scene": { "description": "..." },
  "camera": { "framing": "...", "angle": "...", "movement": "..." },
  "sequence": [{ "timestamp": "0.0s-4.0s", "action": "...", "emotion": "..." }],
  "dialogue": { "text": "...", "tone": "...", "language": "pt-BR" },
  "lighting": { "type": "...", "source": "...", "mood": "..." }
}
```

Salva em `04-production/scene-01.json`, `scene-02.json`, etc.

---

### Etapa 4 — Copywriter (`util-copywriter`)

**Modelo:** Claude Opus

Recebe marca + roteiro aprovado + angulo e gera:

1. **Legenda do post** (Instagram feed) — narrativa, nao descricao
2. **Ad copy para Meta Ads** — headline + texto primario + descricao (3 variacoes)

Salva em `05-copy/caption.md` + `05-copy/ad-copy.md`

---

## Aprovacao humana — 6 opcoes

Em cada etapa, voce escolhe:

```
1. Aprovar — seguir para o proximo passo
2. Pedir ajuste — diga o que quer mudar
3. Ajustar manualmente — voce edita o output e o agente segue com a versao editada
4. Refazer do zero — o agente gera um output completamente novo
5. Pular etapa — seguir sem o output dessa etapa
6. Parar fluxo — encerrar aqui (outputs ate agora ficam salvos)
```

Ciclos de ajuste: ilimitados.

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
Preco: ...
CTA principal: ...

## Tom de voz
Direto e empatico. Sem exagero. Linguagem de WhatsApp.
```

**`audience.md`** — O publico
```markdown
## Perfil
Genero: ...
Faixa etaria: ...
Ocupacao: ...

## Dores principais
- ...

## Desejos
- ...

## Como falam
Exemplos de linguagem que o publico usa...
```

**`angles.md`** — Angulos de comunicacao
```markdown
## Angulos mapeados

### 1. [Nome do angulo]
Descricao...
Exemplo de gancho: "..."

### 2. [Nome do angulo]
...
```

---

## Tecnologias

| Tecnologia | Uso |
|-----------|-----|
| [Claude Code](https://claude.ai/code) | Runtime dos agentes |
| [Claude Opus 4](https://anthropic.com) | Roteirista + Copywriter (agentes criativos) |
| [Claude Sonnet 4](https://anthropic.com) | Coordinator + Diretor + Produtor |

---

## Licenca

MIT
