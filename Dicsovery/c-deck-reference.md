# c-deck JSON Component Catalog

This is the full, authoritative list of block `type` values the `JsonSlideDeck`
renderer understands. It's generated from `src/SlideTemplates.jsx` — every
named export there is auto-registered as a usable `type`. **Never invent a
`type` that isn't on this list**: an unrecognized type renders nothing (the
component logs a warning and returns `null`), so the slide silently loses
that content instead of failing loudly.

## How nesting works

`renderBlock` in `src/JsonSlideDeck.jsx` takes each JSON object, pulls out
`type` and `content`, and passes everything else through as props:

```js
const { type, content, ...rest } = block;
// rest        -> spread as props (variant, title, label, items, headers, rows, ...)
// content     -> recursively rendered and passed as the component's children
```

So the rule is: **anything that should become the rendered children of a
component goes under `content`, and `content` must always be a JSON array**
— even for a single string. Every other field — `variant`, `title`, `items`,
`headers`, `rows`, `markers`, `rungs`, `draws`, `num`, `label`, etc. — is a
flat prop sitting next to `type`, not inside `content`.

```json
{ "type": "Slide", "content": [
  "a bare string is allowed *inside the array*",
  { "type": "Headline", "html": "..." }
]}
```

**Gotcha: a bare string is not a valid `content` value, even though it looks
like it should be.** `renderBlock` only builds children when
`Array.isArray(content)` is true:

```js
let children = null;
if (content && Array.isArray(content)) {
  children = content.map(...);
}
```

So `{ "type": "SlideCard", "title": "Chat", "content": "Some text" }` —
the exact pattern shown in this repo's own README — silently renders an
*empty* card body: the string fails the array check, `children` stays
`null`, and the text never appears. Always wrap single strings in an array:
`"content": ["Some text"]`. This is the single most common way a generated
deck looks structurally fine but is missing visible text — always use the
array form, and don't trust the README's flat-string example literally.

The root `Slide` / `TitleSlide` block in `data.slides` gets an `active` prop
injected automatically by the deck — never set `active` yourself.

## Deck-level shape

```json
{
  "brand": "Optional string, top-left chrome label",
  "meterLabel": "Optional string, label above the progress bar (defaults to PROGRESS)",
  "theme": "Optional: 'light' | { preset: 'light' | 'dark-finops', overrides: { ...tokens } }",
  "slides": [ /* array of TitleSlide / Slide blocks, see below */ ]
}
```

Theme override tokens (only needed if asked for custom colors/fonts): `ink`,
`ink2`, `ink3`, `paper`, `amber`, `amberDeep`, `teal`, `coral`, `violet`,
`text`, `muted`, `line`, `line2`, `disp`, `body`, `mono`.

## Slide shells (top level of the `slides` array)

### `TitleSlide`
Hero/title slide. Flat props only — **no `content` array**.

| prop | notes |
|---|---|
| `tagText` | small text in the top tag row |
| `chipText` | pill/badge next to `tagText` |
| `title` | big heading; HTML allowed (sanitized) |
| `subtitle` | supporting line; HTML allowed |
| `creditBold` | bold credit/byline text |
| `creditMuted` | muted text after the credit |
| `hintContent` | small hint row, e.g. keyboard shortcuts; HTML allowed |

### `Slide`
Generic content shell for every other slide.

| prop | notes |
|---|---|
| `content` | array of content blocks (see below), required for any visible content |

Typical slide anatomy, top to bottom: `Eyebrow` → `Headline` → `Lead` →
one primary body component (table/grid/list/chart — pick ONE per the
guidance in SKILL.md, don't stack three different visualizations on one
slide).

## Content blocks (used inside a `Slide`'s `content` array)

### `Eyebrow`
Running section tag at the top of a slide.
`{ "num": "01", "text": "Section name" }`

### `Headline`
Large display heading.
`{ "html": "Some <span class=\"hl\">highlighted</span> text" }` — or use
`content: ["plain text"]` for no markup. `html` is sanitized via DOMPurify,
so inline `<span class="hl">` / `class="cool"` / `class="vio"` spans are the
normal way to add color accents (amber / teal / violet) inside a headline or
lead. `style` (inline CSS object) is optional.

### `Lead`
Subdued paragraph under the headline. Same shape as `Headline`: `html` or
`content`, plus optional `style`.

