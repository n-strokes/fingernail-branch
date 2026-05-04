## What Firestorm actually does

I inspected the live page (the interactive lives in an iframe at `interactive.guim.co.uk/2013/may/dunalley/`) and pulled the structure and the relevant CSS/JS. Here is the mechanic, demystified.

### The architecture (one sentence)

There is exactly one viewport-sized "stage" on screen at any moment. Inside that stage is one chapter, which is taller than the viewport and scrolls *internally*. When you reach the end of its inner scroll, a "pull string" indicator appears; pulling past that boundary swaps the chapter for the next one with a transition. So the page never scrolls — chapters do, one at a time, and chapter handoff is a separate, deliberate gesture.

### The DOM, simplified

```
#GuiDunalley                              (the fixed-size stage, 100vw × 100vh)
├── .backgroundFader                      (cross-fades video/photo bg between chapters)
├── .scrollView
│   └── .sequenceView
│       └── .sectionView                  (CURRENT chapter only — others paged out)
│           ├── .pullToScroll             (position: fixed; the "pull string")
│           └── .sectionViewText          (the chapter's prose, taller than 600px)
└── .progressView                         (the chapter list / toc on the right)
```

Key facts I confirmed from the live DOM:
- `.scrollView` is `position: absolute; overflow: hidden`. The page itself does not scroll.
- `.sectionView` is `height: 600px; overflow: hidden` and contains a child `.sectionViewText` taller than that. The actual scrolling is handled in JS — they translate the inner content, they don't use native overflow.
- `.pullToScroll` is `position: fixed` with classes `.atTop`, `.atBottom`, `.pullingBottom`, `.hintToMoveOn` that toggle as you reach the inner-scroll edges.
- The handoff to the next chapter is fired from JS events `pullStringClickedDown` / `pullStringClickedUp`. Reaching the bottom does *not* auto-advance — you have to either click the indicator or pull past it.

### The state machine (what makes it feel right)

Each chapter has three internal states the JS toggles via classes on the `sectionView`:

1. **`pullingTop`** — you've scrolled to the top of the chapter; an upward pull-string is shown.
2. *neutral* — you're somewhere in the middle of the chapter; no indicator.
3. **`pullingBottom`** — you've scrolled to the bottom; a downward pull-string is shown.

There is also `.hintToMoveOn`, which animates the indicator at 0.2 opacity if the reader sits at the boundary too long without acting:

```css
.pullToScroll.hintToMoveOn {
  opacity: 0.2;
  animation: hintToMoveOnAnim 6s ease infinite;
}
```

The actual chapter swap is a JS-orchestrated cross-fade: the old `sectionView` is removed/translated out, the new one is inserted, and `.backgroundFader` cross-fades the underlying video/photo. There is no `scroll-snap-type` involved — Guardian built this in 2013, before CSS scroll-snap existed, and they used pure JS scroll capture.

### Why it feels "snappy"

Three mechanisms compound:

1. **Inner scroll is decoupled from outer scroll.** The browser's scrollbar never moves. There is nothing for the OS to inertially fling.
2. **Boundaries are sticky.** When the inner scroll hits top or bottom, further wheel/touch events accumulate against a *threshold* before the chapter swaps. You can wheel a little and bounce back; only a sustained pull commits.
3. **The commit gesture is visible.** The pull-string indicator gives the reader a target, so the "snap" doesn't feel like the page hijacking input — it feels like opening a door.

---

## What "a tad more sticky than theirs" means for your piece

Firestorm's stickiness is medium-firm: moderate threshold, fast cross-fade. To go a bit stickier you want one or more of:

- **Higher pull threshold.** Require ~80–120px of overscroll past the edge (or ~600–800ms of held intent) before committing. Theirs is around 40–60px.
- **Longer transition.** Their fade is ~400ms; yours could be 700–900ms with a slight directional translate (next chapter rises from below by ~24px while the current dims and lifts).
- **Hard rubber-band at edges.** When you hit the boundary, the inner scroll resists by half (translate slows to 0.5× wheel delta). This makes the boundary feel physical.
- **Quiet the indicator.** Theirs is a chunky 270×50 affixed badge. Yours can be a single hairline rule plus a 1ch glyph (`▽`) at 0.35 opacity, growing to 1.0 only as the threshold is approached.

---

## Spec for Claude Code

Below is a self-contained pattern. It uses a wheel/touch capture model (like Firestorm), not CSS `scroll-snap`, because CSS snap can't easily implement "internal scroll first, then handoff with a threshold." It also exposes tunables so you can dial stickiness.

