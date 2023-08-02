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

INSTALL_REQUIRES = ["numpy", "pandas", "astroquery", "astropy", "scipy"]


setup(
    name="tess-atl",
    version="0.0.2.2",
    author="Daniel Hey",
    packages=["atl"],
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    install_requires=INSTALL_REQUIRES,
    entry_points={
        "console_scripts": [
            "atl=atl.cli:main",
        ],
    },
)
