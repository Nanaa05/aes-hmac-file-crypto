from setuptools import setup, find_packages

setup(
    name="aeshmac",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "cryptography>=41.0.0",
    ],
    entry_points={
        "console_scripts": [
            "filecrypt=aeshmac.main:main",
        ],
    },
    author="Brian Ricardo Tamin, Nathanael Rachmat",
    license="MIT",
    description="AES-HMAC file crypto utility",
    python_requires=">=3.7",
)
