"""
build_lightened_claws.py
Rebuild lightened-claws.html from same-teeth-same-surface-dialogue.md.

Recognized [@claude ...] directives:
  transition to chapterN                 → chapter-transition (1)
  new transition page here ... haiku     → chapter 2 transition
  now we have a chapter transition       → chapter 3 transition
  consolidate ... build-up after clicks  → start build-page
  do a transition here - new build page  → start build-page
  on this page the dialogue builds       → start build-page
  note deletions / simplification        → start build-page
  consolidate the below into a click-build → start build-page
  single tile that gets crowded          → start refrain-build
  1-click addition (build/further)       → continuation step
  end the 1-page click-build             → end build (flag color if "different color")
  end of new page and on to the placard  → end build
  end of the new page, on to the placard → end build
  this should be same with illustration  → koan-illustration scene
  second screen, not second part         → commentary scene
  [after one-click, as a build]          → marker for click-step (handled inline)
"""
import json
import re
from pathlib import Path
from html import escape

PROJECT = Path("/Users/n-strokes/Documents/9_works/interrogating a branch. also, fingernails.")
INPUT = PROJECT / "same-teeth-same-surface-dialogue.md"
OUTPUT = PROJECT / "lightened-claws.html"

# ==========================================================================
# Static content
# ==========================================================================

CHAPTERS = {
    1: "the koan",
    2: "the exchange",
    3: "claws lightened",
}

PREFACE_PARAGRAPHS = [
    'What follows is based on a real dialogue between a man and his clawed friend. It has been polished, and the claws were lightened.',
    'We shall call the man n-strokes (pronounced *en hyphen strokes*) and we shall call his friend Lightened Claws.',
]

INTRO = {
    'image': 'images/how-it-is-hanging-textless.jpg',
    'koan_paragraphs': [
        [
            'It is like a man up in a tree, hanging from a branch by his mouth;',
            'his hands cannot grasp a branch, his feet won’t reach a bough.',
        ],
        [
            'Another man comes under the tree and asks him,',
            '“What is the meaning of Bodhidharma coming from the West?”',
            'If he does not answer, he fails the questioner.',
            'If he answers, he will fall and die.',
            'At such a time, how should he answer?',
        ],
    ],
    'haiku_lines': [
        'the man looks down.',
        'his fingernails are bitten.',
    ],
}

KOAN_TEXT_PARAGRAPHS = INTRO['koan_paragraphs']

MUMON_COMMENTARY = [
    'Even if your eloquence flows like a river, it is of no use.',
    'Even if you can expound the whole body of the sutras, it is of no avail.',
    'If you can respond to it fittingly, you will give life to those who have been dead, '
    'and put to life those who have been alive.',
    'If, however, you are unable to do this, wait for Maitreya to come and ask him.',
]

# ==========================================================================
# Helpers
# ==========================================================================

def strip_directives(s):
    s = re.sub(r'\s*\[Claude:\s*enter date\]', ' (1228)', s)
    s = re.sub(r'\s*\[Claude:[^\]]*\]', '', s)
    s = re.sub(r'\s*\[@claude[^\]]*\]', '', s)
    s = re.sub(r'\s*\[after one-click,\s*as a build\]', '', s)
    return s.strip()

def render_inline(s):
    s = strip_directives(s)
    e = escape(s)
    e = re.sub(r'\*\*([^*\n]+)\*\*', r'<strong>\1</strong>', e)
    e = re.sub(r'\*([^*\n]+)\*', r'<em>\1</em>', e)
    return e

PLACARD_META = [
    ('the old branch still holds', 'Lightened Claws', '17 syllables', None),
    ('the branch holds',           'Lightened Claws', '12 syllables', None),
    ('the old pond',               'Bashō',           '12 syllables', 'example of the form, offered by Lightened Claws'),
    ('a young tree',               'n-strokes',       '11 syllables', None),
    ('the man looks down',         'n-strokes',       '11 syllables', None),
    ('he climbs down',             'Lightened Claws', '17 syllables', None),
    ('a man who asks questions',   'n-strokes',       '17 syllables', None),
    ('the answer was the asking',  'Lightened Claws', '10 syllables', None),
]

def attribute_placard(text):
    t = text.lower()
    for key, speaker, syll, note in PLACARD_META:
        if key in t:
            return (speaker, syll, note)
    return (None, None, None)

# ==========================================================================
# Parser
# ==========================================================================

with open(INPUT, encoding='utf-8') as f:
    md = f.read()

body = md.split('#dialogue', 1)[1] if '#dialogue' in md else md
lines = body.split('\n')
N = len(lines)

KOAN_OPEN = '[Panel with koan]'
KOAN_CLOSE = '[end 1-pg panel]'
KOAN_MID   = '[second part to panel introduced upon one click advance]'

def is_speaker_line(s):
    return bool(re.match(r'^(n-strokes|Lightened Claws):', s.strip()))

def is_block_starter(s):
    s = s.strip()
    return (is_speaker_line(s)
            or s.startswith(KOAN_OPEN)
            or s.startswith('[1pg placard')
            or s.startswith('[@claude'))

def consume_blank(i):
    while i < N and not lines[i].strip():
        i += 1
    return i

