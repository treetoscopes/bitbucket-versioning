# Bitbucket Versioning

A reusable versioning system for Bitbucket Pipelines that helps manage semantic versioning across multiple repositories.

## Features

- 🔢 Semantic versioning (x.y.z) with intelligent increment/reset logic
- 🔄 Support for multiple storage backends (file, DynamoDB, S3)
- 🏷️ Automatic image tag generation for Docker images
- 🔌 Easy integration with Bitbucket Pipelines
- 🚀 Command-line interface for all operations

## Installation

### From PyPI (recommended)

```bash
pip install bitbucket-versioning
```

### From Source

```bash
git clone https://github.com/treetoscopes/bitbucket-versioning.git
cd bitbucket-versioning
pip install -e .
```

## Storage Options

### File Storage (Default)

Stores version information in a local JSON file. Simple but limited to single runners.

```bash
version-manager --storage-type file --version-file version.json
```

### DynamoDB Storage

Stores version information in a DynamoDB table. Ideal for sharing versions across builds.

```bash
version-manager --storage-type dynamodb --dynamodb-table version-table
```

### S3 Storage

Stores version information in an S3 bucket. Good for organizational versioning.

```bash
version-manager --storage-type s3 --s3-bucket version-bucket --s3-prefix versions
```

## Usage in Bitbucket Pipelines

Add this to your `bitbucket-pipelines.yml`:

```yaml
pipelines:
  default:
    - step:
        name: "Version Management"
        script:
          # Install the versioning tool
          - pip install bitbucket-versioning
          
          # Use DynamoDB for shared versioning
          - version-manager --storage-type dynamodb --dynamodb-table app-versions --increment z
          
          # Get the version string
          - export VERSION=$(version-manager --storage-type dynamodb --dynamodb-table app-versions --get-version)
          - echo "Building version $VERSION"
          
          # Generate Docker image tag
          - export IMAGE_TAG=$(version-manager --storage-type dynamodb --dynamodb-table app-versions --get-tag)
          - echo "Image tag: $IMAGE_TAG"
```

## Command Line Interface

```
usage: version-manager [-h] [--increment {x,y,z}] [--reset-z] [--get-tag]
                      [--get-version] [--set-x SET_X] [--set-y SET_Y]
                      [--set-z SET_Z] [--storage-type {file,dynamodb,s3}]
                      [--version-file VERSION_FILE]
                      [--dynamodb-table DYNAMODB_TABLE]
                      [--s3-bucket S3_BUCKET] [--s3-prefix S3_PREFIX]

Version Manager for CI/CD

optional arguments:
  -h, --help            show this help message and exit
  --increment {x,y,z}   Increment specific version component
  --reset-z             Reset Z component to 0
  --get-tag             Generate and print full image tag
  --get-version         Print current version string
  --set-x SET_X         Set X component value
  --set-y SET_Y         Set Y component value
  --set-z SET_Z         Set Z component value
  --storage-type {file,dynamodb,s3}
                        Storage type for version data
  --version-file VERSION_FILE
                        Path to version file
  --dynamodb-table DYNAMODB_TABLE
                        DynamoDB table name
  --s3-bucket S3_BUCKET
                        S3 bucket name
  --s3-prefix S3_PREFIX
                        S3 key prefix
```

## AWS Permissions

If using DynamoDB or S3 storage, your pipeline needs appropriate IAM permissions:

### DynamoDB Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/your-version-table"
    }
  ]
}
```

### S3 Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::your-version-bucket/versions/*"
    }
  ]
}
```

## Advanced Usage

### Creating a DynamoDB Table

```bash
aws dynamodb create-table \
  --table-name app-versions \
  --attribute-definitions AttributeName=repo_id,AttributeType=S \
  --key-schema AttributeName=repo_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### Version Promotion Strategy

For promoting versions between environments:

```yaml
pipelines:
  custom:
    promote-to-prod:
      - step:
          script:
            - pip install bitbucket-versioning
            - VERSION=$(version-manager --storage-type dynamodb --dynamodb-table dev-versions --get-version)
            - version-manager --storage-type dynamodb --dynamodb-table prod-versions --set-x $(echo $VERSION | cut -d. -f1) --set-y $(echo $VERSION | cut -d. -f2) --set-z $(echo $VERSION | cut -d. -f3)
```

### Branch-Based Version Management

Different version increments based on branch:

```yaml
pipelines:
  branches:
    master:
      - step:
          script:
            - pip install bitbucket-versioning
            - version-manager --storage-type dynamodb --dynamodb-table app-versions --increment y --reset-z
    feature/*:
      - step:
          script:
            - pip install bitbucket-versioning
            - version-manager --storage-type dynamodb --dynamodb-table app-versions --increment z
```

## License

MIT


# Developers
### What is this repository for? ###

* This repository is meant to be a helper in a bitbucket pipline to maintain code versioning
* Version 1.0.0

### How do I get set up? ###

* The top level Dockerfile is a development docker (dev container) and should include all the necessary set up
* The code is python using poetry as package manager
* The actual logic is within version-manager folder
* Flake8 is used with --max-line-length 95
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

