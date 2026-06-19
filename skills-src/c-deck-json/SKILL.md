---
name: c-deck-json
description: Converts a source document — meeting notes, a README, a spec, a transcript, a pasted outline, a Word/PDF export, anything text-based — into a complete presentation JSON object that renders via this repo's JsonSlideDeck component. Use this whenever the user wants to turn written content into a slide deck, presentation, or "deck.json" for c-deck, even if they don't say "JSON" explicitly (e.g. "make a deck out of this doc", "turn these notes into slides", "build a presentation from this spec"). Also use it when asked to add or fix slides in an existing c-deck deck JSON file, since it knows the exact component schema and will catch invalid types before they silently disappear at render time.
---

# c-deck Deck JSON Builder

`JsonSlideDeck` (in `src/JsonSlideDeck.jsx`) renders a whole presentation from
one JSON object. The hard part isn't writing JSON — it's knowing which of the
~25 components fits a given piece of content, and getting the prop shapes
right so nothing silently drops. An unrecognized `type` doesn't error, it
just renders nothing and logs a console warning, so a wrong guess can produce
a deck that looks fine until you actually open it and a slide is half empty.

## Workflow

1. **Read the whole source document first.** Don't start mapping content to
   slides paragraph-by-paragraph — skim it end to end so the deck's
   structure reflects the document's actual argument, not its accidental
   ordering.

2. **Decide the shape of the deck before writing JSON.** Pick a title, then
   list out sections as one-line slide summaries. A good rule of thumb: one
   idea per slide. If a section needs more than ~2 cards, a table with more
   than ~5 rows, or a list with more than ~6 items to do it justice, split it
   into two slides rather than cramming — the renderer doesn't scroll, so
   overflow just gets visually cramped or clipped.

3. **First slide is always `TitleSlide`.** Every section after that
   typically opens with `Eyebrow` (sequential `num`, starting at `01`) +
   `Headline`, optionally a `Lead`, then *one* primary body component. Use
   this to pick that body component based on what the content actually is,
   rather than defaulting to `CardGrid` for everything:

   | content shape | component |
   |---|---|
   | pros/cons, wins/risks, before/after | `CardGrid` + `SlideCard` (`variant="good"`/`"bad"`) |
   | pricing, comparison rows | `DataTable` |
   | a single important number/metric | `StatRow` + `Stat` |
   | sequential phases/timeline | `Stages` + `StageCard` |
   | a flat list of points | `TickList` |
   | warning, risk, or important aside | `NoteBlock` |
   | two parallel tracks (e.g. admin vs. user) | `SplitColumns` + `SplitCol` |
   | options plotted on a scale | `Spectrum` |
   | a budget/capacity that fills up | `PoolReservoir` |
   | system/architecture layers | `NestedLayers` + `Layer` |
   | relative cost/size bars | `LadderChart` |

   Read `references/component-catalog.md` for the exact prop shape of every
   component before writing the JSON — it documents which fields are flat
   props vs. which go under `content` (the array that becomes the rendered
   children), plus deck-level fields (`brand`, `meterLabel`, `theme`). Two
   real gotchas it covers in detail, both easy to get wrong by pattern-
   matching off this repo's own README:
   - **`content` must always be a JSON array, even for one string.** A bare
     string (`"content": "some text"` — the exact shape the README's own
     `SlideCard` example uses) silently renders nothing, because
     `JsonSlideDeck`'s renderer only builds children when `content` passes
     `Array.isArray`. Always write `"content": ["some text"]`.
   - `Layer`'s styling prop is named `type` in the React source, which
     collides with the JSON block-selector key and is therefore unreachable
     through `JsonSlideDeck` — don't try to set it.

4. **Validate before presenting the result.** Run:
   ```
   node .claude/skills/c-deck-json/scripts/validate_deck.js <path-to-deck.json>
   ```
   This derives the allowed component list live from `src/SlideTemplates.jsx`
   (so it can't go stale) and walks your JSON for any `type` that doesn't
   match. Fix anything it flags — don't ship a deck with an unknown type.
   If the JSON only exists as a value in your response (not yet written to
   disk), write it to a temp file first so you can run the validator, then
   decide on the final destination per step 5.

5. **Deliver the result.** If the user named a file path (or one is obvious
   from context, e.g. `src/data/deck.json` in an app that already imports
   `JsonSlideDeck`), write it there. Otherwise show the JSON in a fenced code
   block and mention it can be passed directly as
   `<JsonSlideDeck data={...} />`. Either way, briefly note the slide count
   and which components you used, so the user can sanity-check structure
   without reading the raw JSON.

## Reference material

- `references/component-catalog.md` — every block type, its exact props, and
  worked-out JSON snippets. This is the source of truth for prop shapes;
  don't guess from memory or from the README's single short example.
- `assets/example-deck.json` — a complete 5-slide deck exercising title,
  cards, stats, a data table, stages, and a note block, validated clean. Use
  it as a structural reference for how slides compose, not as content to
  copy.
