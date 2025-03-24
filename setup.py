from setuptools import setup, find_packages

setup(
    name="reyrey_auth",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "loguru",
        "playwright",
        "python-dotenv",
        "requests",
        "sqlalchemy",  # For database provider
    ],
    entry_points={
        "console_scripts": [
            "reyrey_auth=reyrey_auth.cli:main",
        ],
    },
    python_requires=">=3.7",
    author="Your Name",
    author_email="your.email@example.com",
    description="Authentication module for Reynolds & Reynolds CRM",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
