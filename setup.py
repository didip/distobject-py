from setuptools import setup, find_packages

setup(
    name="distobject-py",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "redis",
        "ulid-py",
    ],
    python_requires=">=3.6",
    author="Your Name",
    description="Distributed objects with Redis for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/distobject-py",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
