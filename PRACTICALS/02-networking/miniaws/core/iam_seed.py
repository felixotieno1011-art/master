"""Seed common AWS-style policies into MiniIAM."""
from core import iam


COMMON_POLICIES = {
    "AmazonS3FullAccess": {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["s3:*"],
            "Resource": "*",
        }],
    },
    "AmazonS3ReadOnlyAccess": {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:ListBucket"],
            "Resource": "*",
        }],
    },
    "AmazonEC2FullAccess": {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["ec2:*"],
            "Resource": "*",
        }],
    },
    "AmazonEC2ReadOnlyAccess": {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["ec2:Describe*"],
            "Resource": "*",
        }],
    },
    "IAMReadOnlyAccess": {
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
