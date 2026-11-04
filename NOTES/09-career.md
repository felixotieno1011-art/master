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

## Mock Interview Drill

### Q1: Walk me through your Zero-Trust Gateway architecture.
**My initial answer:** "I built it for a portfolio. It verifies requests and detects anomalies. Works on my machine."
**Feedback:** Sounded like a hobbyist. Missed the "how" and the "result".
**Pro Answer:** "Solves the problem of securing backend microservices. Uses JWT for identity, custom WAF for payload filtering, Redis for rate limiting. 69 automated tests. Containerized with Docker for any cloud."

### Q2: Tell me about learning a new tech quickly.
**My initial answer:** "FelChat was slow. I remembered Groq and used it. It responds fast."
**Feedback:** Good skeleton, but needs metrics and technical depth.
**Pro Answer:** "FelChat had 5-10s latency. I needed low-latency. I researched Groq's LPU architecture, read their docs, swapped the provider. Result: dropped latency to <1s. Learned that infra matters as much as code."

### Q3: Secure a Kubernetes cluster in the cloud.
**My initial answer:** "Pod security and authentication."
**Feedback:** Right concepts, but too brief.
**Pro Answer:** "Three layers: 1) Network (VPC, Network Policies), 2) Identity (RBAC, OIDC, IAM roles), 3) Workload (Pod Security Standards, image scanning). Priority: Secrets Management."

### Lesson
- Never say "it works on my machine." Say "it's containerized."
- Use STAR for behavioral questions.
- For technical questions, list the layers/concepts you know, and be honest about what you haven't implemented.
## 9.8 Interview Prep — Phase B DONE ✅

Practiced translating hands-on project work into professional interview answers.
Used the STAR method and learned how to structure complex technical answers.

### Core concepts
- **STAR Method:** Situation, Task, Action, Result. Essential for behavioral questions.
- **Show, don't tell:** Instead of "it detects anomalies," say "it filters SQLi and XSS using a custom WAF."
- **Use metrics:** "Reduced latency from 5s to <1s" is better than "it's fast."
- **The "I don't know" test:** Don't bluff. Break the problem into layers (Network, Identity, Workload) and explain your approach.
- **"Works on my machine" is banned.** Say "it's containerized with Docker" or "it runs on any environment with X."
- **Own the action:** Don't say "AI fixed it." Say "I used AI to research, then I implemented the fix."

### The drill (what I actually did)
- Answered 3 mock interview questions.
- Q1 (Zero-Trust Gateway): Learned to focus on the 'how' and the 'result' instead of the 'why I built it'.
- Q2 (Learning quickly): Learned to name the specific tech (Groq LPU) and use metrics.
- Q3 (K8s security): Learned to break a big topic into layers (Network, Identity, Workload).

### Things I saw
- My initial answers were honest but lacked structure.
- Adding specific tech names (JWT, Redis, RBAC) makes a huge difference.
- Structuring answers (STAR) makes you sound senior.

### My own words (locked in)
- Never say "it works on my machine."
- Use STAR. Give the result.
- Break complex questions into layers.
- Be honest about what you haven't built, but explain how you would approach it.

### Connection to other topics
- 9.5 (Portfolio) — the projects you talk about.
- 9.6 (GitHub) — the proof you link to.
- 9.7 (Resume & LinkedIn) — the first impression.
- 7.11 (Kubernetes) — the tech for Q3.
- 12.35 (Container Security) — the security concepts for Q3.

## 9.7 Resume & LinkedIn — Phase B DONE ✅

Optimized LinkedIn to target Security Engineer roles.
Removed confusing experience, added real projects, and fixed keyword skills.

### Core concepts
- **The 6-Second Scan:** Layout, Terminologies (keywords), and Projects.
- **ATS (Applicant Tracking Systems):** Robots scan for exact keywords before humans see the resume.
- **Narrative Control:** Every item on the profile must support the role you want.
- **The "Experience Trap":** Unrelated jobs (resort, accounting) dilute the message. Projects are better proof.
- **LinkedIn Projects:** A hidden feature that lets you showcase GitHub repos with descriptions.

### The drill (what I actually did)
- Audited the LinkedIn profile and found it was confusing.
- Deleted the resort/accounting job.
- Rewrote Headline and About with target keywords.
- Added 4 major projects with GitHub links.
- Swapped accounting skills for tech skills.

### Things I saw
- A mixed profile makes the recruiter guess what you do.
- A focused profile makes you look like a specialist.
- Links to live projects are the strongest proof of skill.

### My own words (locked in)
- Don't list accounting on a security profile.
- Headline must match the job title you want.
- Projects are the new experience for self-taught devs.
- Use real screenshots, not fake AI graphics.

### Connection to other topics
- 9.5 (Portfolio) — the live site linked on LinkedIn.
- 9.6 (GitHub) — the proof behind the projects.
- 9.8 (Interview Prep) — you can now talk about the projects you listed.

## Communication Drill — The Manager Update

### The Scenario
Project is due tomorrow. Found a critical security bug (SQL injection) that takes 3 hours to fix. Only 1 hour left.

### My First Draft (Junior)
"The project is moving fine and it's almost complete, but due to a bug we identified, we request 2 more hours to debug it."
*Feedback: Downplayed the risk. Called a critical flaw a "bug". Sounds uncertain.*

### My Second Draft (Better)
"Our project is in completion phase, but there is issue where the project can expose database secrets. We've been trying to fix it, if you give us like 3 hours we may solve it."
*Feedback: Much better business impact. But still sounds passive ("trying", "may solve").*

### The Senior Version (BLUF)
"Status: Feature-complete.
Impact: Found a security flaw that could expose database credentials.
Action: Patching the flaw and running the security test suite.
Request: Need ~3 hours to verify the fix. Deployment pushed to tomorrow at 10 AM."

### Lesson
- Use BLUF (Bottom Line Up Front).
- Translate tech (SQLi) to business impact (exposed secrets).
- Be definitive ("approximately 3 hours", not "like 3 hours").
- Take ownership ("I am patching", not "we are trying").
## 9.11 Communication — Phase B DONE ✅

Practiced translating technical problems into professional updates for managers.
Learned the BLUF method and how to communicate business impact.

### Core concepts
- **BLUF (Bottom Line Up Front):** Status → Impact → Action → Request.
- **Translate Tech to Business:** "SQL injection" = "exposed database secrets." "Server down" = "users cannot access the platform."
- **Be definitive:** Use precise timelines ("3 hours", not "like 3 hours").
- **Take ownership:** "I am patching it" instead of "we are trying."
- **Don't hide bad news:** Managers hate surprises. Tell them the risk immediately and give them the solution.

### The drill (what I actually did)
- Roleplayed a scenario: deadline tomorrow, found a critical bug.
- Wrote a first draft that downplayed the risk.
- Rewrote it using BLUF and business impact.
- Learned to provide a concrete new deadline.

### Things I saw
- A "bug" sounds minor to a manager. A "security flaw that exposes credentials" sounds critical.
- Asking for time is better if you also provide the new delivery time.
- The difference between junior and senior is not just code; it's how they communicate.

### My own words (locked in)
- Don't say "bug" when it's a security flaw.
- BLUF: Status, Impact, Action, Request.
- "Like 3 hours" sounds unsure. Say "approximately 3 hours."
- Take responsibility and provide a solution.

### Connection to other topics
- 9.8 (Interview Prep) — STAR method for behavioral questions.
- 12.24 (Incident Response) — writing clear incident reports.
- 8.4 (Secure Coding) — the SQL injection you found.
- 9.7 (Resume) — communicating your skills clearly.