def directive_kind(line_raw):
    s = line_raw.strip().lower()
    if not s.startswith('[@claude'):
        return None
    if 'transition to chapter' in s:
        m = re.search(r'chapter\s*(\d+)', s)
        return ('chapter', int(m.group(1)) if m else 1)
    if 'new transition page here' in s and 'haiku' in s:                    return ('chapter', 2)
    if 'now we have a chapter transition' in s:                             return ('chapter', 3)
    if 'consolidate the below few' in s:                                    return ('build-start', 'build-page')
    if 'do a transition here - new build page' in s:                        return ('build-start', 'build-page')
    if 'on this page the dialogue builds' in s:                             return ('build-start', 'build-page')
    if 'note deletions / simplification' in s:                              return ('build-start', 'build-page')
    if 'consolidate the below into a click-build' in s:                     return ('build-start', 'build-page')
    if 'single tile that gets crowded' in s:                                return ('build-start', 'refrain-build')
    if '1-click addition' in s:                                             return ('build-step',)
    if 'end the 1-page click-build' in s:
        return ('build-end-flag-color',) if 'different color' in s else ('build-end',)
    if 'end of new page and on to the placard' in s:                        return ('build-end',)
    if 'end of the new page, on to the placard' in s:                       return ('build-end',)
    if 'new pages for each of the next two' in s:                           return ('noop',)
    if 'this should be same with illustration' in s:                        return ('koan-illustration-marker',)
    if 'second screen, not second part to the panel' in s:                  return ('commentary-marker',)
    return ('noop',)

scenes = []
current_build = None
current_build_type = None
break_pattern_next_n_strokes = False
chapter = 0

def flush_build():
    global current_build, current_build_type
    if current_build is not None and current_build:
        scenes.append({'type': current_build_type, 'steps': current_build, 'chapter': chapter})
    current_build = None
    current_build_type = None

def push_scene(scene):
    scene.setdefault('chapter', chapter)
    scenes.append(scene)

def parse_speaker_turn(i):
    line = lines[i].strip()
    m = re.match(r'^(n-strokes|Lightened Claws):\s*(.*)$', line)
    speaker = m.group(1)
    first = strip_directives(m.group(2))
    chunks = [first] if first else []
    i += 1
    while i < N:
        nxt = lines[i].strip()
        if not nxt:
            j = consume_blank(i)
            if j >= N:
                i = j; break
            next_line = lines[j].strip()
            if is_block_starter(next_line):
                i = j
                break
            chunks.append('')
            i = j
            continue
        chunks.append(strip_directives(nxt))
        i += 1
    paragraphs = []
    cur = []
    for c in chunks:
        if c == '':
            if cur:
                paragraphs.append(' '.join(cur).strip()); cur = []
        else:
            cur.append(c)
    if cur:
        paragraphs.append(' '.join(cur).strip())
    return [p for p in paragraphs if p], speaker, i

i = 0
while i < N:
    i = consume_blank(i)
    if i >= N: break
    line_raw = lines[i]
    line = line_raw.strip()

    # Directives
    if line.startswith('[@claude'):
        kind = directive_kind(line_raw)
        if kind is None:
            i += 1; continue
        if kind[0] == 'chapter':
            flush_build()
            chapter = kind[1]
            push_scene({'type': 'chapter-transition', 'number': chapter, 'title': CHAPTERS.get(chapter, '')})
            i += 1; continue
        if kind[0] == 'build-start':
            flush_build()
            current_build = []
            current_build_type = kind[1]
            i += 1; continue
        if kind[0] == 'build-step':
            content = re.sub(r'^\[@claude[^\]]*\]\s*', '', line_raw, count=1)
            content = strip_directives(content)
            if current_build is None:
                current_build = []; current_build_type = 'build-page'
            if content:
                current_build.append({'speaker': 'Lightened Claws', 'text': content})
            i += 1; continue
        if kind[0] in ('build-end', 'build-end-flag-color'):
            flush_build()
            if kind[0] == 'build-end-flag-color':
                break_pattern_next_n_strokes = True
            i += 1; continue
        # noop / koan-illustration-marker / commentary-marker — no immediate action
        # (the koan panel block below detects its own marker via the immediate context)
        i += 1; continue

    # Koan panel — emit koan-illustration + commentary scenes
    if line == KOAN_OPEN or line.startswith(KOAN_OPEN):
        flush_build()
        # skip over the panel content (we don't render it; we use static content)
        i += 1
        while i < N and lines[i].strip() != KOAN_CLOSE:
            i += 1
        i += 1
        push_scene({'type': 'koan-illustration'})
        push_scene({'type': 'commentary'})
        continue

    # Single placard
    m = re.match(r'^\[1pg placard\s*[-:]?\s*(.*)$', line)
    if m:
        flush_build()
        rest = m.group(1)
        if rest.rstrip().endswith(']'):
            text = rest.rstrip()[:-1]
            i += 1
        else:
            text_lines = [rest]
            i += 1
            while i < N:
                ll = lines[i]
                if ll.rstrip().endswith(']'):
                    text_lines.append(ll.rstrip()[:-1])
                    i += 1
                    break
                text_lines.append(ll)
                i += 1
            text = '\n'.join(t for t in text_lines if t.strip()).strip()
        text = text.replace('/newline', '\n').strip()
        if text.startswith('*') and text.endswith('*') and text.count('*') == 2:
            text = text[1:-1].strip()
        if text.lower() == 'the basho haiku':
            text = 'the old pond —\na frog jumps in,\nthe sound of water'
        push_scene({'type': 'placard', 'text': text})
        continue

    # Speaker turn
    if is_speaker_line(line):
        paragraphs, speaker, ni = parse_speaker_turn(i)
        i = ni
        if not paragraphs:
            continue
        if current_build is not None:
            for p in paragraphs:
                current_build.append({'speaker': speaker, 'text': p})
        else:
            scene = {'type': 'turn', 'speaker': speaker, 'paragraphs': paragraphs}
            if break_pattern_next_n_strokes and speaker == 'n-strokes':
                scene['break_pattern'] = True
                break_pattern_next_n_strokes = False
            push_scene(scene)
        continue

    # Continuation paragraph (orphan); attach to current build if any
    if current_build is not None and line:
        last_speaker = current_build[-1]['speaker'] if current_build else 'Lightened Claws'
        chunks = [strip_directives(line)]
        i += 1
        while i < N:
            nxt = lines[i].strip()
            if not nxt or is_block_starter(nxt): break
            chunks.append(strip_directives(nxt))
            i += 1
        text = ' '.join(c for c in chunks if c)
        if text:
            current_build.append({'speaker': last_speaker, 'text': text})
        continue

    i += 1