### `StatRow` / `Stat`
Dashboard-style big numbers.
```json
{ "type": "StatRow", "content": [
  { "type": "Stat", "value": "72%", "color": "amber", "label": "pool remaining" }
]}
```
`color` is a free-form class hook (e.g. `amber`, `cool`, `vio`, or empty).

### `CardGrid` / `SlideCard`
Responsive card grid. `cols` is `2`, `3`, or `4`.
```json
{ "type": "CardGrid", "cols": 2, "content": [
  { "type": "SlideCard", "variant": "good", "title": "Win", "content": "Short description." },
  { "type": "SlideCard", "variant": "bad", "title": "Risk", "content": "Short description." }
]}
```
`SlideCard` props: `variant` (free-form, e.g. `good`/`bad`/`warn`/`""`),
`label` + `labelType` (small badge), `title`, `tickLabel` (small corner
tag), and `content` — **always an array**, e.g. `["Some text"]` for a plain
paragraph or nested blocks for richer bodies (e.g. a `TickList` inside a
card). See the gotcha above: a bare string here renders nothing.

### `TickList`
Bulleted list with `›` markers. Items are raw HTML strings (sanitized), not
nested blocks: `{ "items": ["First point", "Second <b>point</b>"] }`.

### `NoteBlock`
Colored callout box. `variant` is free-form (e.g. `vio`, `coral`, `""`).
Use `html` for a single sanitized HTML string, or `content: ["..."]`
(array, per the gotcha above) for nested blocks/plain text.

### `DataTable`
Styled comparison/pricing table.
```json
{ "type": "DataTable",
  "headers": [{ "label": "Plan" }, { "label": "Price" }],
  "rows": [
    { "highlight": true, "cells": [
      { "value": "Pro", "name": true },
      { "value": "$20", "price": "good" }
    ]}
  ]
}
```
Header cells support `hideSm` (hide on small screens). Row cells support
`name` (bold/name styling), `mono` (monospace), `price` (free-form class,
e.g. `good`/`bad`), `hideSm`, and `dot` (small colored status dot, free-form
class).

### `Spectrum`
Gradient bar with positioned markers (e.g. plotting options on a scale).
```json
{ "type": "Spectrum", "markers": [
  { "position": "20%", "tier": "good", "value": "$4", "name": "Option A" }
]}
```

### `PoolReservoir`
Animated fill bar (e.g. a shared budget/credit pool).
```json
{ "type": "PoolReservoir", "level": "72%", "label": "Shared credit pool",
  "pctText": "~72% remaining",
  "draws": [{ "text": "Background agents", "action": "-18%" }]
}
```

### `NestedLayers` / `Layer`
Layered system/architecture diagram.
```json
{ "type": "NestedLayers", "content": [
  { "type": "Layer", "layerType": "outer", "label": "Org budget", "description": "set quarterly" },
  { "type": "Layer", "layerType": "inner", "label": "Team pool", "description": "shared by 8 seats" }
]}
```
`Layer`'s component prop for styling is literally named `type` in the React
source (e.g. `outer`/`inner`/a tier name) — but since the JSON block's own
`type: "Layer"` key already selects the component, **do not also add a
second `type` field for the styling hook**, it will collide and be consumed
as the block selector instead of the prop. There's no JSON-safe way to pass
both; in practice just pick a `label`/`description` that conveys the tier
and skip the extra styling prop, or check the current `Layer` source in
`src/SlideTemplates.jsx` if exact tier styling matters.

### `LadderChart`
Horizontal cost-comparison bars.
```json
{ "type": "LadderChart", "rungs": [
  { "label": "Self-hosted", "sublabel": "per seat/mo", "width": "40%",
    "gradient": "linear-gradient(90deg,#46D4B3,#2FA88C)", "cost": "$12" }
]}
```

### `Stages` / `StageCard`
Numbered phase/playbook cards.
```json
{ "type": "Stages", "content": [
  { "type": "StageCard", "num": "01", "title": "Pilot",
    "items": ["Define scope", "Pick 2 pilot teams"] }
]}
```
`StageCard.items` is an array of raw HTML strings (sanitized), same as
`TickList.items` — not nested blocks.

### `SplitColumns` / `SplitCol`
Two-track side-by-side layout (e.g. admin view vs. user view).
```json
{ "type": "SplitColumns", "content": [
  { "type": "SplitCol", "role": "admin", "title": "For admins", "content": [
    { "type": "TickList", "items": ["Set the pool budget"] }
  ]}
]}
```

