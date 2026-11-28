from setuptools import setup, find_packages

setup(
    name="agy-shield",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "agy-shield=agy_shield.cli:main",
        ],
    },
)
