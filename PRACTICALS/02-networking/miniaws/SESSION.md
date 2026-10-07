# Session Log — MiniAWS

## Session: 2026-10-05 — Chapter 5 Complete ✅
**Goal:** Give the private subnet outbound-only internet access. ✅ Achieved.

### Current Infrastructure
- VPC:            vpc-d49769ed81d046a79  (10.0.0.0/16)
- Public subnet:  subnet-497b38a8f4f544dd9  (10.0.1.0/24, public-1)
- Private subnet: subnet-3277d9a129b2472c8  (10.0.2.0/24, private-1)
- IGW:            igw-2c9fb7e69a094c6aa  (attached)
- NAT Gateway:    nat-0c2a82ceb0074d598  (in public-1, public IP 203.0.113.10)
- Main RT:        rtb-ca302df68d6b427e9  (local + 0.0.0.0/0 → IGW)
- Private RT:     rtb-3fcb0396fad94fb3b  (local + 0.0.0.0/0 → NAT)
                  associated with subnet-3277d9a129b2472c8

### Chapter 5 — Progress
- [x] Create VPC
- [x] Create public + private subnets
- [x] Create + attach Internet Gateway
- [x] Add internet route to main RT
- [x] Create NAT Gateway in public subnet
- [x] Create private route table
- [x] Add NAT route to private RT
- [x] Associate private RT with private subnet
- [x] Verify routes

### Vocabulary
- VPC = private network in AWS
- Subnet = slice of the VPC (public faces internet, private hidden)
- IGW = door to the internet (two-way traffic)
- NAT Gateway = mail slot (outbound only, has its own public IP)
- Route table = signpost telling packets where to go
- Main route table = auto-created with VPC, used by default
- Private route table = custom, associated with private subnets

### Next Chapter (6)
- Route tables deeper: peering, VPN, transit gateway
- Multi-tier architectures
- Security Groups (firewalls for instances)

---

## Session: 2026-10-06 — Help System Added
**Goal:** Add `--help` support to all commands. ✅ Achieved.

### What we built
- `core/help_text.py` — help text for ~30 commands
- Wrapper: detects `--help`, looks up, prints, exits
- Every command now self-documents

### Example

### Why this matters
- Future-you can look up syntax without leaving Termux
- Matches real AWS behavior (per-command help)
- Makes MiniAWS feel like a real CLI tool

---

## Session: 2026-10-06 (continued) — Chapters 6 & 7 Complete
**Goal:** Route tables deep dive + Security Groups. ✅ Achieved.

### Chapter 6 — Route Tables Deep Dive
- Longest-prefix match (most specific wins)
- Default route (0.0.0.0/0) catches the rest
- VPC Peering, VPN, Transit Gateway concepts (not yet in MiniAWS)
- Peering: pcx-xxx route between VPCs
- VPN: vgw-xxx route to on-premises
- TGW: hub for many VPCs

### Chapter 7 — Security Groups
- Built `core/sg.py` and `sg_cli.py`
- Security Groups = per-instance firewalls
- Default: deny inbound, allow outbound
- Rules: protocol + port + CIDR + direction
- Duplicate prevention
- Same port, different CIDR = separate rules

### Security Groups in MiniAWS
- SG created: sg-a9148d9c50904ccdb (web-sg)
- VPC: vpc-d49769ed81d046a79
- Inbound rules:
  - tcp 80  from 0.0.0.0/0
  - tcp 443 from 0.0.0.0/0
  - tcp 22  from 192.168.0.0/16
  - tcp 22  from 10.0.0.0/8
- Outbound: allow all

### Commands added
- aws ec2 create-security-group --group-name <n> [--description <d>] [--vpc-id <v>]
- aws ec2 describe-security-groups [--vpc-id <v>]
- aws ec2 delete-security-group <sg-id>
- aws ec2 authorize-security-group-ingress --group-id <sg> --protocol <tcp> --port <n> [--cidr <c>]
- aws ec2 revoke-security-group-ingress --group-id <sg> --protocol <tcp> --port <n> [--cidr <c>]

### Next Chapter (8)
- Subnet Math (AWS reserved IPs: .0-.3 + .255 per subnet)

---

## Session: 2026-10-06 (continued) — s3api Added
**Goal:** Add `aws s3api` commands matching real AWS. ✅ Achieved.

### What we built
- `core/s3api.py` — low-level S3 operations
- `s3api_cli.py` — CLI wrapper
- Wrapper: routes `s3api` commands
- Commands: list-buckets, create-bucket, list-objects, put-object,
  delete-object, delete-bucket, head-bucket

### Difference from aws s3
- `aws s3` = high-level, human-friendly (mb, cp, ls, rm, rb)
- `aws s3api` = low-level, matches API calls, JSON output by default

### Example
EOF

---

## Session: 2026-10-06 (continued) — Clean Slate + Flag Fixes
**Goal:** Clean MiniAWS + fix placeholder issues. ✅ Achieved.

### What we cleaned
- Deleted all VPCs, subnets, NATs, IGWs, route tables, SGs
- MiniAWS is now empty (fresh start)

### What we fixed
- `aws ec2 delete-vpc --vpc-id <id>` now works (real AWS syntax)
- `aws ec2 delete-subnet --subnet-id <id>` now works
- Both flag AND positional syntax supported