flush_build()

# Prepend in reverse order so final sequence is: title → intro (illustration) → preface → ...
scenes.insert(0, {'type': 'preface', 'chapter': 0})
scenes.insert(0, {'type': 'intro', 'chapter': 0})
scenes.insert(0, {'type': 'title', 'chapter': 0})

# ==========================================================================
# Render
# ==========================================================================

def render_title(s):
    return '''
      <div class="scene-inner title-inner">
        <h1 class="title-main">Same teeth,<br>same surface</h1>
        <p class="title-sub">a dialogue with n-strokes and lightened claws</p>
      </div>
      <p class="title-enter">↓</p>
    '''

def render_preface(s):
    paras_html = '\n'.join(f'<p>{render_inline(p)}</p>' for p in PREFACE_PARAGRAPHS)
    return f'''
      <div class="scene-inner preface-inner">
        <div class="preface-body">
{paras_html}
        </div>
      </div>
      <p class="preface-enter">begin ↓</p>
    '''

def render_intro(s):
    paras_html = '\n'.join(
        '<p>' + '<br>'.join(escape(line.strip()) for line in para) + '</p>'
        for para in INTRO['koan_paragraphs']
    )
    haiku_html = ' '.join(escape(line.strip()) for line in INTRO['haiku_lines'])
    return f'''
      <div class="scene-inner intro-inner">
        <div class="intro-text-column">
          <div class="intro-koan-block">
            <div class="intro-koan">
{paras_html}
            </div>
            <p class="intro-koan-attr">Mumon · Mumonkan · 1228</p>
          </div>
          <div class="intro-haiku-block">
            <blockquote class="intro-haiku">{haiku_html}</blockquote>
            <p class="intro-haiku-attr">n-strokes</p>
          </div>
        </div>
        <p class="intro-enter">enter dialogue ↓</p>
      </div>
    '''

def render_koan_illustration(s):
    paras_html = '\n'.join(
        '<p>' + '<br>'.join(escape(line.strip()) for line in para) + '</p>'
        for para in KOAN_TEXT_PARAGRAPHS
    )
    return f'''
      <div class="scene-inner intro-inner">
        <div class="intro-text-column">
          <div class="intro-koan-block">
            <div class="intro-koan">
{paras_html}
            </div>
            <p class="intro-koan-attr">Mumon · Mumonkan · 1228</p>
          </div>
        </div>
      </div>
    '''

def render_commentary(s):
    paras_html = '\n'.join(f'<p>{escape(p.strip())}</p>' for p in MUMON_COMMENTARY)
    return f'''
      <div class="scene-inner commentary-inner">
        <p class="commentary-eyebrow">Mumon’s commentary · 1228</p>
        <div class="commentary-body">{paras_html}</div>
      </div>
    '''

def render_chapter_transition(s):
    n = s['number']
    title = s.get('title', '')
    roman = ['', 'i.', 'ii.', 'iii.'][n] if 0 < n < 4 else f'{n}.'
    return f'''
      <div class="scene-inner chapter-inner">
        <p class="chapter-numeral">{escape(roman)}</p>
        <h2 class="chapter-title">{escape(title)}</h2>
      </div>
    '''

def render_turn(s):
    speaker = s['speaker']
    paras = ''.join(f'<p>{render_inline(p)}</p>' for p in s['paragraphs'])
    extra = ' turn--break-pattern' if s.get('break_pattern') else ''
    return f'''
      <div class="scene-inner turn-inner{extra}" data-speaker="{escape(speaker)}">
        <p class="speaker">{escape(speaker)}</p>
        <div class="body">{paras}</div>
      </div>
    '''

def render_placard(s):
    text = s['text']
    lines_h = [l.strip() for l in text.split('\n') if l.strip()]
    body = '<br>'.join(escape(l) for l in lines_h)
    speaker, syll, note = attribute_placard(text)
    cls = ''
    if speaker == 'n-strokes':       cls = 'placard--n-strokes'
    elif speaker == 'Lightened Claws': cls = 'placard--claws'
    elif speaker == 'Bashō':           cls = 'placard--basho'
    speaker_html = f'<span class="placard-speaker">{escape(speaker)}</span>' if speaker else ''
    syll_html = f'<span class="placard-syll">{escape(syll)}</span>' if syll else ''
    meta_html = f'<footer class="placard-meta">{speaker_html}{syll_html}</footer>' if (speaker or syll) else ''
    note_html = f'<p class="placard-note">{escape(note)}</p>' if note else ''
    return f'''
      <div class="scene-inner placard-inner {cls}">
        <blockquote class="placard-haiku">{body}</blockquote>
        {meta_html}
        {note_html}
      </div>
    '''

