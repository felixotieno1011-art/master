# Job Mapping — Security Analyst

### Requirement 1: Monitor security alerts using SIEM.
- **My Evidence:** Built the **Cloud-Native SIEM**. It ingests logs over WebSockets, runs real-time detection rules, and visualizes alerts on a React dashboard.
- **Interview Pitch:** "I understand how a SIEM works because I built one from scratch. I know how logs are ingested, how rules are written, and how alerts are triaged."

### Requirement 2: Investigate suspicious activity and document incidents.
- **My Evidence:** Incident Response (12.24). I investigated a brute-force attack in a mock log, contained it by disabling the account, and wrote an Incident Report.
- **Interview Pitch:** "I follow the 6-stage IR lifecycle. I don't just panic when an alert fires; I contain the blast radius, preserve evidence, and write a post-mortem."

### Requirement 3: Assist in threat hunting.
- **My Evidence:** Threat Hunting (12.25). I hunted for hidden anomalies in an auth log by comparing against a baseline and found an admin login from a new IP.
- **Interview Pitch:** "I know that alerts only catch known-bad patterns. I hunt for the TTPs that bypass the rules."

### Requirement 4: Collaborate with DevOps to secure cloud.
- **My Evidence:** Secure Architecture (12.36). I threat-modeled an app and reduced the blast radius by moving the DB to a private subnet with least-privilege access.
- **Interview Pitch:** "I don't just tell DevOps to 'fix it.' I understand VPCs, IAM roles, and Docker security."
