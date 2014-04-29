#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='syndicate',
    version='0.99.2',
    description='A wrapper for REST APIs',
    author='Justin Mayfield',
    author_email='tooker@gmail.com',
    url='https://github.com/mayfield/syndicate/',
    license='MIT',
    long_description=open('README.md').read(),
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-dateutil',
        'tornado',
    ],
    test_suite='test',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ]
)
