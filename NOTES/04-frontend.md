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
