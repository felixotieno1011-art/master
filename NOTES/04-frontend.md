### 4.1 HTML5 — Phase B DONE ✅

Built my first HTML page (index.html). Name, paragraph, list, link.

### Core concepts
- HTML = HyperText Markup Language — marks content with TAGS
- Element = opening tag + content + closing tag: <p>hello</p>
- Attribute = extra info inside opening tag: <a href="...">
- Structure: <!DOCTYPE html> → <html> → <head> + <body>
- <head> = info about page (title)
- <body> = what you see

### Key tags I used
- <h1>, <h2> = headings
- <p> = paragraph
- <ul>, <li> = bullet list, list item
- <a href=""> = link

### My nyama choma analogy
- A menu has structure: header, body, footer, sections, items
- HTML tags = labels that say what each part IS
- No tags = jumble of text. With tags = browser knows what's what

### Real commands I ran
- nano index.html
- termux-open index.html

### Things I saw
- Page rendered in browser: big name, paragraph, bullet list, clickable link
- Removed </ul> → NO visible change (browser guessed and fixed silently)
- Added <img src="nothing.jpg"> → broken-image icon appeared (visible failure)

### My own words (locked in)
- HTML is not a programming language — it's a MARKUP language
- Browsers are forgiving with STRUCTURE (missing tags) but can't fix MISSING CONTENT
- Python crashes loudly; HTML fails silently — so write carefully
- Every webpage is HTML underneath — the skeleton
### 4.2 CSS3 — Phase B DONE ✅

Styled my HTML page: green h1, gray background, white list card, gold link.

### Core concepts
- CSS = Cascading Style Sheets — style the HTML structure
- Rule = selector + property + value
  h1 { color: green; }
  ↑     ↑       ↑
  who   what    how much
- Where CSS goes: inline (tag), internal (<style> in head), external (.css file)
- Common properties: color, background, font-size, padding, margin, border, border-radius, text-align

### My tailor analogy
- HTML = the person. CSS = the tailor dressing them.
- Selector = who. Property = what. Value = how much.

### Real commands I ran
- nano index.html
- termux-open index.html
- cat index.html

### Things I saw
- Full styled page in browser (green h1, gray bg, list card, gold link)
- Missing colon in CSS → no change (browser guessed)
- Missing closing brace → no change (browser merged/guessed)
- cat showed TWO documents stacked in one file → real bug
- After fixing: one clean document

### My own words (locked in)
- HTML and CSS are FORGIVING — they don't crash like Python
- Forgiving = easy to write, hard to debug (nothing yells)
- When "nothing changes," cat the file — the bug is rarely where you think
- Broken-but-working files bite you later. Fix them now.
- Two documents stacked = browser merges them. Dangerous.
## 4.3 Responsive Design — Phase B DONE ✅

Added viewport meta tag + media queries to Felix's page.
Confirmed viewport tag changes phone rendering.
Media queries verified in code (visual diff needs laptop DevTools).

### Core concepts
- Responsive design = one HTML page that adapts to every screen size
- Without it → "one size fits all" → fits nobody
- Three tools:
  1. Viewport meta tag — tells the browser the real device width
  2. Media queries — CSS that only applies at certain widths
  3. Mobile-first approach — start small, add for bigger

### Viewport meta tag
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  - Without it: mobile browsers fake a ~980px viewport and zoom out
  - With it: browser uses the real device width → readable text
  - The SINGLE most important line for mobile rendering

### Media queries
  /* Mobile default */
  body { padding: 30px; }

  /* Tablet and up */
  @media (min-width: 768px) {
    body { padding: 60px; }
  }

  /* Desktop and up */
  @media (min-width: 1024px) {
    body { padding: 80px; max-width: 900px; margin: 0 auto; }
  }

### Mobile-first vs desktop-first
- Mobile-first (modern standard):
  - Default CSS = phone
  - @media (min-width: ...) adds for larger screens
  - Pros: smaller CSS, easier to add than remove, Google SEO
- Desktop-first (legacy):
  - Default CSS = desktop
  - @media (max-width: ...) overrides for smaller screens

### Common breakpoints
- 0–640px     phone
- 640–768px   large phone / small tablet
- 768–1024px  tablet
- 1024–1280px laptop
- 1280px+     desktop

### My own words (locked in)
- One page → different layouts → fits every screen
- Viewport tag = stops the phone from faking a desktop
- Media query = "if screen is at least X wide, use these styles"
- Mobile-first = start with the phone layout, add for bigger screens
- On a phone, "desktop mode" simulates width but zooms out to fit
  → looks smaller, not actually broken
- The real test needs DevTools or a laptop
- I understand the theory — the visual click will come on a laptop

### Files changed
- ~/master/PRACTICALS/04-frontend/4.1-html5/index.html
  Added viewport meta tag + @media (min-width: 768px) + @media (min-width: 1024px)