### What's left in MiniAWS
- Instances: monitor-test (running), web-server (running), web-server (terminated)
- IAM: alice, bob, proving-user
- CloudWatch: some alarms
- Everything else: clean

### Ready for Chapter 8
- Subnet Math (AWS reserved IPs: 5 per subnet)

---

## Session: 2026-10-06 (evening) — Lambda Added
**Goal:** Add AWS Lambda (serverless functions) to MiniAWS. ✅ Achieved.

### What we built
- `core/lambda_svc.py` — Lambda logic (real Python execution)
- `lambda_cli.py` — CLI wrapper
- Wrapper: routes `lambda` service
- Help text updated

### Commands
- `aws lambda create-function --function-name <n> --zip-file <path.py>`
- `aws lambda list-functions`
- `aws lambda invoke --function-name <n> [--payload '<json>']`
- `aws lambda delete-function --function-name <n>`

### How it works
- Stores Python code in `state/lambda/functions/<name>.py`
- Metadata in `<name>.json`
- On invoke: actually runs the code in a sandbox
- Captures stdout, return value, execution time
- Returns realistic AWS-style response

### Tested
- Created `hello` function that takes `{"name": "X"}` and returns "Hello, X!"
- Invoked with no payload → "Hello, World!"
- Invoked with `{"name": "Kelvin"}` → "Hello, Kelvin!"
- Deleted successfully

### Test results
- ✅ create-function works
- ✅ list-functions works (table + JSON)
- ✅ invoke works (real execution)
- ✅ delete-function works

---

## Session: 2026-10-06 (evening) — Lambda + DynamoDB Added
**Goal:** Add serverless + NoSQL to MiniAWS. ✅ Achieved.

### Lambda (serverless functions)
- `core/lambda_svc.py`, `lambda_cli.py`
- `aws lambda create-function --function-name <n> --zip-file <path.py>`
- `aws lambda list-functions`
- `aws lambda invoke --function-name <n> [--payload '<json>']`
- `aws lambda delete-function --function-name <n>`
- **Real execution:** runs Python code with event + context
- Captures stdout, return value, duration

### DynamoDB (NoSQL key-value store)
- `core/dynamodb.py`, `dynamodb_cli.py`
- `aws dynamodb create-table --table-name <n> --key-schema '<attr>:S'`
- `aws dynamodb list-tables`
- `aws dynamodb put-item --table-name <n> --item '<json>'`
- `aws dynamodb get-item --table-name <n> --key '<value>'`
- `aws dynamodb delete-item --table-name <n> --key '<value>'`
- `aws dynamodb scan --table-name <n>`
- `aws dynamodb delete-table --table-name <n>`

### Tested
- Lambda: created `hello` function, invoked with/without payload, deleted
- DynamoDB: created `Users` table, added 2 items, retrieved, scanned, deleted

### MiniAWS now has 13 services
Account, EC2, S3, S3 API, VPC, IAM, CloudWatch, CloudFormation,
AZs, NATs, Security Groups, Lambda, DynamoDB.

---

## Session: 2026-10-06 (evening) — Interactive Console (Session 1 of 3)
**Goal:** Make the console interactive — create VPCs from browser. ✅ Achieved.

### What we built
- `console_server.py`: added `do_POST` handler + form parsing
- `console.py`: added form CSS, alert banner, "Create VPC" details button
- New route: `POST /create-vpc`
- Redirects back to `/` with success/error message
- Success/error banner displays at top of dashboard

### How it works
1. User clicks "➕ Create VPC" (details element expands)
2. Types CIDR, clicks Create
3. Browser POSTs to `/create-vpc`
4. Server calls `vpc.create_vpc(cidr)`
5. Server redirects to `/?ok=<msg>` or `/?error=<msg>`
6. Dashboard reads query string, shows banner
7. VPC appears in list

### Real-AWS-style layout
- Create button next to the resource section (like real AWS)
- Not a central "Quick Actions" panel
- Matches what real engineers see in real AWS console

### Session 1 of 3 complete
- ✅ POST handling
- ✅ Create VPC form
- ✅ Real-AWS layout
- ⏳ Delete VPC + Create subnet (Session 2)
- ⏳ Other resources (Session 3)

---

## Session: 2026-10-06 (evening) — Interactive Console Progress
**Goal:** Make console interactive — Session 1 of 3 (mostly done).

### Working
- POST handler in console_server.py
- Create VPC from browser (green banner + list update)
- Create S3 bucket from browser
- Create Security Group from browser
- Create Lambda function from browser
- Create DynamoDB table from browser
- Create Subnet from VPC detail page
- Delete Subnet from VPC detail page (with confirm)
- Delete VPC button on VPC detail page
- Real-AWS-style layout (create buttons per section)

### Not yet done
- Delete buttons on SG, Lambda, DynamoDB, NAT detail pages
- Create EC2 instance from browser
- Create NAT Gateway from browser
- Add remaining create forms to other sections

### To resume
- See TODOs above when we come back
- Console code is stable, forms work
- Just add more routes + handlers

### Progress recap
- MiniAWS: 13 services
- Course: Chapters 1-7 complete
- Console: interactive, mostly complete
