# Copyright 2018-2021 Alvaro Bartolome, alvarobartt @ GitHub
# See LICENSE for details.

import io

from setuptools import setup, find_packages


def readme():
    with io.open('README.md', encoding='utf-8') as f:
        return f.read()

def requirements(filename):
    reqs = list()
    with io.open(filename, encoding='utf-8') as f:
        for line in f.readlines():
            reqs.append(line.strip())
    return reqs


setup(
    name='investpyx',
    version='0.1.5',
    packages=find_packages(),
    url='https://investpy.readthedocs.io/',
    download_url='https://github.com/alvarobartt/investpy/archive/1.0.3.tar.gz',
    license='MIT License',
    author='Original Author: Alvaro Bartolome, Author of Extended Feature: Komal Paudyal',
    author_email='alvarobdc@yahoo.com, komal.paudyal@icloud.com',
    description='This is a fork of investpy library, and is intended for testing purpose only. All descriptions are hence of original investpy library. Please support the original Author for the contribution he made by developing the investpy library.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    install_requires=requirements(filename='requirements.txt'),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries"
    ],
    python_requires='>=3',
    extras_require={
        "tests": requirements(filename='tests/requirements.txt'),
        "docs": requirements(filename='docs/requirements.txt')
    },
    keywords=', '.join([
        'investing', 'investing-api', 'historical-data',
        'financial-data', 'stocks', 'funds', 'etfs',
        'indices', 'currency crosses', 'bonds', 'commodities',
        'crypto currencies'
    ]),
    project_urls={
        'Bug Reports': 'https://github.com/alvarobartt/investpy/issues',
        'Source': 'https://github.com/alvarobartt/investpy',
        'Forked (Extended Feature)': 'https://github.com/lively-ops/investpy',
        'Documentation': 'https://investpy.readthedocs.io/'
    },
)
