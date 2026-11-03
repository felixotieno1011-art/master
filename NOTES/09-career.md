## Docs reading drill — Python `requests`

### Goal
Find how to make a GET request with a 5-second timeout without reading the whole docs page.

### Strategy used
- Ctrl+F for "timeout" (search)
- Checked the TOC (table of contents)
- Found the `requests.get()` method in the API reference

### Code written
```python
import requests
response = requests.get("https://api.github.com/user", timeout=5)
print("Status code:", response.status_code)
print("Response body:", response.text)

**`NOTES/09-career.md`:**

```markdown
## 9.1 Reading Docs — Phase B DONE ✅

Used the "extraction method" to find the exact syntax for a timeout in the Python `requests` docs.
Ran the code, got a 401, and understood that the error response itself points to the docs.

### Core concepts
- **Docs are a reference, not a novel.** You query them, you don't read them cover-to-cover.
- **The 4-step Extraction Method:**
  1. **Ctrl+F** — search for the exact verb/object you need.
  2. **TOC** — use the sidebar to understand categories.
  3. **Quickstart** — find the minimum viable code.
  4. **API Reference** — find exact parameters (often a dictionary-style list).
- **Errors are directions.** API errors often include a `documentation_url` or a specific error code. Paste the error into the docs search.
- **Don't guess.** If you're unsure of a parameter, search the docs for it.

### The drill (what I actually did)
- Wrote `extract.py` to hit `https://api.github.com/user` with a 5s timeout.
- Found the `timeout=5` parameter by searching the `requests` docs.
- Ran it → got 401.
- Realized the 401 is a *success* for the script (the request worked, the API just requires auth).

### Things I saw
- The docs are huge, but the answer was in one line.
- The 401 response gave me the `documentation_url` to fix it.
- A junior might think the code is broken; a pro reads the error and fixes the request.

### My own words (locked in)
- Search keywords or use the TOC/subtopics.
- Docs are a database; you run a query (Ctrl+F) to get the answer.
- Errors are just directions to the right page.

### Connection to other topics
- 1.4 (Command Line) — using `grep` and `man` pages is the same skill.
- 9.3 (Problem Solving) — docs are a primary tool.
- 9.2 (AI Tools) — AI is an alternative to docs, but docs are the source of truth.
- 9.4 (Testing & Debugging) — reading error messages.
