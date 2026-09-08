# Motion craft

Read for interactive animation, transitions or authored motion. Record the grammar in DesignDNA and its summary in craft_contract; observe actual transitions, including interruption. Read research-contract.md for executable receipt fields.

## Motion Source Catalog

Pesquisar conforme necessidade:

```text
Motion
GSAP
ScrollTrigger
View Transitions API
CSS transitions/keyframes
Open Props easing
Motion Primitives
React Bits
Magic UI
Aceternity
Theatre.js
Rive
Lottie
```

Motion hoje possui APIs específicas para layout animation, scroll-linked animation, gestures, springs, exit animations e reduced motion.

GSAP + ScrollTrigger devem ser considerados em timelines complexas, pinning, scrub e choreographies profundamente ligadas ao scroll.

Lottie/Rive devem ser considerados para animation assets desenhados externamente em vez de recriar tudo com DOM quando fizer sentido. LottieFiles, por exemplo, oferece runtime web para assets Lottie/dotLottie.

## Motion Grammar

Todo projeto substancial deve possuir uma pequena motion grammar.

Exemplo:

```text
micro interaction
150–220 ms

small spatial transition
220–320 ms

layout transition
300–450 ms

hero expressive motion
450–900 ms

scroll-linked motion
continuous
```

Valores não são mandamentos.

A regra é:

> **animations belonging to the same experience must feel related.**

Definir:

```text
duration family
easing family
spring family
stagger logic
entrance direction
exit logic
hover response
press response
scroll response
```

## Motion Failure Detector

Considerar defeito visual:

```text
everything fades upward
every section animates
arbitrary 500ms ease-in-out
linear object movement
huge scale animations
hover scale on every card
excessive stagger
motion with no hierarchy
animations restarting while scrolling
layout jumps between animation states
text becoming blurry under transform
scroll-jank
sticky elements fighting each other
```

## Animation Interruption

Toda animação interativa importante deve sobreviver a:

```text
rapid hover/unhover
double click
fast scroll
route interruption
resize
touch
reduced motion
tab visibility change when relevant
```

Não basta parecer bonita quando reproduzida uma vez lentamente.

## Transition System

Route/page transitions devem possuir:

```text
entry state
continuity
exit behavior
loading behavior
focus behavior
scroll restoration policy
failure fallback
```

Não adicionar page transition só porque parece sofisticado.

Quando shared-element transition fizer sentido, pesquisar View Transitions / Motion layoutId / outra solução adequada antes de recriar manualmente.

## No Default Animation Package Behavior

Depois de adquirir um componente animado:

Não aceitar automaticamente seu default.

Inspecionar:

```text
duration
spring
easing
stagger
blur
scale
overshoot
```

e normalizar para o projeto.

## Animation Library Selection

### CSS/Open Props

Use para:

```text
small state change
hover
simple entrance
small loop
```

### Motion

Use para:

```text
layout
React state transitions
gestures
springs
shared layout
moderate scroll behavior
```

### GSAP

Use para:

```text
complex timeline
heavy scroll choreography
scrubbing
pinning
advanced sequencing
```

### Theatre.js

Use para:

```text
authored cinematic timeline
camera
3D
complex scene choreography
```

### Rive/Lottie

Use para:

```text
authored animation asset
illustration
brand animation
```

Não transformar seleção de library em religião.
