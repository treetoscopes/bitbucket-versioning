from setuptools import setup, find_packages

setup(
    name="bitbucket-versioning",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.28.0",
    ],
    entry_points={
        'console_scripts': [
            'version-manager=bitbucket_versioning.version_manager:main',
        ],
    },
    author="Alon Fux",
    author_email="Alon.Fux@treetoscope.com",
    description="A reusable versioning tool for Bitbucket Pipelines",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/treetoscopes/bitbucket-versioning",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)