# Job Mapping — Cloud Engineer

### Requirement 1: Design and deploy cloud infrastructure (VPCs, subnets).
- **My Evidence:** Built a custom MiniAWS CLI. Provisioned a VPC (10.1.0.0/16) and a subnet (10.1.1.0/24) entirely from the command line. 
- **Interview Pitch:** "I understand cloud networking because I built a VPC and subnet from scratch using a CLI. I know how CIDR blocks and routing work."

### Requirement 2: Implement IAM policies.
- **My Evidence:** In the POS Lab, I analyzed how the app authenticated users. I understand IAM roles, least privilege, and how to prevent privilege escalation (12.36).
- **Interview Pitch:** "I know that IAM is the most important security layer in the cloud. I always follow the principle of least privilege."

### Requirement 3: Ensure cloud security.
- **My Evidence:** Threat-modeled a cloud app (12.36). Moved the database to a private subnet to reduce the blast radius. 
- **Interview Pitch:** "I don't just deploy things. I think about what happens if a server gets compromised. I isolate resources."

### Requirement 4: Use Infrastructure as Code (IaC).
- **My Evidence:** Used GitHub Actions for CI/CD and wrote Ansible playbooks in the Honeypot Factory.
- **Interview Pitch:** "I use code to manage infrastructure. I don't click buttons in the console; I write scripts that can be version-controlled."

### Requirement 5: Monitor cloud costs.
- **My Evidence:** In the MiniAWS, I understand how resources (like EC2 instances and buckets) consume state and cost money.
- **Interview Pitch:** "I understand that cloud is pay-as-you-go. I always check the pricing of an instance before I spin it up."
