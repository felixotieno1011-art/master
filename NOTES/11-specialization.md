## Security Analyst Role Mapping

### The Job
A Security Analyst (SOC Analyst) sits on the Blue Team. They monitor alerts, investigate incidents, and respond to attacks. They are different from Penetration Testers (Red Team), who break in legally to find bugs.

### How My Projects Map to the Job

**Requirement: Monitor security alerts using SIEM.**
- My Evidence: Built the Cloud-Native SIEM (logs over WebSockets, real-time detection, React dashboard).
- Interview Pitch: "I understand how a SIEM works because I built one from scratch."

**Requirement: Investigate suspicious activity and document incidents.**
- My Evidence: Incident Response (12.24). Investigated a brute-force attack, contained it, wrote an Incident Report.
- Interview Pitch: "I follow the 6-stage IR lifecycle. I contain blast radius, preserve evidence, and write post-mortems."

**Requirement: Assist in threat hunting.**
- My Evidence: Threat Hunting (12.25). Found a hidden admin login by comparing against a baseline.
- Interview Pitch: "I know alerts only catch known-bad patterns. I hunt for TTPs that bypass the rules."

**Requirement: Collaborate with DevOps to secure cloud.**
- My Evidence: Secure Architecture (12.36). Threat-modeled an app, moved DB to private subnet, used least privilege.
- Interview Pitch: "I don't just tell DevOps to 'fix it.' I understand VPCs, IAM roles, and Docker security."

### Lesson
- Don't say "I am a student." Say "I built a SIEM."
- Map your projects directly to the job description.
- Show the interviewer you know *how* the tools work, not just *that* they exist.
## 11.3 Cybersecurity Analyst — Phase B DONE ✅

Mapped my security projects directly to a Junior Security Analyst job description.
Learned the difference between Blue Team (Analyst) and Red Team (Pentester).

### Core concepts
- **Security Analyst (Blue Team):** Monitors, detects, and responds to attacks. Uses SIEM.
- **Penetration Tester (Red Team):** Breaks in legally to find vulnerabilities.
- **SOC (Security Operations Center):** The room where analysts watch the dashboards.
- **Job Mapping:** Taking your projects and matching them to the exact requirements in a job description.
- **The "I built it" advantage:** Saying "I built a SIEM" is stronger than "I used a SIEM."

### The drill (what I actually did)
- Mapped Cloud-Native SIEM to "Monitor security alerts."
- Mapped 12.24 to "Investigate and document incidents."
- Mapped 12.25 to "Assist in threat hunting."
- Mapped 12.36 to "Collaborate with DevOps."

### Things I saw
- Analysts don't usually find bugs; they detect attackers.
- My projects cover the entire SOC workflow.
- I need to stop saying "I'm learning" and start saying "I built."

### My own words (locked in)
- I understand SIEM because I built one.
- Blue Team detects. Red Team attacks.
- Map projects to the job description.
- The best interview answer is "I built it."

### Connection to other topics
- 12.19–12.25 (Blue Team, SIEM, IR, Threat Hunting) — the skills.
- 9.7 (Resume) — where this mapping goes.
- 9.8 (Interview Prep) — how to say it.
- 11.2 (Cloud) — the next specialization.
## 11.2 Cloud Engineer — Phase B DONE ✅

Mapped my cloud training (miniaws, secure architecture) to a Junior Cloud Engineer job description.
Learned the difference between Cloud Engineering (foundation) and DevOps (flow).

### Core concepts
- **Cloud Engineer:** Builds and secures the infrastructure (VPCs, IAM, subnets, databases).
- **DevOps Engineer:** Builds the deployment pipeline (CI/CD, containers, automation).
- **VPC (Virtual Private Cloud):** Your own isolated network in the cloud.
- **Subnet:** A smaller network inside a VPC (public or private).
- **IAM (Identity and Access Management):** Who can do what in the cloud.
- **Least Privilege:** Give only the permissions needed to do the job.
- **Blast Radius:** How much damage one compromised server can cause.
- **IaC (Infrastructure as Code):** Managing infrastructure with code (Terraform, Ansible).

### The drill (what I actually did)
- Mapped `miniaws` (VPC and subnet creation) to "Design and deploy infrastructure."
- Mapped 12.36 (Secure Architecture) to "Ensure cloud security."
- Mapped GitHub Actions and Ansible to "Use Infrastructure as Code."
- Wrote interview pitches for each requirement.

### Things I saw
- Cloud is not about clicking buttons in AWS. It is about architecture.
- The "I built a mini cloud" pitch is incredibly strong.
- Security and Cloud overlap heavily.

