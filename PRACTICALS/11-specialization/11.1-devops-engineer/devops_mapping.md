# Job Mapping — DevOps Engineer

### Requirement 1: Build and maintain CI/CD pipelines.
- **My Evidence:** Built a CI/CD pipeline in the Honeypot Factory using GitHub Actions. It automatically builds the Docker image, runs the Ansible playbook, and deploys the honeypot whenever I push to `main`.
- **Interview Pitch:** "I understand CI/CD because I built one. I know how to write GitHub Actions workflows, how to pass secrets securely, and how to fail a pipeline if a test fails."

### Requirement 2: Write Infrastructure as Code (IaC).
- **My Evidence:** Used Ansible in the Honeypot Factory to configure the server and deploy the Cowrie honeypot.
- **Interview Pitch:** "I use code to manage servers. I don't SSH into a machine and type commands manually. I write Ansible playbooks so the infrastructure is version-controlled and repeatable."

### Requirement 3: Manage Docker containers.
- **My Evidence:** Built a custom Docker image for Cowrie (the honeypot). Pushed it to GHCR (GitHub Container Registry). Ran it in a container.
- **Interview Pitch:** "I know how to build a Dockerfile, push it to a registry, and run it in any environment. I understand the difference between an image and a container."

### Requirement 4: Automate deployments.
- **My Evidence:** The entire Honeypot Factory deployment is automated. From `git push` to a running honeypot, with zero manual steps.
- **Interview Pitch:** "I automate everything. If I have to do a task twice, I write a script for it."