### Markup

```html
<main class="stage" id="stage">
  <div class="chapter" data-index="0" aria-labelledby="ch0-title">
    <article class="chapter-inner">
      <h2 id="ch0-title">…</h2>
      <p>…</p>
      <!-- chapter prose, taller than the viewport -->
    </article>
    <div class="pull pull-down" aria-hidden="true">
      <span class="pull-rule"></span>
      <span class="pull-glyph">▽</span>
      <span class="pull-label">continue</span>
    </div>
    <div class="pull pull-up" aria-hidden="true">
      <span class="pull-glyph">△</span>
      <span class="pull-rule"></span>
    </div>
  </div>
  <!-- repeat .chapter for each chapter -->
</main>
```

Render only the *current* chapter into the DOM at a time, plus optionally a hidden pre-rendered "next" for the cross-fade frame.

### CSS (the structural part)

```css
:root {
  --pull-threshold: 96px;     /* how far past the edge before commit */
  --transition-out: 520ms;
  --transition-in:  720ms;
  --ease: cubic-bezier(.2,.7,.2,1);
}

html, body { height: 100%; overflow: hidden; }   /* page itself doesn't scroll */

.stage {
  position: fixed; inset: 0;
  overflow: hidden;
  background: var(--paper);
}

.chapter {
  position: absolute; inset: 0;
  overflow: hidden;             /* native scroll OFF; we drive translateY in JS */
  will-change: transform, opacity;
  transition:
    transform var(--transition-out) var(--ease),
    opacity   var(--transition-out) var(--ease);
}

.chapter.entering { opacity: 0; transform: translateY(24px); }
.chapter.entered  { opacity: 1; transform: translateY(0); transition-duration: var(--transition-in); }
.chapter.leaving  { opacity: 0; transform: translateY(-12px); }

.chapter-inner {
  position: absolute; left: 0; right: 0; top: 0;
  padding: 18vh 8vw 24vh;
  transform: translate3d(0, var(--inner-y, 0px), 0);
  /* JS sets --inner-y as the user scrolls within the chapter */
}

.pull {
  position: fixed; left: 50%; transform: translateX(-50%);
  display: grid; grid-auto-flow: column; gap: .6ch; align-items: center;
  font: 12px/1 ui-sans-serif, system-ui;
  letter-spacing: .12em; text-transform: uppercase;
  color: color-mix(in oklab, var(--ink) 55%, transparent);
  opacity: 0; pointer-events: none;
  transition: opacity 240ms var(--ease);
}
.pull-down { bottom: 4vh; }
.pull-up   { top: 4vh; }
.pull-rule { display:block; width: 6ch; height: 1px; background: currentColor; opacity:.5; }

/* state classes set on the chapter by JS */
.chapter.at-bottom .pull-down { opacity: .35; }
.chapter.pulling-bottom .pull-down { opacity: 1; transform: translate(-50%, calc(var(--pull-progress, 0) * -8px)); }
.chapter.at-top    .pull-up   { opacity: .35; }
.chapter.pulling-top .pull-up { opacity: 1; }

/* the rubber-band feel at the edge */
.chapter.at-bottom .chapter-inner { transition: transform 220ms var(--ease); }
```

### JS (the controller)