### My own words (locked in)
- I understand cloud because I built one and mastered the architecture.
- Cloud builds the foundation. DevOps builds the flow.
- Least privilege is the most important IAM rule.
- Map your projects to the job requirements.

### Connection to other topics
- 2.10 (Cloud Networking) — VPCs and subnets.
- 7.10 (Cloud Platforms) — AWS/GCP/Azure.
- 12.34 (Cloud Security) — securing the cloud.
- 12.36 (Secure Architecture) — blast radius.
- 10.8 (Deploy Everything) — the practical deployment.
## Cloud Engineer Role Mapping

### The Difference (Cloud vs DevOps)
- **Cloud Engineer:** Focuses on the foundation (VPCs, subnets, IAM, security, architecture).
- **DevOps Engineer:** Focuses on the flow (CI/CD, deployment, automation, containers).

### How My Projects Map to the Job

**Requirement: Design and deploy infrastructure (VPCs, subnets).**
- **My Evidence:** Built `miniaws`. Provisioned a VPC (10.1.0.0/16) and a subnet (10.1.1.0/24) using a custom CLI.
- **Interview Pitch:** "I understand cloud networking because I built a VPC and subnet from scratch. I know how CIDR blocks and routing work."

**Requirement: Implement IAM policies.**
- **My Evidence:** Analyzed authentication in POS Lab and designed least-privilege architecture in 12.36.
- **Interview Pitch:** "I know IAM is the most important security layer in the cloud. I always follow least privilege."

**Requirement: Ensure cloud security.**
- **My Evidence:** Threat-modeled an app (12.36) and isolated the database in a private subnet.
- **Interview Pitch:** "I don't just deploy things. I think about blast radius and network isolation."

**Requirement: Use Infrastructure as Code (IaC).**
- **My Evidence:** GitHub Actions (CI/CD) and Ansible playbooks (Honeypot Factory).
- **Interview Pitch:** "I use code to manage infrastructure, not the console. Everything is version-controlled."

**Requirement: Monitor cloud costs.**
- **My Evidence:** Understood pay-as-you-go resource limits in MiniAWS.
- **Interview Pitch:** "Cloud costs money. I check pricing before spinning up instances."

### Lesson
- Don't say "I took a course." Say "I built a mini cloud."
- Cloud Engineers build the foundation. DevOps Engineers build the flow.
- Map your projects to the job description.

## Final Project — The Master README

### The Goal
Turn the `master` repo from a messy learning folder into a professional portfolio directory.

### The Problem
The original README was an internal map (TOC, rules, focus). A recruiter looking at it would think I was on Part 1. It didn't show the 5 major projects.

### The Solution
Rewrote the root `README.md` to act as a "Front Door":
1. Added a "Featured Projects" section with links to FelChat, Zero-Trust Gateway, SIEM, Honeypot, and Recon Platform.
2. Added a "Tech Stack" section (Backend, Security, Cloud, Frontend).
3. Added "Let's Connect" with LinkedIn and Email.
4. Kept the internal links (TOC, NOTES, PRACTICALS) at the bottom for the raw learning journey.

### Lesson
- A repo is not just a storage box. It is a presentation.
- The root README is the most important file. It is the picture of all things.
- Show the highlight reel first; let them dig into the code second.
## 11.7 Final Project — Phase B DONE ✅

Upgraded the root `master` README to act as a professional portfolio directory.
Turned a messy learning repo into a recruiter-friendly showcase.

### Core concepts
- **The Master README:** The "Front Door" to the repository.
- **Highlight Reel:** Showing the 5 best projects first, instead of the 182 folders.
- **The Map:** A clear index of TOC, NOTES, PRACTICALS, and JOURNAL.
- **Repository as a Portfolio:** A GitHub repo isn't just storage; it's a presentation.

### The drill (what I actually did)
- Replaced the internal-only README with a professional one.
- Added "Featured Projects" with links and descriptions.
- Added "Tech Stack" and "Let's Connect".
- Kept the internal links at the bottom for the learning journey.

### Things I saw
- The old README said "Part 1 — Foundations", which would confuse a recruiter.
- The new README says "I build secure systems" and links to 5 projects.
- A recruiter can now see the picture of all things in 10 seconds.

### My own words (locked in)
- The README is the picture of all things.
- Show the highlight reel first.
- A repo is a presentation, not just a storage box.

### Connection to other topics
- 9.5 (Portfolio) — the live site version.
- 9.6 (GitHub Profile) — the profile README.
- 10.8 (Deploy Everything) — the live apps.
- 11.1 (DevOps), 11.2 (Cloud), 11.3 (Security) — the tracks showcased.
