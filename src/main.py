import sys
import argparse
from src.version_manager import VersionManager


def main():
    """Command-line interface for version manager."""
    parser = argparse.ArgumentParser(description="Version Manager for CI/CD")
    parser.add_argument("--increment", choices=["x", "y", "z"],
                        help="Increment specific version component")
    parser.add_argument("--reset-z", action="store_true",
                        help="Reset Z component to 0")
    parser.add_argument("--get-tag", action="store_true",
                        help="Generate and print full image tag")
    parser.add_argument("--get-version", action="store_true",
                        help="Print current version string")
    parser.add_argument("--set-x", type=int, help="Set X component value")
    parser.add_argument("--set-y", type=int, help="Set Y component value")
    parser.add_argument("--set-z", type=int, help="Set Z component value")

    # Storage options
    parser.add_argument("--storage-type", choices=["file", "dynamodb", "s3"],
                        default="file", help="Storage type for version data")
    parser.add_argument("--version-file", help="Path to version file")
    parser.add_argument("--dynamodb-table", help="DynamoDB table name")
    parser.add_argument("--s3-bucket", help="S3 bucket name")
    parser.add_argument("--s3-prefix", help="S3 key prefix")

    args = parser.parse_args()

    # Initialize version manager
    version_manager = VersionManager(
        storage_type=args.storage_type,
        version_file=args.version_file,
        dynamodb_table=args.dynamodb_table,
        s3_bucket=args.s3_bucket,
        s3_prefix=args.s3_prefix
    )

    # Apply version changes
    if args.set_x is not None or args.set_y is not None or args.set_z is not None:
        version_manager.set_version(args.set_x, args.set_y, args.set_z)

    if args.increment == "x":
        version_manager.increment_x()
    elif args.increment == "y":
        version_manager.increment_y()
    elif args.increment == "z":
        version_manager.increment_z()

    if args.reset_z:
        version_manager.reset_z()

    # Save updated version
    version_manager.save_version()

    # Generate and print tag if requested
    if args.get_tag:
        tag = version_manager.generate_image_tag()
        print(tag)

    # Print version if requested
    if args.get_version:
        version = version_manager.get_version_string()
        print(version)

    return 0
#test

if __name__ == "__main__":
    sys.exit(main())
