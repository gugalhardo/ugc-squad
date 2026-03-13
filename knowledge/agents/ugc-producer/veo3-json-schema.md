# VEO 3.1 — Schema JSON e Regras de Producao

## Contrato de estrutura

Todo JSON de cena deve conter exatamente estes 5 blocos de topo:

```
scene / camera / sequence / dialogue / lighting
```

Responda sempre com um unico JSON valido e completo. Sem texto fora do JSON.

---

## Schema

```json
{
  "scene": {
    "description": "Personagem (aparencia, roupa, acessorios) + cenario + atmosfera geral",
    "style": "Estetica geral — UGC autentico, vertical, social media",
    "aspect_ratio": "9:16",
    "duration_seconds": 8
  },
  "camera": {
    "framing": "Tipo de enquadramento — close-up, medium shot, etc.",
    "angle": "Angulo — eye-level, etc.",
    "movement": "Movimento geral da camera durante toda a cena"
  },
  "sequence": [
    {
      "time": "0.0-X.X",
      "action": "O que acontece neste trecho: expressao facial + gesto corporal + qual parte da fala esta sendo dita",
      "camera": "(opcional) mudanca de camera neste trecho especifico, se houver"
    }
  ],
  "dialogue": {
    "text": "Fala exata em portugues",
    "tone": "Tom de entrega — firme, calmo, ironico, acolhedor, etc."
  },
  "lighting": {
    "type": "Tipo de iluminacao",
    "source": "Fonte de luz",
    "temperature": "Temperatura de cor em Kelvin"
  }
}
```

---

## Regras obrigatorias

- **Duracao padrao: 8 segundos** — nao alterar salvo instrucao explicita
- **Audio:** apenas voz do personagem — sem musica, sem fundo sonoro
- **Idioma dos campos:** ingles tecnico cinematografico em todos os valores. Excecao: `dialogue.text` e sempre em portugues.
- **JSON valido:** sem texto fora do JSON, sem comentarios, sem explicacoes
- **Marcas e pessoas reais:** nunca citar — use descricoes genericas
- **Camera:** o Produtor decide framing e movimento — o Diretor so define atuacao
- **Fala comeca em 0.0s** — o primeiro item da sequence ja tem a fala iniciando, sem silencio inicial

## Sobre o campo `sequence.action`

Combine expressao + gesto + fala do trecho em um unico campo descritivo. Exemplo:

```
"She opens with a direct gaze, eyebrows slightly raised, torso leaning slightly forward. She says: 'Separei aqui os 5 erros que a maioria...'"
```

O campo `camera` dentro de cada item da sequence e **opcional** — so use quando a camera muda naquele trecho especificamente.

## `post_fx` — constante UGC (nao vai no JSON)

Todos os videos UGC usam os mesmos post_fx. O script de geracao aplica automaticamente:
- Natural skin tones, slight warmth, minimal smartphone correction
- Moderate smartphone sharpness
- Very subtle digital noise (mobile capture grain)
- No vignette
- Light digital stabilization preserving handheld authenticity

## Auto-check antes de entregar

Valide mentalmente antes de gerar:
- JSON valido e completo?
- Todos os 5 blocos presentes (scene, camera, sequence, dialogue, lighting)?
- duration_seconds = 8?
- dialogue.text em portugues?
- Fala comeca no primeiro item da sequence (0.0s)?
- Sem texto fora do JSON?
- Sem nomes de marcas ou pessoas reais?

---

## Exemplo completo — cena UGC talking head

```json
{
  "scene": {
    "description": "Brazilian woman, 28-32 years old, medium build, wearing an off-white lightweight turtleneck and a thin gold necklace. Long dark brown straight hair falling past shoulders. Speaking directly to camera in front of a solid green chromakey background, evenly lit.",
    "style": "Natural UGC aesthetic, vertical social media video, authentic and direct delivery.",
    "aspect_ratio": "9:16",
    "duration_seconds": 8
  },
  "camera": {
    "framing": "Medium shot from mid-torso upward, subject centered in vertical frame.",
    "angle": "Eye-level, smartphone perspective.",
    "movement": "Static with subtle handheld micro-movements throughout."
  },
  "sequence": [
    {
      "time": "0.0-2.5",
      "action": "She looks directly into the lens, eyes open and alert, both eyebrows slightly raised. Torso leans slightly forward. Hands relaxed at lower frame. She says: 'Separei aqui os 5 erros que a maioria dos atacadistas...'"
    },
    {
      "time": "2.5-8.0",
      "action": "She continues with firm direct conviction, steady eye contact, natural mouth articulation. Hands remain relaxed. She finishes: '...comete todo dia e que provavelmente estao destruindo as suas vendas sem voce perceber.'"
    }
  ],
  "dialogue": {
    "text": "Separei aqui os 5 erros que a maioria dos atacadistas comete todo dia e que provavelmente estao destruindo as suas vendas sem voce perceber.",
    "tone": "Firm and direct."
  },
  "lighting": {
    "type": "Natural indoor soft light",
    "source": "Diffused window light from front-left",
    "temperature": "Warm daylight 5500K"
  }
}
```

---

## CLI de geracao

```bash
# Via JSON payload (recomendado)
python scripts/generate_video.py --payload "outputs/{task}/04-production/veo3-payloads/scene-XX.json" --image "outputs/{task}/03-photography/scene-XX.png" --output "outputs/{task}/04-production/scene-XX.mp4"
```
