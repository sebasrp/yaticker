"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

import pathlib

# Always prefer setuptools over distutils
from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="yaticker",
    version="0.1",
    description="Ticker for stocks and cryptocurrencies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sebasrp/yaticker",
    author="Sebastian Rodriguez",
    author_email="331558+sebasrp@users.noreply.github.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="web-app terminal-app finance stocks crypto ticker",
    package_dir={"": "yaticker"},
    packages=find_packages(where="yaticker"),
    python_requires=">=3.8, <4",
    install_requires=[
        "requests>=2.25.1",
        "yfinance>=0.1.59",
        "click~=8.0.1",
        "bottle>=0.12.19",
        "mplfinance~=0.12.7a17",
        "Pillow~=8.2.0",
        "nh-currency~=1.0.1",
        "matplotlib~=3.4.2",
        "PyYAML~=5.4.1",
    ],
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    entry_points={"console_scripts": ["yaticker=cli:main"]},
    project_urls={
        "Bug Reports": "https://github.com/sebasrp/yaticker/issues",
        "Source": "https://github.com/sebasrp/yaticker",
    },
)
