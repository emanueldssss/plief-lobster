# Typography craft

Read before selecting or repairing type. A role system and its rendering evidence must justify the choice; a font name alone cannot do that.

## Typography Intelligence

Fontes de pesquisa:

```text
Google Fonts
Fontsource
Fontshare
Typewolf
variable font documentation
Fonts In Use
real design systems
existing project fonts
```

Lobster deve distinguir:

```text
display
heading
body
label
caption
code
numeric
editorial
interface
```

## Font Acquisition Gate

Antes de adicionar fonte nova:

```text
Does the project already have a viable family?
Does the concept actually require another family?
Is the font licensed?
Are required weights/styles available?
Does it support the required glyphs/language?
What happens during fallback?
What is the loading strategy?
```

## Typography Rendering Gate

Inspecionar:

```text
font-size
weight
optical size
tracking
line-height
measure
wrap
fallback
font smoothing
variable axis usage
numeric alignment
heading rhythm
```

Testar:

```text
short text
long text
all caps
numbers
Portuguese accents
multilingual strings when relevant
narrow viewport
200% zoom where applicable
```

## No Fake Premium Typography

Rejeitar automaticamente:

```text
Inter everywhere
giant 72px heading
font-weight 800
letter-spacing -0.04em
gray paragraph
```

como substituto de direção tipográfica.

Inter pode ser correta.

O padrão automático não.
