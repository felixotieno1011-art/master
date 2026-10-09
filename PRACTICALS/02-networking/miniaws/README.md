# MiniAWS

A local, learning-oriented implementation of the AWS CLI, written in
Python and run through a bash wrapper named `aws`.

The goal is not to replace the real AWS CLI. The goal is to *imitate its
contract* — the parts that scripts and SDKs actually depend on — so that
using real AWS later feels familiar.

---

## What this is

- **A simulator.** State lives in `state/`. Nothing hits the network.
- **A contract exerciser.** It emits AWS-shaped errors, exit codes,
  JSON, and JMESPath responses.
- **A learning tool.** You can break it, reset it, and experiment
  without spending money.

## What this is not

- **Not production.** No auth, no real networking, no real IAM.
- **Not a compatibility shim.** It does not need to be, and it
  intentionally diverges from AWS in places (see below).
- **Not complete.** Several services are still "beginner tier" — they
  work, but they don't yet honor the AWS contract.

---

## The contract layer

These features apply to *migrated* services. See the migration table.

| Feature | Status |
|---|---|
| AWS error template: `{op} failed: {resource} An error occurred ({Code}) when calling the {Operation} operation: {message}` | ✅ |
| Error codes in `(Parentheses)` form | ✅ |
| Exit codes: `0` success, `1` service error, `255` client error | ✅ |
| Errors on stderr, success on stdout | ✅ |
| `--output json` (real AWS-shaped JSON) | ✅ for whitelisted commands |
| `--query '<JMESPath>'` (real jmespath library) | ✅ for whitelisted commands |
| `--dry-run` (no side effects, exit 255, `(DryRunOperation)`) | ✅ for whitelisted write commands |
| Unknown flag rejection: `(UnknownOptions)`, exit 255 | ✅ for migrated services |
| Global flag stripping: `--output`, `--query`, `--region`, `--profile`, `--endpoint-url` | ✅ |
| Filtered describe with missing ID: `(InvalidInstanceID.NotFound)`, exit 255 | ✅ ec2 describe-instances |

## Migration status

| Service | Error template | Exit codes | `--dry-run` | Strict flags | `--output json` | `--query` |
|---|---|---|---|---|---|---|
| **s3** | ✅ | ✅ | ✅ | ✅ | ✅ `ls` | ✅ |
| **iam** | ✅ | ✅ | ✅ | ✅ | ✅ 4 commands | ✅ |
| **ec2** (instance ops) | ✅ | ✅ | ✅ | ✅ | ✅ `describe-*` | ✅ |
| **vpc / subnet / igw / rtb** | ❌ legacy | ❌ | ❌ | ❌ | ❌ | ❌ |
| **cloudwatch** | ❌ legacy | ❌ | ❌ | ❌ | ✅ `list-alarms` | ❌ |
| **cloudformation** | ❌ legacy | ❌ | ❌ | ❌ | ❌ | ❌ |
| **lambda** | ❌ legacy | ❌ | ❌ | ❌ | ❌ | ❌ |
| **dynamodb** | ❌ legacy | ❌ | ❌ | ❌ | ❌ | ❌ |
| **sts** | ❌ legacy | ❌ | n/a | ❌ | ❌ | ❌ |

"Legacy" means the service works, but errors print `❌ message` on
stdout with exit code 1. To migrate a service to the contract layer,
follow the S3/IAM/EC2 pattern: `AWSError` + `wrap_legacy`, wire
`check_dry_run`, wire `strict_flags`, add JSON handlers.

---

## Intentional divergences from real AWS

These are *choices*, not bugs. Do not "fix" them without deciding
whether you still want the learning-friendly behavior.

- **Emoji on stdout** — `✅`, `❌`, `⚠️`, `ℹ️` prefix on status output.
  Real AWS is plain ASCII. This is easier to scan for a human learner.
- **Dashed tables** — `BUCKET  REGION  CREATED` with `-` separators.
  Real AWS `--output table` uses `+---+` borders.
- **`s3 rb --force`** — not a real AWS flag. Convenience for emptying
  non-empty buckets without `s3 rm --recursive` first.
- **`cp` shows the object URL** — `https://bucket.s3.region.amazonaws.com/key`
  instead of real AWS's `./local.txt to s3://bucket/key` form.
- **`s3 ls` includes REGION column** — real AWS doesn't show it
  (it requires a separate `get-bucket-location` call per bucket).
- **Empty `ls s3://bucket` prints a warning** — real AWS prints nothing.
- **CIDR overlap rejected across VPCs** — real AWS allows overlapping
  VPCs. This CLI rejects them for pedagogical clarity.

If you want strict AWS parity, this is your list. Each can be flipped
with a few lines, but do it deliberately.

---

## Test recipe

Run this after any change. If any line fails, something regressed.

### 1. Contract smoke test

```bash
# Error template + code + exit code
aws s3 rb s3://nope-xyz
# expected: remove_bucket failed: s3://nope-xyz An error occurred (NoSuchBucket) ... ; exit 1

# stderr separation
aws s3 rb s3://nope-xyz 2>/dev/null
# expected: nothing; exit 1

# Dry-run safety
aws s3 mb s3://drought-test --dry-run
# expected: (DryRunOperation); exit 255; bucket NOT created

# Unknown flag
aws s3 mb s3://x --bogus
# expected: (UnknownOptions); exit 255

# --output json
aws s3 ls --output json | python3 -m json.tool >/dev/null
# expected: exit 0 (valid JSON)

# --query
aws s3 ls --query 'Buckets[].Name' | python3 -m json.tool >/dev/null
# expected: exit 0

# Filtered describe on missing resource
aws ec2 describe-instances --instance-ids i-00000000000000000
# expected: (InvalidInstanceID.NotFound); exit 255

# IAM DeleteConflict
aws iam create-user --user-name readme-test
aws iam create-access-key --user-name readme-test >/dev/null
aws iam delete-user --user-name readme-test
# expected: (DeleteConflict); exit 1

# cleanup
AK=$(aws iam list-access-keys --user-name readme-test | awk 'NR==3 {print $1}')
aws iam delete-access-key --user-name readme-test --access-key-id "$AK" >/dev/null
aws iam delete-user --user-name readme-test
