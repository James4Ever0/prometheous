#!/usr/bin/env python3
"""Setup script for Prometheous package."""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Prometheous: AI-powered documentation and vector indexing tool"

# Read requirements
def read_requirements():
    # requirements = []
    
    # Base requirements from document_agi_computer_control/requirements.txt
    base_reqs = [
        "beartype",
        "progressbar2", 
        "jinja2",
        "langchain",
        "parse",
        "pydantic",
        "tiktoken",
        "tinydb",
        "textual",
        "markdown",
        "humanize",
        "rich",
        "aiofiles",
        "numpy",
        "identify",
        "openai",
        "litellm",
        "click>=8.0.0",  # For CLI interface
    ]
    
    # Vector store requirements
    vector_reqs = [
        "langchain-ollama",
        "docarray[hnswlib,proto]",
        "llama_index",
    ]
    
    return base_reqs + vector_reqs

setup(
    name="prometheous",
    version="0.1.0",
    author="James Brown",
    author_email="randomvoidmail@foxmail.com",
    description="AI-powered documentation generation and vector indexing tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/James4Ever0/prometheous",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Indexing",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "prom=prometheous.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "prometheous": [
            "templates/*.html.j2",
            "templates/*.html",
            "static/*.js",
            "static/*.css",
        ],
    },
)
