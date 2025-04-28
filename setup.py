from setuptools import setup, find_packages

setup(
    name='distobject',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'aioredis>=2.0.1',
        'ulid-py>=1.1',
    ],
    python_requires='>=3.8',
    author='Your Name',
    description='Distributed Object Library for Python (async, Redis-backed, pure functions)',
    url='https://github.com/yourname/distobject-py',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
)
