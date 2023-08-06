#!/usr/bin/env python

"""Setup script for the package."""

import logging
import os
import sys
from typing import Optional

import setuptools

PACKAGE_NAME = "sqla_ext"
MINIMUM_PYTHON_VERSION = "3.7"


def check_python_version() -> None:
    """Exit when the Python version is too low."""
    if sys.version < MINIMUM_PYTHON_VERSION:
        sys.exit("Python {0}+ is required.".format(MINIMUM_PYTHON_VERSION))


def read_package_variable(key: str, filename: str = "__init__.py") -> "Optional[str]":
    """Read the value of a variable from the package without importing."""
    module_path = os.path.join("src", PACKAGE_NAME, filename)
    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(" ", 2)
            if parts[:-1] == [key, "="]:
                return parts[-1].strip("'").strip('"')
    logging.warning("'%s' not found in '%s'", key, module_path)
    return None


check_python_version()


DEV_REQUIRES = [
    "pytest",
    "pytest-cov",
    "pytest-benchmark",
    "pre-commit",
    "pylint",
    "black",
    "mypy",
]

setuptools.setup(
    name=read_package_variable("__project__"),
    version=read_package_variable("__version__"),
    description="SQLAlchemy Helpers",
    url="https://github.com/olirice/sqla",
    author="Oliver Rice",
    author_email="oliver@oliverrice.com",
    packages=setuptools.find_packages("src", exclude=("src/tests",)),
    package_dir={"": "src"},
    tests_require=["pytest", "coverage"],
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=["typing_extensions", "sqlalchemy>=1.4.0b3", "sqlalchemy-stubs"],
    extras_require={
        "dev": DEV_REQUIRES,
        "docs": ["mkdocs", "mkautodoc", "pygments", "pymdown-extensions"],
    },
)
