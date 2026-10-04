# MiniAWS

A minimal version of AWS, built to learn how cloud actually works.

## What it does

- AWS-style account + region model
- EC2 instances (VMs as real processes)
- S3 buckets and objects (served over HTTP)
- VPC + Subnets + Security Groups
- IAM users, policies, roles
- CloudWatch monitoring + alarms
- CloudFormation-style YAML deploys
- Browser console dashboard

## Why

To understand AWS's model at the mechanism level,
not just memorize the console UI.

## Requirements

- Python 3.7+
- No external packages (uses Python stdlib)
- `curl` for S3 testing

## Quick start

    python cli.py help
    python cli.py account show
    python cli.py region set us-east-1
