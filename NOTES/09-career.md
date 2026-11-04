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
## GitHub Profile Upgrade

### What I did
- Created a special profile repo (`felixotieno1011-art/felixotieno1011-art`)
- Added a custom README with:
  - Title & tagline
  - Links to Portfolio, Resume, LinkedIn
  - Tech stack badges (Python, FastAPI, Node.js, Redis, PostgreSQL, Docker, etc.)
  - Table of 5 featured projects
- Pinned the 5 best repos to the profile.

### Why it matters
- Recruiters don't read through 20 repos. They look at the Pinned section.
- The Profile README acts as a landing page.
- Clean presentation = professional.
- The badges show tech stack at a glance.

## 9.6 GitHub Profile — Phase B DONE ✅

Built a custom GitHub Profile README using the username special repo.
Pinned the 5 best projects and cleaned up the presentation.

### Core concepts
- **Profile README:** A repo named exactly after your username shows up on your profile. It's your GitHub landing page.
- **Pinned Repos:** The 6 projects featured at the top of your profile. Curate these — don't let GitHub choose.
- **Badges:** Shields.io badges give a visual tech stack (e.g., Python, Docker, Redis).
- **Clean Repos:** Archive old practice repos (`git_test`, `docker-basics`) so they don't clutter the list.
- **Bio:** Short, keyword-rich, professional. No "learning to code."

### The drill (what I actually did)
- Created `felixotieno1011-art/felixotieno1011-art`.
- Wrote a README with intro, links, badges, and a table of 5 projects.
- Pushed it to GitHub.
- Pinned `felchat`, `zero-trust-gateway`, `cloud-native-siem`, `honeypot-factory`, `recon-platform`.

### Things I saw
- The README rendered perfectly with the badges.
- It immediately makes the profile look 10x more professional than a list of repos.
- A recruiter can see my best work in 3 seconds without scrolling.

### My own words (locked in)
- Neatly arranged is the goal.
- Profile README = the shop window.
- Pinned repos = the front counter.
- Badges = quick visual proof of skills.

### Connection to other topics
- 9.5 (Portfolio) — the GitHub profile complements the live portfolio site.
- 9.7 (Resume & LinkedIn) — they all link to each other.
- 9.6 is the GitHub side of the same story.


**`NOTES/09-career.md`:**

```markdown
## 9.2 AI Tools — Phase B DONE ✅

Used AI to review vulnerable code, identify a security flaw, and produce a fix.
Practiced the "exoskeleton" mindset — AI as a force multiplier, not a replacement for understanding.

### Core concepts
- **Crutch vs. Exoskeleton:** Copying AI code you don't understand vs. using AI to review/explain/test.
- **AI in security:** Great for code review, finding flaws, generating test cases.
- **AI in debugging:** Give it the error + stack trace, not just "it doesn't work."
- **The 2 AM test:** If it breaks and the AI is gone, can you fix it?
- **Prompting for depth:** Ask "Why is this vulnerable?" not just "Fix it."

### The drill (what I actually did)
- Wrote a deliberately vulnerable SQL function.
- Asked AI to review it.
- AI found the SQL injection and provided the parameterized fix.
- I retyped the fix myself and verified why it works.

### Things I saw
- The AI spotted the flaw immediately.
- The fix was small (one placeholder) but conceptually huge.
- Retyping the fix made the logic stick.

### My own words (locked in)
- Junior dev can't understand if code breaks or crashes later.
- AI is a rubber duck that never sleeps.
- Use AI to explain, not to skip understanding.
- If you can't explain it, you don't own it.

### Connection to other topics
- 9.1 (Reading Docs) — AI is an alternative to docs, but docs are the source of truth.
- 9.3 (Problem Solving) — AI is a tool in the problem-solving toolkit.
- 9.4 (Testing & Debugging) — AI can generate tests.
- 12.15 (Web Hacking) — the SQLi you just found with AI is the same one from DVWA.
### The "10,000 Lines" Rule (Debugging AI vs. Human Code)
- Writing code yourself gives you a **mental map** of the system. You know where the likely failure points are.
- Copying AI code gives you a **maze**. When it breaks, you are a stranger in your own codebase.
- At 2 AM, nobody reads 10,000 lines. You use **logs, stack traces, and monitoring** to jump straight to the bug.
- The rule: If you use AI to write a feature, read every line, add comments in your own words, and break it on purpose. If you can't explain it, it's too big.