def render_step(step, idx):
    speaker = step['speaker']
    text_html = render_inline(step['text'])
    cls = 'step--user' if speaker == 'n-strokes' else 'step--claws'
    return (
        f'<div class="step {cls}" data-step="{idx}" aria-hidden="true">'
        f'<p class="step-speaker">{escape(speaker)}</p>'
        f'<div class="step-body">{text_html}</div>'
        f'</div>'
    )

def render_build_page(s):
    steps_html = '\n'.join(render_step(st, i) for i, st in enumerate(s['steps']))
    cls_extra = 'build--refrain' if s['type'] == 'refrain-build' else 'build--page'
    n_steps = len(s['steps'])
    return f'''
      <div class="scene-inner build-inner {cls_extra}" data-total="{n_steps}">
        <div class="build-stack">
{steps_html}
        </div>
        <p class="build-hint" aria-hidden="true">click to continue ↓</p>
      </div>
    '''

def render_scene(i, s):
    t = s['type']
    ch = s.get('chapter', 0) if t != 'chapter-transition' else s.get('number', 0)
    common = f'data-i="{i}" data-type="{t}" data-chapter="{ch}"'
    if t == 'title':
        return f'<section class="scene scene--title" {common}>{render_title(s)}</section>'
    if t == 'preface':
        return f'<section class="scene scene--preface" {common}>{render_preface(s)}</section>'
    if t == 'intro':
        return f'<section class="scene scene--intro" {common}>{render_intro(s)}</section>'
    if t == 'turn':
        speaker_class = 'turn--user' if s['speaker'] == 'n-strokes' else 'turn--claws'
        bp = ' scene--break-pattern' if s.get('break_pattern') else ''
        return f'<section class="scene scene--turn {speaker_class}{bp}" {common}>{render_turn(s)}</section>'
    if t == 'placard':
        return f'<section class="scene scene--placard" {common}>{render_placard(s)}</section>'
    if t == 'koan-illustration':
        return f'<section class="scene scene--intro scene--koan-illustration" {common}>{render_koan_illustration(s)}</section>'
    if t == 'commentary':
        return f'<section class="scene scene--commentary" {common}>{render_commentary(s)}</section>'
    if t == 'chapter-transition':
        return f'<section class="scene scene--chapter" {common}>{render_chapter_transition(s)}</section>'
    if t in ('build-page', 'refrain-build'):
        return f'<section class="scene scene--build center-visible" {common}>{render_build_page(s)}</section>'
    return ''

scenes_html = '\n'.join(render_scene(i, s) for i, s in enumerate(scenes))
click_only_indices = [i for i, s in enumerate(scenes) if s['type'] in ('placard', 'commentary', 'koan-illustration', 'chapter-transition')]
build_step_counts = {i: len(s['steps']) for i, s in enumerate(scenes) if s['type'] in ('build-page', 'refrain-build')}
chapter_starts = {0: 0}
for i, s in enumerate(scenes):
    if s['type'] == 'chapter-transition':
        chapter_starts[s['number']] = i

# ==========================================================================
# Compose final HTML
# ==========================================================================

HTML = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
<title>Lightened Claws — a dialogue</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><path d='M16 30 V18 M16 18 L8 10 M16 18 L24 10 M16 18 L16 6' stroke='%23232324' stroke-width='2.5' stroke-linecap='round' fill='none'/></svg>" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet" />
<style>
:root {
  --paper: #fefefa;
  --paper-deep: #f4ece0;
  --paper-warm: #efe5cf;
  --paper-aged: #e6dfca;
  --ink: #232324;
  --ink-soft: #5b5b5d;
  --ink-faint: #8c8c8f;
  --rule: #d6cfb9;
  --accent: #6a4a2a;
  --user-tag: #2b3a55;
  --claws-tag: #6a4a2a;
  --break-color: #8a3a2a;
  --placard-bg: #efe5cf;
  --commentary-bg: #2d2a26;
  --commentary-ink: #efe9d9;
  --font-sans: 'Brandon Grotesque', system-ui, -apple-system, sans-serif;
  --font-serif: 'EB Garamond', 'Iowan Old Style', Georgia, serif;
  --font-mono: 'JetBrains Mono', ui-monospace, Menlo, monospace;
  --ease: cubic-bezier(0.6, 0.05, 0.25, 1);
  --t-scene: 880ms;
}
*, *::before, *::after { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0; height: 100%; width: 100%;
  overflow: hidden; overscroll-behavior: none;
  background: var(--paper); color: var(--ink);
  font-family: var(--font-sans); font-size: 18px;
  -webkit-font-smoothing: antialiased;
  touch-action: none;
}
em { font-style: italic; }
strong { font-weight: 600; }

.atmosphere {
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background:
    radial-gradient(ellipse at 22% 28%, rgba(225, 200, 165, 0.30) 0%, transparent 52%),
    radial-gradient(ellipse at 78% 72%, rgba(180, 165, 140, 0.25) 0%, transparent 56%),
    var(--paper);
}

/* chrome */
.chrome {
  position: fixed; top: 1.25rem; left: 1.25rem; z-index: 30;
  display: flex; gap: 0.5rem;
}
.nav-btn {
  font-family: var(--font-mono);
  font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase;
  background: rgba(254, 254, 250, 0.85);
  backdrop-filter: blur(6px);
  border: 1px solid var(--rule);
  color: var(--ink-soft);
  padding: 0.5rem 0.875rem; border-radius: 999px;
  cursor: pointer; transition: all 0.2s ease;
}
.nav-btn:hover { border-color: var(--ink-soft); color: var(--ink); }
.nav-btn:disabled { opacity: 0.3; cursor: default; }

