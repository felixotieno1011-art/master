# MiniAWS 🅰️

A minimal, educational implementation of AWS's core services in Python.

Built to understand how AWS *actually works* — not just memorize the console UI.

## What This Is

MiniAWS is a **local simulator** of AWS's most important services. It runs entirely on your machine (even a phone with Termux) using only Python's standard library. No cloud account. No credit card. No installs.

Every concept maps directly to a real AWS service.

## Services Implemented

| MiniAWS | Real AWS Equivalent | What It Does |
|---------|---------------------|--------------|
| `account` | AWS Account + `aws configure` | 12-digit account ID, regions, tags |
| `ec2` | Amazon EC2 | Virtual machines (real processes) |
| `s3` | Amazon S3 | Object storage, `s3://` URIs, HTTP-served |
| `vpc` | Amazon VPC | Virtual networks, subnets, IGW, route tables |
| `iam` | AWS IAM | Users, groups, JSON policies, permissions |
| `cloudwatch` | Amazon CloudWatch | Metrics, alarms, log groups |
| `cfn` | AWS CloudFormation | Infrastructure as Code (YAML/JSON templates) |
| `console` | AWS Management Console | Browser dashboard |

## Why This Exists

I built MiniAWS to **learn AWS by understanding the mechanics**, not by memorizing commands. Reading docs teaches you *what* AWS does. Building a mini version teaches you *how*.

Every command in MiniAWS has a real AWS equivalent:


Same concept. Same CIDR math. Same result. Zero cost while learning.

## Requirements

- **Python 3.7+**
- **No external packages** — uses only Python's standard library
- **`ping` and `curl`** — for testing S3 objects over HTTP
- Tested on **Termux (Android)** and **Linux**

## Quick Start

```bash
# Setup account
python cli.py account init
python cli.py account show

# Set region
python cli.py region set af-south-1

# Create a VPC and subnet
python vpc_cli.py create-vpc --cidr-block 10.0.0.0/16
python vpc_cli.py create-subnet --vpc-id <VPC-ID> --cidr-block 10.0.1.0/24 --name public-1

# Launch an EC2 instance
python cli.py ec2 run-instances --name web-server --type t3.micro
python cli.py ec2 describe-instances

# Create an S3 bucket and upload a file
python cli.py s3 mb s3://my-bucket
python cli.py s3 cp ./file.txt s3://my-bucket/file.txt

# Create IAM users and policies
python iam_cli.py login root
python iam_cli.py seed
python iam_cli.py create-user alice
python iam_cli.py attach-user-policy --user alice --policy S3ReadOnly
python iam_cli.py login alice
python iam_cli.py can s3:GetObject

# Deploy a stack with CloudFormation
python cfn_cli.py deploy --stack my-stack --template stack-demo.json

# View the browser console
python console.py serve
# Then open: http://localhost:7000
eof
EOF
