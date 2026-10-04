## Real VPN (WireGuard/OpenVPN)
- Status: PARKED — needs hardware we don't have
- Why parked:
  * Needs a real server (VPS ~$5/month)
  * Needs kernel-level TUN/TAP (blocked on Android)
  * Needs root or a real Linux machine
- What we DID do on phone:
  * Built mini_proxy.py (HTTP forwarding)
  * Built mini_tunnel.py (base64 wrapping)
  * Understood proxy vs VPN vs tunneling conceptually
- Resume at: After Topic 7.1 (Linux Server Basics)
- Future plan:
  * Rent a VPS (DigitalOcean $5/month)
  * Set up WireGuard server + client
  * Connect from phone
## Cloud Computing Deep Dive
- Status: PARKED — needs dedicated time
- Why: Bigger than I imagined. Deserves its own focused journey.
- What I already know:
  * Cloud = rented computers in data centers
  * Big 3: AWS, Azure, GCP
  * Regions + Availability Zones (redundancy)
  * VPCs, subnets, public/private split
  * Firebase runs on GCP
- What I want to learn deeply:
  * Real AWS console (EC2, S3, IAM, RDS, Lambda)
  * Real Azure (VMs, Resource Groups, Storage)
  * Real GCP (Compute, Cloud Storage, BigQuery)
  * Multi-cloud networking
  * Cost optimization
  * Kubernetes, Terraform, CI/CD
- Plan: Dedicated 2-3 week focused learning block
- Resume at: Topic 7.10 (Cloud Platforms) — will do real hands-on then
- Optional: Build mini-AWS/Azure/GCP simulators first
