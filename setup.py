#!/usr/bin/env python

"""
Installation configuration for pytest-probedock
"""

from setuptools import setup

setup(
    name='pytest-probedock',
    version='0.1.0',
    py_modules=['pytest_probedock'],
    url='https://github.com/probedock/probedock-pytest',
    license='MIT',
    author='Benjamin Schubert',
    author_email='ben.c.schubert@gmail.com',
    description='Pytest plugin for reporting test results to ProbeDock CI',
    long_description=open("README.rst").read(),

    entry_points={
       'pytest11': [
           'probedock = pytest_probedock',
       ]
    },

    install_requires=[
        "probedock",
        "pytest",
    ],

    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
    ],
)