### `Code` / `Mono`
Inline styled text spans for use inside other text-bearing props (`content`
arrays of `Headline`/`Lead`/`SlideCard`, etc.): `{ "type": "Code", "content": ["npm install"] }`.

### `Hl` / `Cool` / `Vio`
Inline accent-color spans (amber / teal / violet) for use *inside* a
`Headline`/`Lead`'s `content` array when you want to mix highlighted and
plain text without writing raw HTML:
```json
{ "type": "Headline", "content": [
  "Reduce ", { "type": "Hl", "content": ["seat costs"] }, " by 40%"
]}
```
Equivalent to writing `html: "Reduce <span class=\"hl\">seat costs</span> by 40%"`
— use whichever is easier to construct correctly; `html` is more compact for
simple cases, the nested-block form avoids any HTML-escaping mistakes.



## Example deck json
```json 
{
  "brand": "Acme FinOps",
  "meterLabel": "PILOT PROGRESS",
  "slides": [
    {
      "type": "TitleSlide",
      "tagText": "PILOT SUMMARY · Q3",
      "chipText": "FINOPS",
      "title": "Cutting AI Seat Costs <span class=\"hl\">40%</span>",
      "subtitle": "Moving from per-seat licensing to a shared token pool.",
      "creditBold": "One Shared Pool",
      "creditMuted": "govern the pool, not the seats",
      "hintContent": "<kbd>&rarr;</kbd> Next slide &middot; <kbd>O</kbd> Overview &middot; <kbd>F</kbd> Fullscreen"
    },
    {
      "type": "Slide",
      "content": [
        { "type": "Eyebrow", "num": "01", "text": "The Problem" },
        { "type": "Headline", "html": "Seat costs scale <span class=\"hl\">faster</span> than usage" },
        { "type": "Lead", "html": "Three teams, three license tiers, no shared budget." },
        {
          "type": "CardGrid",
          "cols": 2,
          "content": [
            { "type": "SlideCard", "variant": "bad", "title": "Today", "content": ["Per-seat billing regardless of actual token usage."] },
            { "type": "SlideCard", "variant": "good", "title": "Proposed", "content": ["Shared token pool billed by consumption."] }
          ]
        }
      ]
    },
    {
      "type": "Slide",
      "content": [
        { "type": "Eyebrow", "num": "02", "text": "Usage by Activity" },
        { "type": "Headline", "content": ["Background agents drive ", { "type": "Hl", "content": ["62%"] }, " of spend"] },
        {
          "type": "StatRow",
          "content": [
            { "type": "Stat", "value": "62%", "color": "amber", "label": "background agents" },
            { "type": "Stat", "value": "23%", "color": "cool", "label": "chat" },
            { "type": "Stat", "value": "15%", "color": "vio", "label": "code review" }
          ]
        }
      ]
    },
    {
      "type": "Slide",
      "content": [
        { "type": "Eyebrow", "num": "03", "text": "Pricing Comparison" },
        { "type": "Headline", "html": "Pooled pricing wins at every tier" },
        {
          "type": "DataTable",
          "headers": [{ "label": "Plan" }, { "label": "Seats" }, { "label": "Monthly" }],
          "rows": [
            { "cells": [{ "value": "Per-seat", "name": true }, { "value": "8" }, { "value": "$960", "price": "bad" }] },
            { "highlight": true, "cells": [{ "value": "Shared pool", "name": true }, { "value": "8" }, { "value": "$580", "price": "good" }] }
          ]
        }
      ]
    },
    {
      "type": "Slide",
      "content": [
        { "type": "Eyebrow", "num": "04", "text": "Rollout Plan" },
        { "type": "Headline", "html": "Three stages, six weeks" },
        {
          "type": "Stages",
          "content": [
            { "type": "StageCard", "num": "01", "title": "Pilot", "items": ["Pick 2 teams", "Set a starter budget"] },
            { "type": "StageCard", "num": "02", "title": "Expand", "items": ["Add remaining teams", "Tune alert thresholds"] },
            { "type": "StageCard", "num": "03", "title": "Operate", "items": ["Monthly budget review", "Quarterly rate renegotiation"] }
          ]
        },
        { "type": "NoteBlock", "variant": "vio", "html": "Risk: a single noisy team can drain the shared pool — mitigated by per-team soft caps." }
      ]
    }
  ]
}
```
