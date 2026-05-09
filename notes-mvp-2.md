# mvp-2

Live at https://n-strokes.github.io/fingernail-branch/lightened-claws.html

## What's new since mvp-1

- **Page is shareable.** Open Graph + Twitter Card meta tags point at `images/lightened-claws-preview.png` so iMessage / Slack / etc. show the cartoon as the link preview.
- **Repo is public** (was private under mvp-1). GitHub Pages serves from the `fingernail` branch root.
- **Heavy content iteration.** Most of the commits between mvp-1 and mvp-2 are n-strokes' copy and structural work on the dialogue itself — see `git log mvp-1..mvp-2` for the play-by-play. Highlights, in chronological order:
  - Page order rearranged: title → illustration → preface → dialogue.
  - Prologue koan text rewritten; preface page added before the intro.
  - Chapter 1 expanded with multi-step build sequences on the Bodhidharma question, including Mumonkan Case 37 and Case 21 reference panels.
  - Chapter 1's refrain consolidated into a single 13-step build.
  - Chapter 2 dropped the count-syllables / padded-haiku detour; added the John Wayne tag-question to the "same surface" build.
  - Chapter 3 rewritten as a 6-step build with fragment-reveal of the early Claws steps (Private Joker, etc.).
- **Mechanics tightened.**
  - Builds clip to their 100vh box so overflowing steps don't bleed into the next scene.
  - Scroll-to-top on re-entering a fully-revealed build.
  - Scroll input no longer advances pages — clicks / arrow keys only.
  - "Click to continue" hint hidden until the build's final step is shown.
  - All prose uses curly Unicode quotes/apostrophes/dashes.

## State at this tag

- Branch `fingernail`, commit at HEAD when tagged.
- Working files in repo root: `lightened-claws.html`, `same-teeth-same-surface-dialogue.md`, `build_lightened_claws.py`, `images/`, `1853b2bc-…json`.
- Prior artifacts in `0_archive/`.
- Tag history: `serviceable-1` (the earlier same-teeth-same-surface page) → `mvp-1` (first end-to-end lightened-claws build) → `mvp-2` (this).

## Reverting

```
git reset --hard mvp-2
```

or check out the tag without moving the branch:

```
git checkout mvp-2
```
