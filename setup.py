#!/usr/bin/env python

from setuptools import setup, find_packages

README = 'README.md'

def long_desc():
    try:
        import pypandoc
    except ImportError:
        with open(README) as f:
            return f.read()
    else:
        return pypandoc.convert(README, 'rst')

setup(
    name='syndicate',
    version='3.0.0',
    description='A wrapper for REST APIs',
    author='Justin Mayfield',
    author_email='tooker@gmail.com',
    url='https://github.com/mayfield/syndicate/',
    license='MIT',
    long_description=long_desc(),
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-dateutil',
        'aiohttp>=3.5.1',
    ],
    test_suite='test',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
    ]
)