.chapter-nav {
  position: fixed; top: 1.25rem; right: 1.25rem; z-index: 30;
  display: flex; gap: 0.25rem; align-items: center;
  background: rgba(254, 254, 250, 0.85);
  backdrop-filter: blur(6px);
  padding: 0.4rem 0.6rem; border-radius: 999px;
  border: 1px solid var(--rule);
  font-family: var(--font-mono);
  font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase;
}
.chapter-nav button {
  background: transparent; border: none; color: var(--ink-faint);
  padding: 0.25rem 0.6rem; cursor: pointer; border-radius: 999px;
  font-family: inherit; font-size: inherit; letter-spacing: inherit;
  text-transform: inherit;
  transition: color 0.2s ease, background 0.2s ease;
}
.chapter-nav button:hover { color: var(--ink); }
.chapter-nav button.is-current { color: var(--ink); background: rgba(0,0,0,0.06); }
.chapter-nav .ch-sep { color: var(--rule); padding: 0 0.15rem; }

.progress {
  position: fixed; top: 0; left: 0; right: 0;
  height: 2px; z-index: 40; background: rgba(0, 0, 0, 0.06);
}
.progress__fill {
  height: 100%; width: 0%; background: var(--accent);
  transition: width 600ms var(--ease);
}

.track {
  position: fixed; top: 0; left: 0; right: 0; z-index: 10;
  transform: translate3d(0, 0, 0);
  transition: transform var(--t-scene) var(--ease);
  will-change: transform;
}

.scene {
  position: relative; height: 100vh; width: 100%;
  display: flex; align-items: center; justify-content: center;
  padding: 5rem clamp(1.25rem, 5vw, 4rem);
}
.scene-inner { width: 100%; max-width: 42rem; }
.scene { opacity: 0.06; transition: opacity 600ms var(--ease); }
.scene.is-active { opacity: 1; }

/* intro / koan-illustration */
.scene--intro {
  background-color: var(--paper);
  background-image: url("images/how-it-is-hanging-textless.jpg");
  background-size: auto min(86vh, 70vw);
  background-position: 2% center;
  background-repeat: no-repeat;
  position: relative;
  padding: 0;
}
.scene--intro .scene-inner {
  position: relative; width: 100%; height: 100%;
  max-width: none; padding: 0; margin: 0; text-align: left;
}
.intro-text-column {
  position: absolute;
  top: 50%; right: 4%; transform: translateY(-50%);
  width: 40%; max-width: 34rem; max-height: 82vh;
  overflow: hidden; text-align: center;
  display: flex; flex-direction: column; gap: 2.75rem;
}
.intro-koan-block { margin: 0; }
.intro-koan {
  font-family: var(--font-serif); font-style: italic;
  font-size: clamp(1.15rem, 1.45vw, 1.55rem);
  line-height: 1.5; color: var(--ink); margin: 0 0 1.5rem;
}
.intro-koan p { margin: 0 0 0.875rem; }
.intro-koan p:last-child { margin-bottom: 0; }
.intro-koan-attr {
  font-family: var(--font-mono);
  font-size: 13px; letter-spacing: 0.28em; text-transform: uppercase;
  color: var(--accent); margin: 0;
}
.intro-haiku-block { margin: 0; }
.intro-haiku {
  font-family: var(--font-serif); font-style: italic;
  font-size: clamp(1.5rem, 2.2vw, 2rem);
  line-height: 1.3; color: var(--ink); margin: 0 0 0.875rem;
}
.intro-haiku-attr {
  font-family: var(--font-mono);
  font-size: 12px; letter-spacing: 0.28em; text-transform: uppercase;
  color: var(--user-tag); margin: 0;
}
.intro-enter {
  position: absolute;
  bottom: 2rem; left: 50%;
  transform: translateX(-50%);
  font-family: var(--font-mono);
  font-size: 13px; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--ink-soft); margin: 0;
  animation: bob-centered 2.4s ease-in-out infinite;
}
@keyframes bob-centered {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50%      { transform: translateX(-50%) translateY(6px); }
}

/* chapter transition */
.scene--chapter { background: var(--paper); }
.scene--chapter::after {
  content: ""; position: absolute;
  left: 50%; top: 50%;
  transform: translate(-50%, calc(-50% + 6rem));
  width: 4rem; height: 1px;
  background: var(--accent); opacity: 0.4;
}
.chapter-inner { text-align: center; }
.chapter-numeral {
  font-family: var(--font-serif); font-style: italic;
  font-size: clamp(2.5rem, 5vw, 4rem);
  color: var(--accent); margin: 0 0 1.5rem; line-height: 1;
}
.chapter-title {
  font-family: var(--font-serif);
  font-style: italic; font-weight: 500;
  font-size: clamp(1.5rem, 2.4vw, 2.2rem);
  color: var(--ink); margin: 0; letter-spacing: 0.01em;
}

