# 3D craft

Read when 3D/WebGL is part of the brief. Review geometry, materials, lighting, camera, motion, fidelity and cost independently. Working WebGL is only an implementation fact. Read research-contract.md for receipt fields.

## 3D Craft System

3D deixa de ser tratado como “WebGL presente = missão cumprida”.

## 3D stack intelligence

Pesquisar conforme o papel da cena:

```text
Three.js
React Three Fiber
Drei
React Three Rapier
Three.js examples
Pmndrs ecosystem
Theatre.js
GSAP
Spline runtime
Rive where appropriate
glTF ecosystem
KTX2
Draco
Meshopt
HDRI / environment tooling
```

React Three Fiber deve ser entendido como renderer React de Three.js; Drei como coleção de abstrações prontas para R3F.

Theatre.js deve ser considerado quando animação de cena/câmera/material exigir direção temporal mais refinada. Ele possui integração com React Three Fiber, Three.js e HTML/SVG.

## 3D Quality Gates

Uma cena 3D não passa apenas porque carrega.

Avaliar:

### Geometry

```text
silhouette quality
poly density
visible faceting
normal quality
UV integrity
edge quality
LOD
mesh scale
```

### Materials

```text
PBR correctness
roughness
metalness
normal mapping
texture resolution
anisotropy
alpha artifacts
environment response
```

### Lighting

```text
key/fill/rim logic
environment
shadow resolution
contact shadow
tone mapping
exposure
contrast
```

### Camera

```text
FOV
composition
near/far planes
camera motion
damping
framing responsive behavior
```

### Rendering

```text
DPR
antialiasing
texture filtering
color management
postprocessing
SSR/SSAO/bloom only when justified
```

### Motion

```text
object choreography
camera easing
no robotic linear interpolation
no accidental clipping
no motion discontinuity
```

### Performance

```text
draw calls
triangle count
texture memory
shader complexity
mobile fallback
lazy loading
adaptive DPR
```

## 3D Resolution Rule

Proibir implicitamente cenas que parecem pobres por:

```text
low-res textures
poor normal maps
undersampled canvas
bad DPR
weak lighting
cheap extrusion
primitive geometry pretending to be finished asset
pixelated text in texture
oversized compression
```

Lobster deve perguntar internamente:

> “A baixa qualidade percebida vem realmente da modelagem, ou de lighting/material/render resolution/camera?”

Corrigir a causa correta.

## Asset Acquisition for 3D

Lobster pode pesquisar assets quando o usuário não exigiu modelagem original.

Fontes possíveis:

```text
Poly Haven
ambientCG
Sketchfab
Kenney
Quaternius
Three.js examples
Pmndrs demos/assets
official vendor assets
user-provided models
```

Sempre verificar licença.

Nunca inventar provenance.

## 3D Evidence

Registrar no receipt:

```text
3d_evidence
```

quando aplicável.

Registrar:

```text
asset source
model format
texture sizes
renderer DPR
lighting setup
camera
performance observation
mobile fallback
```

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

## Progressive Enhancement

Heavy craft não pode significar experiência quebrada.

Planejar fallback para:

```text
no WebGL
low performance
reduced motion
small viewport
touch
slow connection
asset failure
```

## Performance Budget

Quando houver efeitos pesados, registrar orçamento aproximado:

```text
JS cost
asset weight
texture memory
video
draw calls
animation work
layout work
```

Lobster deve preferir:

```text
transform
opacity
native compositor
WAAPI
ScrollTimeline
```

quando suficientes.

Motion, por exemplo, combina APIs do browser com fallback JS para casos mais complexos e oferece suporte direto a scroll e gestures.

## High-Fidelity 3D Pass

Se 3D é protagonista, fazer passe dedicado:

```text
geometry
material
texture
lighting
camera
animation
postprocessing
resolution
performance
fallback
```

Se continuar visualmente pobre:

> do not hide poor geometry behind bloom, blur, chromatic aberration, or excessive postprocessing.
