#!/usr/bin/env python3
"""
Version Manager for Bitbucket Pipelines CI/CD.
This module handles version management according to semantic versioning principles.
"""

import json
import os
from datetime import datetime
import boto3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('version_manager')

# Default version file if using local file storage
DEFAULT_VERSION_FILE = "version.json"


class VersionManager:
    """Manager for handling semantic versioning across repositories."""

    def __init__(self, storage_type: str = "file", version_file: str = None,
                 dynamodb_table: str = None, s3_bucket: str = None, s3_prefix: str = None,
                 aws_access_key_id: str = None, aws_secret_access_key: str = None,
                 aws_session_token: str = None):
        """
        Initialize the version manager.

        Args:
            storage_type (str): Type of storage to use ('file', 'dynamodb', or 's3')
            version_file (str): Path to version file if using file storage
            dynamodb_table (str): DynamoDB table name if using DynamoDB storage
            s3_bucket (str): S3 bucket name if using S3 storage
            s3_prefix (str): S3 key prefix if using S3 storage
            aws_access_key_id (str): aws access key id
            aws_secret_access_key (str): aws secret access key
            aws_session_token (str): aws session token
        """
        self.storage_type = storage_type
        self.version_file = version_file or DEFAULT_VERSION_FILE
        self.dynamodb_table = dynamodb_table
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token

        # Get repository identifier
        self.repo_id = self._get_repo_identifier()

        # Initialize version data
        self.version_data = self.load_version()

    def _get_repo_identifier(self):
        """Get a unique identifier for the repository."""
        # Try to get from Bitbucket environment variables
        if "BITBUCKET_REPO_SLUG" in os.environ:
            repo_slug = os.environ.get("BITBUCKET_REPO_SLUG")
            workspace = os.environ.get("BITBUCKET_WORKSPACE", "default")
            return f"{workspace}/{repo_slug}"

        # Fall back to local directory name
        import pathlib
        return pathlib.Path(os.getcwd()).name

    def load_version(self):
        """Load version data from the configured storage."""
        if self.storage_type == "file":
            return self._load_from_file()
        elif self.storage_type == "dynamodb":
            return self._load_from_dynamodb()
        elif self.storage_type == "s3":
            return self._load_from_s3()
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")

    def _load_from_file(self):
        """Load version from a local file."""
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r') as f:
                    version_data = json.load(f)
                    logger.info(f"Loaded version from file: {version_data}")
                    return version_data
            except json.JSONDecodeError:
                logger.warning(f"Error parsing {self.version_file}, creating new version")

        # Create default version
        default_version = self._get_default_version()
        logger.info(f"Using default version: {default_version}")
        return default_version

    def _load_from_dynamodb(self):
        """Load version from DynamoDB."""
        if not self.dynamodb_table:
            raise ValueError("DynamoDB table name is required for DynamoDB storage")

        try:
            dynamodb = boto3.resource('dynamodb',
                                      aws_access_key_id=self.aws_access_key_id,
                                      aws_secret_access_key=self.aws_secret_access_key,
                                      aws_session_token=self.aws_session_token)
            table = dynamodb.Table(self.dynamodb_table)
            response = table.get_item(Key={'repo_id': self.repo_id})

            if 'Item' in response:
                version_data = response['Item'].get('version_data', {})
                logger.info(f"Loaded version from DynamoDB: {version_data}")
                return version_data

            # Create default version
            default_version = self._get_default_version()
            logger.info(f"No version found in DynamoDB, using default: {default_version}")
            return default_version

        except Exception as e:
            logger.error(f"Error loading from DynamoDB: {e}")
            # Fall back to default version
            return self._get_default_version()

    def _load_from_s3(self):
        """Load version from S3."""
        if not self.s3_bucket:
            raise ValueError("S3 bucket name is required for S3 storage")

        s3_key = f"{self.s3_prefix or 'versions'}/{self.repo_id}.json"

        try:
            s3 = boto3.client('s3',
                              aws_access_key_id=self.aws_access_key_id,
                              aws_secret_access_key=self.aws_secret_access_key,
                              aws_session_token=self.aws_session_token)

            response = s3.get_object(Bucket=self.s3_bucket, Key=s3_key)
            version_data = json.loads(response['Body'].read().decode('utf-8'))
            logger.info(f"Loaded version from S3: {version_data}")
            return version_data
        except Exception as e:
            logger.warning(f"Error loading from S3: {e}")
            # Create default version
            default_version = self._get_default_version()
            logger.info(f"Using default version: {default_version}")
            return default_version

    def _get_default_version(self):
        """Get default version data."""
        return {
            "x": int(os.environ.get("VERSION_X", 1)),
            "y": int(os.environ.get("VERSION_Y", 0)),
            "z": int(os.environ.get("VERSION_Z", 0))
        }

    def save_version(self):
        """Save version data to the configured storage."""
        if self.storage_type == "file":
            return self._save_to_file()
        elif self.storage_type == "dynamodb":
            return self._save_to_dynamodb()
        elif self.storage_type == "s3":
            return self._save_to_s3()
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")

    def _save_to_file(self):
        """Save version to a local file."""
        with open(self.version_file, 'w') as f:
            json.dump(self.version_data, f, indent=2)
        logger.info(f"Version saved to file: {self.version_data}")

    def _save_to_dynamodb(self):
        """Save version to DynamoDB."""
        if not self.dynamodb_table:
            raise ValueError("DynamoDB table name is required for DynamoDB storage")

        try:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(self.dynamodb_table)

            # Store version data with repo identifier
            item = {
                'repo_id': self.repo_id,
                'version_data': self.version_data,
                'updated_at': datetime.now().isoformat()
            }

            table.put_item(Item=item)
            logger.info(f"Version saved to DynamoDB: {self.version_data}")
        except Exception as e:
            logger.error(f"Error saving to DynamoDB: {e}")
            # Fall back to file storage
            logger.info("Falling back to file storage")
            self._save_to_file()

    def _save_to_s3(self):
        """Save version to S3."""
        if not self.s3_bucket:
            raise ValueError("S3 bucket name is required for S3 storage")

        s3_key = f"{self.s3_prefix or 'versions'}/{self.repo_id}.json"

        try:
            s3 = boto3.client('s3')
            s3.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=json.dumps(self.version_data),
                ContentType='application/json'
            )
            logger.info(f"Version saved to S3: {self.version_data}")
        except Exception as e:
            logger.error(f"Error saving to S3: {e}")
            # Fall back to file storage
            logger.info("Falling back to file storage")
            self._save_to_file()

    def get_version_string(self):
        """Get version as a string."""
        return f"{self.version_data['x']}.{self.version_data['y']}.{self.version_data['z']}"

    def increment_x(self):
        """Increment X value and reset Y and Z."""
        self.version_data["x"] += 1
        self.version_data["y"] = 0
        self.version_data["z"] = 0
        return self

    def increment_y(self):
        """Increment Y value and reset Z."""
        self.version_data["y"] += 1
        self.version_data["z"] = 0
        return self

    def increment_z(self):
        """Increment Z value."""
        self.version_data["z"] += 1
        return self

    def reset_z(self):
        """Reset Z to 0."""
        self.version_data["z"] = 0
        return self

    def set_version(self, x=None, y=None, z=None):
        """Set specific version components."""
        if x is not None:
            self.version_data["x"] = x
        if y is not None:
            self.version_data["y"] = y
        if z is not None:
            self.version_data["z"] = z
        return self

    def generate_image_tag(self):
        """Generate full image tag with project name, commit hash, timestamp, and version."""
        # Use repository slug if available, fallback to env var or default
        project_name = os.environ.get("BITBUCKET_REPO_SLUG",
                                      os.environ.get("PROJECT_NAME", "python-app"))
        commit_hash = os.environ.get("BITBUCKET_COMMIT", "local")[:8]
        timestamp = int(datetime.now().timestamp())
        version_str = self.get_version_string()

        return f"{project_name}-{commit_hash}-{timestamp}-{version_str}"
