#!/usr/bin/env python

from setuptools import setup

setup(
    name='syndicate',
    version='0.99',
    description='A wrapper for REST APIs',
    author='Justin Mayfield',
    author_email='tooker@gmail.com',
    license='LICENSE',
    long_description=open('README.md').read(),
    packages=['syndicate'],
    install_requires=['requests'],
    test_suite='test',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ]
)
