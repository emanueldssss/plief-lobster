# Scroll craft

Read when native scrolling changes, when scenes are pinned or linked, and when investigating jank. Document the selected behavior and observed restoration/interruption cases.

## Scroll Craft System

Classificar scroll behavior:

```text
native
sticky narrative
scroll-triggered
scroll-linked
parallax
horizontal
snap
pinned
virtualized
smoothened
```

Antes de modificar comportamento nativo, justificar o benefício.

## Smooth Scroll Policy

Smooth-scroll library não deve ser instalada por reflexo.

Quando usada:

```text
preserve anchor navigation
preserve keyboard
avoid input lag
avoid nested scroll conflict
avoid breaking fixed/sticky
respect reduced motion
test touch
```

## Scroll Animation Quality Gate

Testar:

```text
slow wheel
fast wheel
trackpad
touch
resize
back navigation
direct anchor
refresh mid-page
mobile browser chrome
reduced motion
```

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


## Before selecting an engine

Run [Platform Capability Scout](platform-capability-scout.md): inspect View Transitions and CSS scroll-driven animations for the exact mechanism and browser targets before defaulting to a package. Choose native, hybrid or library on observed fit, with a tested fallback.
