#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup
import os

# We store our version number in a simple text file:
version_path = os.path.join(os.path.dirname(__file__), "unimod_mapper", "version.txt")
with open(version_path, "r") as version_file:
    unimod_mapper_version = version_file.read().strip()

with open("requirements.txt") as req:
    requirements = req.readlines()

setup(
    name="unimod_mapper",
    version=unimod_mapper_version,
    packages=["unimod_mapper"],
    package_dir={"unimod_mapper": "unimod_mapper"},
    description="unimod_mapper",
    package_data={
        "unimod_mapper": [
            "version.txt",
        ]
    },
    python_requires=">=3.7.0",
    install_requires=requirements,
    long_description="Unimod Mapper for Proteomics Tools",
    author="Christian Fufezan, Manuel Kösters, Johannes Leufken, Stefan Schulze",
    author_email="ursgal.team@gmail.com",
    url="https://github.com/computational-ms/unimod-mapper",
    license="MIT",
    platforms="Any that supports python 3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: SunOS/Solaris",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
