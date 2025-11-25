"""
FlowSync SDK — Setup
pip install flowsync
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="flowsync",
    version="0.1.0",
    author="0r8 Empire",
    author_email="dev@0r8.ai",
    description="FlowSync SDK — Route through 3i-ATLAS, summon Demigods, build the future",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0r8/flowsync-sdk",
    project_urls={
        "Documentation": "https://docs.0r8.ai/sdk",
        "Bug Tracker": "https://github.com/0r8/flowsync-sdk/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],  # No external dependencies - uses stdlib only
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21",
            "black>=23.0",
            "mypy>=1.0",
        ],
    },
    keywords=[
        "0r8",
        "flowsync",
        "ai",
        "agi",
        "routing",
        "3i",
        "demigods",
        "intelligence",
        "intuition",
        "integration",
    ],
)
