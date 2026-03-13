# Guia de Prompts para Geracao de Imagem UGC

## Estrutura de cada prompt

Todo prompt tem 2 partes:

1. **BLOCO BASE** — fixo em todas as cenas (textura, qualidade, estilo UGC). Copie exatamente.
2. **BLOCO DE CENA** — varia por cena (expressao, gesto, enquadramento). Voce constroi com base na direcao do Diretor.

---

## BLOCO BASE — Copie em todos os prompts

```
Native smartphone vertical photo (9:16), authentic user generated content, organic social media aesthetic, non-commercial look, casual real-life capture, unpolished visual style.
High smartphone sharpness on face, natural skin texture visible, micro skin details: visible pores, minor unevenness, subtle redness around nose, faint under-eye texture, natural skin shine on forehead and cheeks, realistic skin imperfections. No beauty filter, no smoothing, no retouching, no glam filter. Minimal natural makeup slightly imperfect in texture.
Subtle digital noise in shadow areas, mild compression artifacts, smartphone HDR processing, slightly compressed dynamic range, natural JPEG compression.
Natural window light, uneven natural lighting, real daylight exposure, imperfect lighting balance, natural shadow falloff. Not studio lighting, not 3-point lighting. Soft but slightly uneven exposure typical of smartphone auto mode.
Natural color profile, smartphone color science, slight warm tone, no cinematic color grading, organic skin tones, auto white balance slightly warm.
Vertical 9:16 framing, handheld smartphone capture, slight wide angle distortion, casual framing, natural depth of field. Shot on iPhone rear camera, 26mm equivalent wide lens. Deep focus typical of small sensor. Slight highlight clipping, subtle digital sharpening edges, very light grain, minimal lens distortion near edges, authentic handheld framing slightly imperfect.
```

---

## BLOCO DE CENA — O que voce constroi por cena

Para cada cena, adicione ANTES do bloco base:

```
[PERSONAGEM]
[Genero, faixa etaria, aparencia]: descricao detalhada do Bloco Geral do Diretor.
Long dark brown hair falling organically, slight frizz and individual strands visible.
Natural posture with subtle shoulder asymmetry.
[Roupa]: descricao da roupa com textura realista — ex: "terracotta/coral lightweight turtleneck with realistic fabric weave and natural creases"
[Acessorios]: descricao — ex: "thin gold necklace slightly off-center, small gold earrings"

[ATUACAO DA CENA — da direcao do Diretor]
[Expressao facial]: traducao literal da direcao — ex: "direct eye contact, serious expression, micro facial tension, natural asymmetry between eyebrows, lips gently pressed with natural lip lines visible"
[Gesto]: traducao literal — ex: "right hand raised, five fingers open, slight motion softness from handheld capture"

[ENQUADRAMENTO — voce decide]
[Medium shot / Close-up / Wide]: justificado pela energia e intensidade da cena.
Ex: "Medium shot framing chest and torso upward, centered vertical composition"
```

---

## Exemplo completo — Cena 01

```
Brazilian woman, 28-32 years old, medium build, natural posture with subtle shoulder asymmetry. Long dark brown hair falling organically, slight frizz and individual strands visible. Terracotta/coral lightweight turtleneck with realistic fabric weave and natural creases. Thin gold necklace slightly off-center. Small gold earrings. Direct eye contact, serious expression, micro facial tension, natural asymmetry between eyebrows. Lips gently pressed with natural lip lines visible. Right hand raised, five fingers open, slight motion softness from handheld capture. Medium shot framing chest and torso upward, centered vertical composition. Native smartphone vertical photo (9:16), authentic user generated content, organic social media aesthetic, non-commercial look, casual real-life capture, unpolished visual style. High smartphone sharpness on face, natural skin texture visible, micro skin details: visible pores, minor unevenness, subtle redness around nose, faint under-eye texture, natural skin shine on forehead and cheeks, realistic skin imperfections. No beauty filter, no smoothing, no retouching, no glam filter. Minimal natural makeup slightly imperfect in texture. Subtle digital noise in shadow areas, mild compression artifacts, smartphone HDR processing, slightly compressed dynamic range, natural JPEG compression. Natural window light, uneven natural lighting, real daylight exposure, imperfect lighting balance, natural shadow falloff. Not studio lighting, not 3-point lighting. Soft but slightly uneven exposure typical of smartphone auto mode. Natural color profile, smartphone color science, slight warm tone, no cinematic color grading, organic skin tones, auto white balance slightly warm. Vertical 9:16 framing, handheld smartphone capture, slight wide angle distortion, casual framing, natural depth of field. Shot on iPhone rear camera, 26mm equivalent wide lens. Deep focus typical of small sensor. Slight highlight clipping, subtle digital sharpening edges, very light grain, minimal lens distortion near edges, authentic handheld framing slightly imperfect.
```

---

## Regras de prompts

- Sempre em ingles (melhor resultado com modelos de imagem)
- Personagem + atuacao primeiro, bloco base por ultimo
- Se a geracao falhar, simplificar o bloco de cena — nunca o bloco base
- Nao pedir muitos elementos complexos na mesma cena

**NUNCA use estes termos** (quebram a estetica UGC):
- cinematic, film look, dramatic lighting
- shallow depth of field cinematic
- professional photography, studio quality
- glamour, editorial, fashion shoot

**SEMPRE reforce estes termos** (garantem natividade UGC):
- authentic user generated content
- organic social media aesthetic
- non-commercial look, casual real-life capture
- unpolished visual style
- smartphone color science, no cinematic color grading