/* turn */
.scene--turn .scene-inner { max-width: 42rem; }
.speaker {
  font-family: var(--font-mono);
  font-size: 14px; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--ink-soft); margin: 0 0 1.75rem;
}
.scene--turn.turn--user .speaker  { color: var(--user-tag); }
.scene--turn.turn--claws .speaker { color: var(--claws-tag); }
.body {
  font-family: var(--font-serif);
  font-size: clamp(1.25rem, 1.6vw, 1.55rem);
  line-height: 1.55; color: var(--ink);
}
.body p { margin: 0 0 1rem; }
.body p:last-child { margin-bottom: 0; }
.scene--turn.turn--user .body { font-style: italic; }
.scene--turn.scene--break-pattern .body { color: var(--break-color); }
.scene--turn.scene--break-pattern .speaker { color: var(--break-color); }

/* placard */
.scene--placard { background: var(--placard-bg); }
.placard-inner { text-align: center; max-width: 42rem; }
.placard-haiku {
  font-family: var(--font-serif);
  font-style: italic; font-weight: 400;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.4; color: var(--ink); margin: 0 0 2.25rem;
}
.placard-meta {
  font-family: var(--font-mono);
  font-size: clamp(13px, 1.1vw, 15px);
  letter-spacing: 0.18em; text-transform: uppercase; color: var(--ink-soft);
  margin: 0; display: flex; gap: 1.25rem;
  justify-content: center; align-items: baseline; flex-wrap: wrap;
}
.placard-speaker { color: var(--ink-soft); }
.placard--n-strokes .placard-speaker { color: var(--user-tag); }
.placard--claws .placard-speaker     { color: var(--claws-tag); }
.placard--basho .placard-speaker     { color: var(--accent); }
.placard-syll { color: var(--ink-faint); }
.placard-note {
  font-family: var(--font-serif);
  font-style: italic; font-size: clamp(13px, 1vw, 15px);
  letter-spacing: 0.005em; color: var(--ink-soft);
  margin: 1.25rem 0 0; text-align: center;
}

/* commentary */
.scene--commentary {
  background: var(--commentary-bg); color: var(--commentary-ink);
}
.scene--commentary::before {
  content: ""; position: absolute; inset: 0;
  background:
    radial-gradient(ellipse at 30% 40%, rgba(120, 100, 60, 0.25) 0%, transparent 55%),
    radial-gradient(ellipse at 70% 60%, rgba(60, 80, 90, 0.20) 0%, transparent 60%);
  pointer-events: none;
}
.commentary-inner {
  position: relative; z-index: 1; max-width: 50rem; text-align: left;
}
.commentary-eyebrow {
  font-family: var(--font-mono);
  font-size: 13px; letter-spacing: 0.3em; text-transform: uppercase;
  color: rgba(239, 233, 217, 0.6);
  margin: 0 0 2.5rem; text-align: center;
}
.commentary-body {
  font-family: var(--font-serif);
  font-style: italic;
  font-size: clamp(1.4rem, 2vw, 1.9rem);
  line-height: 1.5; color: var(--commentary-ink);
}
.commentary-body p { margin: 0 0 1.25rem; }
.commentary-body p:last-child { margin-bottom: 0; }

/* title */
.scene--title {
  background: var(--commentary-bg);
  color: var(--commentary-ink);
}
.scene--title::before {
  content: ""; position: absolute; inset: 0;
  background:
    radial-gradient(ellipse at 35% 45%, rgba(120, 100, 60, 0.20) 0%, transparent 60%),
    radial-gradient(ellipse at 65% 55%, rgba(80, 90, 100, 0.18) 0%, transparent 65%);
  pointer-events: none;
}
.title-inner {
  position: relative; z-index: 1;
  text-align: center; max-width: 42rem;
}
.title-main {
  font-family: var(--font-serif);
  font-style: italic; font-weight: 400;
  font-size: clamp(2.4rem, 5.5vw, 4.2rem);
  line-height: 1.15;
  margin: 0 0 2.75rem;
  color: var(--commentary-ink);
}
.title-sub {
  font-family: var(--font-mono);
  font-size: clamp(13px, 1.1vw, 15px);
  letter-spacing: 0.3em; text-transform: uppercase;
  color: rgba(239, 233, 217, 0.7);
  margin: 0;
}
.title-enter {
  position: absolute;
  bottom: 2rem; left: 50%;
  transform: translateX(-50%);
  font-family: var(--font-mono);
  font-size: 16px;
  color: rgba(239, 233, 217, 0.55);
  margin: 0;
  z-index: 2;
  animation: bob-centered 2.4s ease-in-out infinite;
}

/* preface */
.preface-inner { max-width: 38rem; text-align: center; }
.preface-body {
  font-family: var(--font-serif);
  font-size: clamp(1.2rem, 1.5vw, 1.5rem);
  line-height: 1.65; color: var(--ink);
}
.preface-body p { margin: 0 0 1.5rem; }
.preface-body p:last-child { margin-bottom: 0; }
.preface-enter {
  position: absolute;
  bottom: 2rem; left: 50%;
  transform: translateX(-50%);
  font-family: var(--font-mono);
  font-size: 13px; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--ink-soft); margin: 0;
  animation: bob-centered 2.4s ease-in-out infinite;
}

