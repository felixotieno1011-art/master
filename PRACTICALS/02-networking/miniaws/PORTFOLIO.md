# Portfolio Project — 3-Tier VPC Architecture

## Summary
I designed and deployed a production-grade 3-tier VPC in AWS (simulated via MiniAWS).

This is the same architecture pattern used by banks, fintechs, and SaaS
companies for production workloads on AWS.

## Architecture

### VPC
- CIDR: 10.10.0.0/16
- Region: af-south-1 (Cape Town)
- 65,536 total IPs

### Subnets (3 tiers)
| Tier | CIDR | Purpose |
|------|------|---------|
| Public | 10.10.1.0/24 | Load balancers, internet-facing |
| App | 10.10.2.0/24 | App servers, outbound-only |
| DB | 10.10.3.0/24 | Databases, fully isolated |

### Network Components
- **Internet Gateway (IGW):** Attached to VPC, route in public RT
- **NAT Gateway:** In public subnet, provides outbound for app tier
- **Route tables:** 4 (public, app, db, main)
  - Public: `0.0.0.0/0 -> IGW` (reachable from internet)
  - App: `0.0.0.0/0 -> NAT` (outbound only)
  - DB: `local` only (fully isolated)
  - Main: `local` only (safe default for new subnets)

### Security Groups (tiered isolation)
| SG | Tier | Inbound Rule |
|----|------|--------------|
| web-sg | Public | HTTP (80), HTTPS (443) from internet |
| app-sg | App | Port 8080 from web-sg (SG reference) |
| db-sg | DB | Port 5432 from app-sg (SG reference) |

**Key design:** The DB tier only accepts traffic from instances that have the
App SG. Even a compromised web server cannot reach the DB directly.

## Security Chain

## Design Principles Applied
1. **Tiered isolation** — Each tier can only reach the next tier.
2. **Defense in depth** — Subnet + Route table + Security Group layers.
3. **Deny by default** — SGs allow nothing unless explicitly permitted.
4. **SG references over CIDRs** — More secure than IP-based rules.
5. **Safe defaults** — Main route table has no internet route.

## How It Was Built
- 100% from the AWS CLI (real AWS syntax)
- Typed every command manually (not copy-pasted)
- Understood every layer before moving on
- Fixed multiple bugs in the simulation tool (MiniAWS) while building

## Skills Demonstrated
- AWS VPC design
- Subnet planning (CIDR math, reserved IPs)
- Route table configuration (longest-prefix match)
- NAT Gateway setup for private subnets
- Security Group design with SG-to-SG references
- Tiered network isolation (defense in depth)

## Why This Matters
This is the same pattern that banks, e-commerce sites, and SaaS platforms
use to protect production data. The DB tier isolation means that even if an
attacker compromises the public-facing load balancer, they cannot reach
customer data.

## Next Steps
- Deploy the same architecture on real AWS (free tier)
- Add EC2 instances to each tier
- Add an Application Load Balancer in the public tier
- Set up monitoring (CloudWatch)
- Automate the deployment with Terraform or CloudFormation
