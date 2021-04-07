# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find out more at https://github.com/ScholCommLab/fhe-collector."""
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
    "Flask==1.1.2",
    "Flask-Migrate==2.5.3",
    "alembic==1.4.3",
    "Flask-SQLAlchemy==2.4.4",
    "psycopg2==2.8.6",
    "pandas==0.25.2",
    "tqdm==4.50.2",
    "facebook-sdk==3.1.0",
    "python-dotenv==0.14.0",
    "pydantic==1.7.2",
]

TESTS_REQUIREMENTS = []

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
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Natural Language :: English",
]

setup(
    author="Stefan Kasberger",
    author_email="mail@stefankasberger.at",
    name="fhecollector",
    version=find_version("app", "__init__.py"),
    description="Facebook Hidden Engagement Microservice",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/ScholCommLab/fhe-collector",
    python_requires=">=3.6",
    platforms=["OS Independent"],
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIREMENTS,
    packages=find_packages(exclude=("tests",)),
    tests_require=TESTS_REQUIREMENTS,
    cmdclass={"test": Tox},
    include_package_data=True,
    keywords=["flask", "facebook", "ncbi", "api", "doi", "Graph API"],
    zip_safe=False,
    project_urls={
        "Documentation": "https://fhe-collector.readthedocs.io/",
        "Issue Tracker": "https://github.com/ScholCommLab/fhe-collector/issues",
        "Changelog": "https://fhe-collector.readthedocs.io/en/latest/",
    },
)
