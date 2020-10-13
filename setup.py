# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find out more at https://github.com/AUSSDA/pyDataverse."""
import codecs
import os
import re
from setuptools.command.test import test as TestCommand
from setuptools import find_packages
from setuptools import setup
import sys

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def read_file(*file_paths):
    """Read text file."""
    with codecs.open(os.path.join(ROOT_DIR, *file_paths), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    """Find package version from file."""
    version_file = read_file(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M,
    )
    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string.")


class Tox(TestCommand):
    """Tox class."""

    def finalize_options(self):
        """Finalize options."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Run tests."""
        # import here, cause outside the eggs aren't loaded
        import tox

        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


INSTALL_REQUIREMENTS = [
    # A string or list of strings specifying what other distributions need to
    # be installed when this one is.
    "flask",
    "alembic",
    "flask-migrate",
    "psycopg2==2.7.5",
    "click",
    "pandas==0.25.2",
    "tqdm",
    "facebook-sdk",
    "python-dotenv",
]

SETUP_REQUIREMENTS = []

TESTS_REQUIREMENTS = ["pytest", "tox" "coverage"]

CLASSIFIERS = [
    # How mature is this project? Common values are
    #   2 - Pre-Alpha
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Natural Language :: English",
]

setup(
    author="Stefan Kasberger",
    author_email="mail@stefankasberger.at",
    name="FHE-Collector",
    version=find_version("fhe_collector", "__init__.py"),
    description="Facebook Hidden Engagement Microservice",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/ScholCommLab/fhe-collector",
    python_requires=">=3.4",
    platforms=["OS Independent"],
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIREMENTS,
    packages=find_packages("src"),
    package_dir={"": "src"},
    setup_requires=SETUP_REQUIREMENTS,
    tests_require=TESTS_REQUIREMENTS,
    cmdclass={"test": Tox},
    include_package_data=True,
    keywords=["fhe_collector", "flask", "facebook", "ncbi", "api", "doi"],
    zip_safe=False,
    project_urls={
        "Documentation": "https://fhe-collector.readthedocs.io/",
        "Issue Tracker": "https://github.com/ScholCommLab/fhe-collector/issues",
        "Changelog": "https://fhe-collector.readthedocs.io/en/latest/",
    },
)
