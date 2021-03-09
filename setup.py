#!/usr/bin/env python3

from setuptools import setup
import os


# We store our version number in a simple text file:
version_path = os.path.join(os.path.dirname(__file__), "unimod_mapper", "version.txt")
with open(version_path, "r") as version_file:
    unimod_mapper_version = version_file.read().strip()


setup(
    name="unimod_mapper",
    version=unimod_mapper_version,
    packages=["unimod_mapper"],
    package_dir={"unimod_mapper": "unimod_mapper"},
    description="unimod_mapper",
    package_data={"unimod_mapper": ["version.txt", "unimod.xml"]},
    long_description="Unimod Mapper for Proteomics tools",
    author="... and Christian Fufezan",
    author_email="christian@fufezan.net",
    url="https://github.com/computational-ms/unimod-mapper",
    license="Lesser GNU General Public License (LGPL)",
    platforms="any that supports python 3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: SunOS/Solaris",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