/* build / refrain */
.scene--build .scene-inner { max-width: 44rem; }
.build-stack {
  display: flex; flex-direction: column; gap: 1.5rem;
}
.scene--build.center-visible .build-stack {
  transition: transform 700ms var(--ease);
  will-change: transform;
}
.step {
  opacity: 0; transform: translateY(8px);
  transition: opacity 700ms var(--ease), transform 700ms var(--ease);
  pointer-events: none;
}
.step.is-shown {
  opacity: 1; transform: translateY(0); pointer-events: auto;
}
.step-speaker {
  font-family: var(--font-mono);
  font-size: 12px; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--ink-soft); margin: 0 0 0.5rem;
}
.step.step--user .step-speaker  { color: var(--user-tag); }
.step.step--claws .step-speaker { color: var(--claws-tag); }
.step-body {
  font-family: var(--font-serif);
  font-size: clamp(1.15rem, 1.45vw, 1.4rem);
  line-height: 1.55; color: var(--ink);
}
.step.step--user .step-body { font-style: italic; }
.build--refrain .build-stack { gap: 0.75rem; }
.build--refrain .step-body {
  font-size: clamp(0.95rem, 1.1vw, 1.15rem);
}

.build-hint {
  font-family: var(--font-mono);
  font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--ink-faint); text-align: center;
  margin: 2.5rem 0 0;
  opacity: 0;
  transition: opacity 600ms var(--ease) 400ms;
}
.scene--build.is-active .build-hint { opacity: 1; }
.scene--build.is-fully-shown .build-hint { color: var(--ink-soft); }
</style>
</head>
<body>

<div class="atmosphere"></div>

<div class="progress"><div class="progress__fill" id="progress-fill"></div></div>

<nav class="chrome" aria-label="navigation">
  <button class="nav-btn" id="back-btn" aria-label="previous">← back</button>
  <button class="nav-btn" id="next-btn" aria-label="next">next →</button>
</nav>

<nav class="chapter-nav" id="chapter-nav" aria-label="chapters">
__CHAPTER_NAV__
</nav>

<div class="track" id="track">
__SCENES__
</div>

