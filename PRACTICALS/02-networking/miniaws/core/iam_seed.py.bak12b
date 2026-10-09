"""Seed common AWS-style policies into MiniIAM."""
from core import iam


COMMON_POLICIES = {
    "S3FullAccess": {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["s3:*"],
            "Resource": "*",
        }],
    },
    "S3ReadOnly": {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:ListBucket"],
            "Resource": "*",
        }],
    },
    "EC2FullAccess": {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["ec2:*"],
            "Resource": "*",
        }],
    },
    "EC2ReadOnly": {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["ec2:Describe*"],
            "Resource": "*",
        }],
    },
    "IAMReadOnly": {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["iam:Get*", "iam:List*"],
            "Resource": "*",
        }],
    },
    "AdministratorAccess": {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": "*",
            "Resource": "*",
        }],
    },
}


def seed():
    """Create all common policies. Idempotent."""
    created = 0
    for name, doc in COMMON_POLICIES.items():
        if iam.get_policy(name):
            continue
        ok_, _ = iam.create_policy(name, doc)
        if ok_:
            created += 1
    return created
