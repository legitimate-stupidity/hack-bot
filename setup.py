"""Setup configuration for hack-bot."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hack-bot",
    version="0.1.0",
    author="Security Framework Team",
    description="Autonomous coding agent + comprehensive security framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/legitimate-stupidity/hack-bot",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "typer[all]>=0.12.0",
        "rich>=13.7.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "black>=23.0.0",
            "pylint>=2.17.0",
        ],
        "security": [
            "cryptography>=41.0.0",
            "boto3>=1.34.0",
            "pillow>=10.1.0",
            "scikit-learn>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hack-bot=agent.cli:app",
        ],
    },
)