<script>
(() => {
  const track = document.getElementById('track');
  const scenes = Array.from(document.querySelectorAll('.scene'));
  const total = scenes.length;
  const CLICK_ONLY = new Set(__CLICK_ONLY__);
  const BUILD_STEPS = __BUILD_STEPS__;
  const CHAPTER_STARTS = __CHAPTER_STARTS__;
  const TRANSITION_MS = 880;
  const COOLDOWN_MS = 700;
  const WHEEL_THRESHOLD = 30;
  const SWIPE_THRESHOLD = 40;
  const GESTURE_END_MS = 150;

  let activeIdx = 0;
  let lastTransitionAt = 0;
  let wheelAccumulator = 0;
  let gestureLocked = false;
  let gestureEndTimer = null;
  let touchStartY = 0;
  const buildState = new Map();

  const backBtn = document.getElementById('back-btn');
  const nextBtn = document.getElementById('next-btn');
  const chapterButtons = Array.from(document.querySelectorAll('.chapter-nav .chapter-btn'));

  function currentChapter() {
    const ch = parseInt(scenes[activeIdx].dataset.chapter, 10);
    if (scenes[activeIdx].dataset.type === 'chapter-transition') return ch;
    return Number.isFinite(ch) ? ch : 0;
  }

  function applyPosition() {
    track.style.transform = `translate3d(0, ${-activeIdx * window.innerHeight}px, 0)`;
    scenes.forEach((s, i) => s.classList.toggle('is-active', i === activeIdx));
    document.getElementById('progress-fill').style.width = (activeIdx / Math.max(1, total - 1) * 100) + '%';
    backBtn.disabled = activeIdx === 0;
    nextBtn.disabled = activeIdx === total - 1;

    const scene = scenes[activeIdx];
    if (scene && (scene.dataset.type === 'build-page' || scene.dataset.type === 'refrain-build')) {
      const total_steps = BUILD_STEPS[String(activeIdx)];
      let v = buildState.get(activeIdx) ?? 0;
      if (v === 0) {
        v = 1;
        buildState.set(activeIdx, v);
      }
      revealSteps(scene, v, total_steps);
    }

    const ch = currentChapter();
    chapterButtons.forEach(b => b.classList.toggle('is-current', parseInt(b.dataset.chapter, 10) === ch));
  }

  function revealSteps(scene, visibleCount, totalSteps) {
    scene.querySelectorAll('.step').forEach((el, idx) => {
      el.classList.toggle('is-shown', idx < visibleCount);
      el.setAttribute('aria-hidden', idx < visibleCount ? 'false' : 'true');
    });
    scene.classList.toggle('is-fully-shown', visibleCount >= totalSteps);
    if (scene.classList.contains('center-visible')) centerVisibleSteps(scene);
  }

  function centerVisibleSteps(scene) {
    const stack = scene.querySelector('.build-stack');
    if (!stack) return;
    const visible = stack.querySelectorAll('.step.is-shown');
    if (!visible.length) {
      stack.dataset.translateY = '0';
      stack.style.transform = '';
      return;
    }
    const sceneRect = scene.getBoundingClientRect();
    const firstRect = visible[0].getBoundingClientRect();
    const lastRect = visible[visible.length - 1].getBoundingClientRect();
    const visibleMid = (firstRect.top + lastRect.bottom) / 2 - sceneRect.top;
    const targetMid = sceneRect.height / 2;
    const currentY = parseFloat(stack.dataset.translateY || '0');
    const newY = currentY + targetMid - visibleMid;
    stack.dataset.translateY = String(newY);
    stack.style.transform = `translateY(${newY}px)`;
  }

  function isClickOnly(idx) { return CLICK_ONLY.has(idx); }

  function go(targetIdx) {
    if (targetIdx < 0 || targetIdx >= total) return;
    if (targetIdx === activeIdx) return;
    const now = Date.now();
    if (now - lastTransitionAt < COOLDOWN_MS) return;
    lastTransitionAt = now;
    activeIdx = targetIdx;
    applyPosition();
  }

  function tryAdvance(direction) {
    const cur = scenes[activeIdx];
    if (direction > 0 && cur && (cur.dataset.type === 'build-page' || cur.dataset.type === 'refrain-build')) {
      const total_steps = BUILD_STEPS[String(activeIdx)];
      let v = buildState.get(activeIdx) ?? 0;
      if (v < total_steps) {
        v += 1;
        buildState.set(activeIdx, v);
        revealSteps(cur, v, total_steps);
        return;
      }
    }
    go(activeIdx + (direction > 0 ? 1 : -1));
  }

  // wheel
  window.addEventListener('wheel', (e) => {
    e.preventDefault();
    if (gestureEndTimer) clearTimeout(gestureEndTimer);
    gestureEndTimer = setTimeout(() => { gestureLocked = false; wheelAccumulator = 0; }, GESTURE_END_MS);
    if (gestureLocked) return;
    if (Date.now() - lastTransitionAt < COOLDOWN_MS) return;
    if (isClickOnly(activeIdx) && e.deltaY > 0) { wheelAccumulator = 0; return; }
    wheelAccumulator += e.deltaY;
    if (Math.abs(wheelAccumulator) >= WHEEL_THRESHOLD) {
      tryAdvance(wheelAccumulator > 0 ? 1 : -1);
      wheelAccumulator = 0;
      gestureLocked = true;
    }
  }, { passive: false });

  // click
  document.addEventListener('click', (e) => {
    if (e.target.closest('.chrome, .chapter-nav')) return;
    tryAdvance(1);
  });

  // touch
  window.addEventListener('touchstart', (e) => { touchStartY = e.touches[0].clientY; }, { passive: true });
  window.addEventListener('touchmove', (e) => { e.preventDefault(); }, { passive: false });
  window.addEventListener('touchend', (e) => {
    const dy = touchStartY - e.changedTouches[0].clientY;
    if (Math.abs(dy) >= SWIPE_THRESHOLD) tryAdvance(dy > 0 ? 1 : -1);
  });

  // keyboard
  window.addEventListener('keydown', (e) => {
    if (['ArrowDown', 'ArrowRight', 'PageDown', ' '].includes(e.key)) { e.preventDefault(); tryAdvance(1); }
    else if (['ArrowUp', 'ArrowLeft', 'PageUp'].includes(e.key))      { e.preventDefault(); tryAdvance(-1); }
    else if (e.key === 'Home')  { e.preventDefault(); go(0); }
    else if (e.key === 'End')   { e.preventDefault(); go(total - 1); }
    else if (e.key === 'Escape'){ e.preventDefault(); go(0); }
  });

  backBtn.addEventListener('click', (e) => { e.stopPropagation(); tryAdvance(-1); });
  nextBtn.addEventListener('click', (e) => { e.stopPropagation(); tryAdvance(1); });

  chapterButtons.forEach(b => {
    b.addEventListener('click', (e) => {
      e.stopPropagation();
      const ch = parseInt(b.dataset.chapter, 10);
      const target = CHAPTER_STARTS[String(ch)];
      if (Number.isFinite(target)) go(target);
    });
  });

  window.addEventListener('resize', () => {
    track.style.transition = 'none';
    track.style.transform = `translate3d(0, ${-activeIdx * window.innerHeight}px, 0)`;
    document.querySelectorAll('.scene--build.center-visible').forEach(scene => {
      const stack = scene.querySelector('.build-stack');
      if (!stack) return;
      const prev = stack.style.transition;
      stack.style.transition = 'none';
      stack.dataset.translateY = '0';
      stack.style.transform = '';
      void stack.offsetHeight;
      stack.style.transition = prev;
      if (scene.querySelectorAll('.step.is-shown').length) centerVisibleSteps(scene);
    });
    requestAnimationFrame(() => { track.style.transition = ''; });
  });

  applyPosition();
})();
</script>
</body>
</html>
'''

chapter_nav_items = [f'<button class="chapter-btn" data-chapter="0">prologue</button>']
for n, title in CHAPTERS.items():
    chapter_nav_items.append('<span class="ch-sep">·</span>')
    chapter_nav_items.append(f'<button class="chapter-btn" data-chapter="{n}">{escape(title)}</button>')
chapter_nav_html = ''.join(chapter_nav_items)

HTML = HTML.replace('__SCENES__', scenes_html)
HTML = HTML.replace('__CHAPTER_NAV__', chapter_nav_html)
HTML = HTML.replace('__CLICK_ONLY__', json.dumps(click_only_indices))
HTML = HTML.replace('__BUILD_STEPS__', json.dumps({str(k): v for k, v in build_step_counts.items()}))
HTML = HTML.replace('__CHAPTER_STARTS__', json.dumps({str(k): v for k, v in chapter_starts.items()}))

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(HTML)

import os
print(f"Wrote {OUTPUT}")
print(f"Size: {os.path.getsize(OUTPUT)} bytes")
print(f"Total scenes: {len(scenes)}")
counts = {}
for s in scenes:
    counts[s['type']] = counts.get(s['type'], 0) + 1
for k in sorted(counts):
    print(f"  - {k}: {counts[k]}")
print(f"Click-only indices: {click_only_indices}")
print(f"Build step counts: {build_step_counts}")
print(f"Chapter starts: {chapter_starts}")
