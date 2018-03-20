from setuptools import setup, find_packages
import os

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(ROOT_DIR, 'README.rst'), encoding='utf-8') as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

CLASSIFIERS = [
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5'
    'Programming Language :: Python :: 3.6'
]

setup(
    name='facebook-hidden-engagement',
    packages=['facebook-hidden-engagement'],
    author='Stefan Kasberger',
    author_email='mail@stefankasberger.at',
    classifiers=CLASSIFIERS,
    description='',
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    keywords=[''],
    long_description=README,
    python_requires='>=3',
    platforms=['OS Independent'],
    package_dir={'': 'src'},
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    url='http://stefankasberger.at',
    version='0.0.1',
    zip_safe=False
)