```js
class DialogueStage {
  constructor(stage, chapters) {
    this.stage = stage;
    this.chapters = chapters;       // array of HTMLElement
    this.i = 0;
    this.innerY = 0;                // current inner translate
    this.pullAccum = 0;             // accumulated overscroll past edge
    this.threshold = 96;            // px; mirror --pull-threshold
    this.busy = false;              // during transitions
    this.mount(this.i);

    stage.addEventListener('wheel', this.onWheel.bind(this), { passive: false });
    this._touch = { y: 0, active: false };
    stage.addEventListener('touchstart', e => { this._touch.y = e.touches[0].clientY; this._touch.active = true; });
    stage.addEventListener('touchmove',  e => this.onTouch(e), { passive: false });
    stage.addEventListener('touchend',   () => { this._touch.active = false; this.releasePull(); });
    window.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown' || e.key === ' ') { e.preventDefault(); this.scrollBy(80); }
      if (e.key === 'ArrowUp')                    { e.preventDefault(); this.scrollBy(-80); }
    });
  }

  mount(i) {
    this.stage.innerHTML = '';
    const ch = this.chapters[i].cloneNode(true);
    ch.classList.add('entering');
    this.stage.appendChild(ch);
    this.current = ch;
    this.inner = ch.querySelector('.chapter-inner');
    this.maxY = -(this.inner.scrollHeight - window.innerHeight); // negative number
    this.innerY = 0;
    this.applyInner();
    requestAnimationFrame(() => ch.classList.replace('entering', 'entered'));
    this.updateEdgeState();
  }

  applyInner() {
    this.inner.style.setProperty('--inner-y', this.innerY + 'px');
  }

  updateEdgeState() {
    const ch = this.current;
    ch.classList.toggle('at-top',    this.innerY >= 0);
    ch.classList.toggle('at-bottom', this.innerY <= this.maxY);
  }

  scrollBy(dy) {
    if (this.busy) return;
    const next = this.innerY - dy;
    if (next > 0) {
      this.accumulatePull(next, 'top');
    } else if (next < this.maxY) {
      this.accumulatePull(next - this.maxY, 'bottom'); // negative overshoot
    } else {
      this.innerY = next;
      this.pullAccum = 0;
      this.current.classList.remove('pulling-top', 'pulling-bottom');
    }
    this.applyInner();
    this.updateEdgeState();
  }

  accumulatePull(overshoot, edge) {
    // overshoot is signed; we use |overshoot| against threshold
    this.pullAccum += Math.abs(overshoot) * 0.5;        // rubber-band: half-rate accumulation
    const ch = this.current;
    ch.classList.toggle('pulling-bottom', edge === 'bottom');
    ch.classList.toggle('pulling-top',    edge === 'top');
    ch.style.setProperty('--pull-progress', Math.min(1, this.pullAccum / this.threshold));
    // clamp inner position at edge so it doesn't drift past
    this.innerY = edge === 'top' ? 0 : this.maxY;
    if (this.pullAccum >= this.threshold) this.commit(edge);
  }

  releasePull() {
    if (this.busy) return;
    this.pullAccum = 0;
    this.current.classList.remove('pulling-top', 'pulling-bottom');
    this.current.style.setProperty('--pull-progress', 0);
  }

  commit(edge) {
    if (this.busy) return;
    const dir = edge === 'bottom' ? +1 : -1;
    const target = this.i + dir;
    if (target < 0 || target >= this.chapters.length) { this.releasePull(); return; }
    this.busy = true;
    this.current.classList.add('leaving');
    setTimeout(() => {
      this.i = target;
      this.mount(this.i);
      this.busy = false;
      this.pullAccum = 0;
    }, 520); // match --transition-out
  }

  onWheel(e) { e.preventDefault(); this.scrollBy(e.deltaY); }
  onTouch(e) {
    if (!this._touch.active) return;
    const y = e.touches[0].clientY;
    const dy = this._touch.y - y;
    this._touch.y = y;
    e.preventDefault();
    this.scrollBy(dy);
  }
}

const stage = document.getElementById('stage');
const chapterTemplates = Array.from(document.querySelectorAll('template.chapter')).map(t => t.content.firstElementChild);
new DialogueStage(stage, chapterTemplates);
```

### Tunables to dial stickiness

| Knob | Firestorm-ish | Stickier (yours) |
|---|---|---|
| `--pull-threshold` | ~50px | **96–128px** |
| Pull accumulation rate | ~0.8 | **0.4–0.5** (half-rate rubber band) |
| `--transition-out` | ~280ms | **480–560ms** |
| `--transition-in` | ~360ms | **640–800ms** with 16–24px translate |
| Hint-to-move-on delay | ~5s | **8–10s**, lower target opacity (0.2 → 0.15) |
| Indicator weight | chunky badge | hairline + 1ch glyph |

### Two crossover ideas for your piece specifically

**Koan moment:** in addition to all of the above, give koan-chapters an extra `--pull-threshold: 200px` and a 1.2s transition. They should feel almost reluctant to leave. The indicator should not appear at all until the reader has been at the bottom for 4+ seconds.

**Haiku moment:** the opposite — let the haiku auto-mount its "next" sibling (a thumbnail dock) on commit, so the residue is preserved as a small artifact in the gutter of the next chapter. Concretely, in `commit()` for haiku-typed chapters, push the leaving chapter's haiku into a `.gutter-stack` element rather than letting it fully exit.

If you want, I can fold both behaviors into the controller as `chapter.dataset.kind === 'koan' | 'haiku' | 'dialogue'` branches and write a tiny test page that demos all three side by side.
