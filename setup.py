#!/usr/bin/env python
import os
import sys
from setuptools import setup

# Prepare and send a new release to PyPI
if "release" in sys.argv[-1]:
    os.system("python setup.py sdist")
    os.system("twine upload dist/*")
    os.system("rm -rf dist/tess-atl*")
    sys.exit()

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

# Load the __version__ variable without importing the package already
exec(open("atl/version.py").read())

setup(
    name="tess-atl",
    version=__version__,
    author="Daniel Hey",
    packages=["atl"],
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "atl=atl.cli:main",
        ],
    },
)
