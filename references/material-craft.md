# Material craft

Read when blur, glass, gradients, shadows, grain or glow contribute to the concept. CSS backdrop blur does not itself simulate optical refraction: judge layering and contrast rather than claiming physical optics.

## Blur / Glass / Material System

Definir uma material grammar no craft contract.

Todo:

```text
blur
glass
frost
shadow
glow
gradient
grain
noise
backdrop-filter
```

precisa pertencer a uma material grammar.

## Glass Quality Gate

Verificar:

```text
background underneath actually supports refraction
blur radius is proportionate
surface still has edge definition
text contrast survives changing backgrounds
nested glass is avoided unless intentional
border/highlight behavior agrees with light direction
shadow and blur do not contradict depth
```

Rejeitar:

```text
backdrop-blur-xl
bg-white/10
border-white/20
```

como solução automática para “premium”.

## Effects Budget

Cada superfície deve ter um **effects budget**.

Exemplo:

```text
Primary expressive device: 1
Secondary motifs: <= 2
Ambient effects: <= 2
```

Não transformar:

```text
blur
glow
grain
gradient
shader
marquee
parallax
3D
cursor
sparkles
```

todos em protagonistas simultâneos.

## “One Hero Mechanism” Rule

Para marketing/portfolio/high-concept UI:

Escolher pelo menos um mecanismo realmente memorável.

Exemplos:

```text
3D product choreography
cinematic typography
shader field
scroll narrative
spatial gallery
interactive comparison
elastic navigation
generative visualization
```

Mas este mecanismo precisa receber qualidade suficiente.

É melhor:

```text
1 mecanismo excelente
```

que:

```text
9 efeitos médios
```

## Blur Rendering

Quando blur animado produzir texto/asset borrado devido a transforms:

Investigar:

```text
fractional transforms
GPU rasterization
scale transforms
filter stacking
backdrop-filter
compositing layer
font antialiasing
```

antes de trocar aleatoriamente propriedades.

## Asset Resolution Gate

Nenhum asset visual importante pode passar sem verificar resolução suficiente para seu tamanho renderizado.

Aplica-se a:

```text
images
textures
videos
canvas
3D textures
SVG rasterization
poster images
Lottie
```
