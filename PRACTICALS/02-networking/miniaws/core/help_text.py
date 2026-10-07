"""Help text for MiniAWS commands."""

HELP = {
    # ---------- EC2 ----------
    "ec2 describe-vpcs": """
describe-vpcs
Describe one or more VPCs.

USAGE
  aws ec2 describe-vpcs [--output json]

OPTIONS
  --output json    Return output as JSON

EXAMPLES
  aws ec2 describe-vpcs
  aws ec2 describe-vpcs --output json
""",
    "ec2 create-vpc": """
create-vpc
Create a new VPC.

USAGE
  aws ec2 create-vpc --cidr-block <cidr>

OPTIONS
  --cidr-block    The IPv4 network range for the VPC (required)
                  Format: x.x.x.x/n  Example: 10.0.0.0/16

EXAMPLES
  aws ec2 create-vpc --cidr-block 10.0.0.0/16
""",
    "ec2 delete-vpc": """
delete-vpc
Delete a VPC. Refuses if subnets exist.

USAGE
  aws ec2 delete-vpc <vpc-id>

EXAMPLES
  aws ec2 delete-vpc vpc-0123456789abcdef0
""",
    "ec2 describe-subnets": """
describe-subnets
Describe one or more subnets.

USAGE
  aws ec2 describe-subnets [--output json]
""",
    "ec2 create-subnet": """
create-subnet
Create a subnet inside a VPC.

USAGE
  aws ec2 create-subnet --vpc-id <vpc> --cidr-block <cidr> [--name <name>]

OPTIONS
  --vpc-id        The VPC to create the subnet in (required)
  --cidr-block    The IPv4 range for the subnet (required)
                  Must be inside the VPC's CIDR
  --name          A human-friendly name tag

EXAMPLES
  aws ec2 create-subnet --vpc-id vpc-abc --cidr-block 10.0.1.0/24 --name public-1
""",
    "ec2 delete-subnet": """
delete-subnet
Delete a subnet.

USAGE
  aws ec2 delete-subnet <subnet-id>
""",
    "ec2 describe-internet-gateways": """
describe-internet-gateways
List internet gateways.

USAGE
  aws ec2 describe-internet-gateways [--output json]
""",
    "ec2 create-internet-gateway": """
create-internet-gateway
Create an internet gateway (the door to the internet).

USAGE
  aws ec2 create-internet-gateway [--name <name>]
""",
    "ec2 attach-internet-gateway": """
attach-internet-gateway
Attach an internet gateway to a VPC.

USAGE
  aws ec2 attach-internet-gateway --igw-id <igw> --vpc-id <vpc>
""",
    "ec2 detach-internet-gateway": """
detach-internet-gateway
Detach an internet gateway from a VPC.

USAGE
  aws ec2 detach-internet-gateway --igw-id <igw> --vpc-id <vpc>
""",
    "ec2 delete-internet-gateway": """
delete-internet-gateway
Delete an internet gateway. Must be detached first.

USAGE
  aws ec2 delete-internet-gateway <igw-id>
""",
    "ec2 describe-route-tables": """
describe-route-tables
List route tables (the signposts for packets).

USAGE
  aws ec2 describe-route-tables [--vpc-id <vpc>] [--output json]

OPTIONS
  --vpc-id    Only show route tables for this VPC
""",
    "ec2 create-route-table": """
create-route-table
Create a new route table for a VPC.

USAGE
  aws ec2 create-route-table --vpc-id <vpc> [--name <name>]
""",
    "ec2 create-route": """
create-route
Add a route to a route table.

USAGE
  aws ec2 create-route --route-table-id <rt> --destination-cidr-block <cidr>
                       [--nat-gateway-id <nat> | --gateway-id <igw>]

OPTIONS
  --route-table-id             The route table to modify (required)
  --destination-cidr-block     The CIDR to route (required)
  --nat-gateway-id             Route via a NAT Gateway
  --gateway-id                 Route via an Internet Gateway

EXAMPLES
  aws ec2 create-route --route-table-id rtb-xxx \\
    --destination-cidr-block 0.0.0.0/0 --nat-gateway-id nat-xxx
""",
    "ec2 associate-route-table": """
associate-route-table
Associate a route table with a subnet.

USAGE
  aws ec2 associate-route-table --route-table-id <rt> --subnet-id <subnet>
""",
    "ec2 delete-route-table": """
delete-route-table
Delete a route table.

USAGE
  aws ec2 delete-route-table <rt-id>
""",
    "ec2 run-instances": """
run-instances
Launch a new EC2 instance.

USAGE
  aws ec2 run-instances --name <name> [--type <type>]

OPTIONS
  --name    Instance name (required)
  --type    Instance type. Default: t3.micro
            Valid: t3.nano, t3.micro, t3.small, t3.medium, t3.large

EXAMPLES
  aws ec2 run-instances --name web-server --type t3.micro
""",
    "ec2 describe-instances": """
describe-instances
List all EC2 instances.

USAGE
  aws ec2 describe-instances [--output json]
""",
    "ec2 describe-instance": """
describe-instance
Show details for one instance.

USAGE
  aws ec2 describe-instance <id-or-name>
""",
    "ec2 start-instances": """
start-instances
Start a stopped instance.

USAGE
  aws ec2 start-instances <id-or-name>
""",
    "ec2 stop-instances": """
stop-instances
Stop a running instance.

USAGE
  aws ec2 stop-instances <id-or-name>
""",
    "ec2 reboot-instances": """
reboot-instances
Reboot an instance (like pressing the reset button).

USAGE
  aws ec2 reboot-instances <id-or-name>
""",
    "ec2 terminate-instances": """
terminate-instances
Permanently terminate an instance (cannot be undone).

USAGE
  aws ec2 terminate-instances <id-or-name>
""",
    "ec2 create-nat-gateway": """
create-nat-gateway
Create a NAT Gateway in a public subnet.
Gives private subnets outbound-only internet.

USAGE
  aws ec2 create-nat-gateway --subnet-id <subnet-id>

EXAMPLES
  aws ec2 create-nat-gateway --subnet-id subnet-abc123
""",
    "ec2 describe-nat-gateways": """
describe-nat-gateways
List all NAT gateways.

USAGE
  aws ec2 describe-nat-gateways
""",
    "ec2 delete-nat-gateway": """
delete-nat-gateway
Delete a NAT Gateway.

USAGE
  aws ec2 delete-nat-gateway <nat-id>
""",
    "ec2 describe-availability-zones": """
describe-availability-zones
List the availability zones in the current region.

USAGE
  aws ec2 describe-availability-zones [--output json]
""",

    # ---------- S3 ----------
    "s3 mb": """
mb
Make a new S3 bucket.

USAGE
  aws s3 mb s3://<bucket>

EXAMPLES
  aws s3 mb s3://my-bucket
""",
    "s3 ls": """
ls
List buckets, or objects inside a bucket.

USAGE
  aws s3 ls
  aws s3 ls s3://<bucket>/[prefix]
""",
    "s3 cp": """
cp
Copy files to or from S3.

USAGE
  aws s3 cp <local-file> s3://<bucket>/<key>
  aws s3 cp s3://<bucket>/<key> <local-file>
  aws s3 cp s3://<src>/<key> s3://<dst>/<key>
""",
    "s3 rm": """
rm
Delete an object from a bucket.

USAGE
  aws s3 rm s3://<bucket>/<key>
""",
    "s3 rb": """
rb
Remove a bucket. Use --force to remove non-empty.

USAGE
  aws s3 rb s3://<bucket> [--force]
""",

    # ---------- IAM ----------
    "iam list-users": """
list-users
List all IAM users.

USAGE
  aws iam list-users [--output json]
""",
    "iam create-user": """
create-user
Create a new IAM user.

USAGE
  aws iam create-user <username>
""",
    "iam delete-user": """
delete-user
Delete an IAM user.

USAGE
  aws iam delete-user <username>
""",

    # ---------- CloudWatch ----------
    "cloudwatch list-alarms": """
list-alarms
List all CloudWatch alarms.

USAGE
  aws cloudwatch list-alarms
""",
    "cloudwatch put-metric-data": """
put-metric-data
Record a metric datapoint.

USAGE
  aws cloudwatch put-metric-data --namespace <ns> --metric <name> --value <n> [--unit <unit>]
""",
    "cloudwatch put-metric-alarm": """
put-metric-alarm
Create or update a CloudWatch alarm.

USAGE
  aws cloudwatch put-metric-alarm --name <n> --namespace <ns> --metric <m>
                                  --threshold <t> [--comparison <c>]
""",

    # ---------- STS ----------
    "sts get-caller-identity": """
get-caller-identity
Show who you're currently logged in as.

USAGE
  aws sts get-caller-identity
""",

    # ---------- Billing ----------
    "billing show": """
show
Show simulated AWS bill.

USAGE
  aws billing show
""",
    "billing reset": """
reset
Reset the simulated bill to $0.

USAGE
  aws billing reset
""",

    # ---------- Lambda ----------
    "lambda create-function": """
create-function
Create a Lambda function (serverless).

USAGE
  aws lambda create-function --function-name <n> --zip-file <path.py>
                             [--runtime <r>] [--handler <h>]

OPTIONS
  --function-name   Name of the function (required)
  --zip-file        Path to the Python file containing the handler (required)
  --runtime         Runtime (default: python3.11)
  --handler         Handler function name (default: lambda_handler)

EXAMPLES
  aws lambda create-function --function-name hello --zip-file ./hello.py
""",
    "lambda list-functions": """
list-functions
List all Lambda functions.

USAGE
  aws lambda list-functions [--output json]
""",
    "lambda invoke": """
invoke
Invoke a Lambda function.

USAGE
  aws lambda invoke --function-name <n> [--payload '<json>']

OPTIONS
  --function-name   Name of the function (required)
  --payload         JSON payload to pass as the event

EXAMPLES
  aws lambda invoke --function-name hello
  aws lambda invoke --function-name hello --payload '{"name": "Kelvin"}'
""",
    "lambda delete-function": """
delete-function
Delete a Lambda function.

USAGE
  aws lambda delete-function --function-name <n>
""",

    # ---------- DynamoDB ----------
    "dynamodb create-table": """
create-table
Create a DynamoDB table.

USAGE
  aws dynamodb create-table --table-name <n> --key-schema '<attr>:<type>'

OPTIONS
  --table-name    Name of the table (required)
  --key-schema    Primary key as 'name:type' where type is S (string) or N (number)

EXAMPLES
  aws dynamodb create-table --table-name Users --key-schema 'id:S'
""",
    "dynamodb list-tables": """
list-tables
List all DynamoDB tables.

USAGE
  aws dynamodb list-tables [--output json]
""",
    "dynamodb put-item": """
put-item
Insert or replace an item in a DynamoDB table.

USAGE
  aws dynamodb put-item --table-name <n> --item '<json>'

EXAMPLES
  aws dynamodb put-item --table-name Users --item '{"id": "alice", "name": "Alice"}'
""",
    "dynamodb get-item": """
get-item
Retrieve an item by its key.

USAGE
  aws dynamodb get-item --table-name <n> --key '<value>'
  aws dynamodb get-item --table-name <n> --key '{"id": "alice"}'

EXAMPLES
  aws dynamodb get-item --table-name Users --key alice
""",
    "dynamodb delete-item": """
delete-item
Delete an item by its key.

USAGE
  aws dynamodb delete-item --table-name <n> --key '<value>'
""",
    "dynamodb scan": """
scan
Scan all items in a table (like SELECT * with no filter).

USAGE
  aws dynamodb scan --table-name <n> [--output json]
""",
    "dynamodb delete-table": """
delete-table
Delete a DynamoDB table.

USAGE
  aws dynamodb delete-table --table-name <n>
""",

    # ---------- CloudFormation ----------
    "cloudformation deploy": """
deploy
Deploy a CloudFormation stack from a template.

USAGE
  aws cloudformation deploy --stack <name> --template <path>

OPTIONS
  --stack      Name of the stack (required)
  --template   Path to YAML/JSON template (required)

EXAMPLES
  aws cloudformation deploy --stack my-stack --template ./stack.yaml
""",
    "cloudformation list-stacks": """
list-stacks
List all CloudFormation stacks.

USAGE
  aws cloudformation list-stacks
""",
    "cloudformation describe-stack": """
describe-stack
Show details for one stack.

USAGE
  aws cloudformation describe-stack <stack-name>
""",
    "cloudformation delete-stack": """
delete-stack
Delete a stack (note: resources are not deleted).

USAGE
  aws cloudformation delete-stack <stack-name>
""",
}
