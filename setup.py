#!/usr/bin/env python

from setuptools import setup, find_packages

with open('requirements.txt', 'r') as req:
    INSTALL_REQUIRES = [x.strip() for x in req.readlines()]

with open('README.rst', 'r') as desc:
    readme = desc.read()

setup(
    name='heman',
    version='1.1.4',
    description="Uses the Empowering Sword (a.k.a Empowering Proxy API for users)",
    packages=find_packages(),
    url='https://github.com/gisce/heman',
    long_description = readme,
    long_description_content_type = 'text/markdown', 
    license='MIT',
    install_requires=INSTALL_REQUIRES,
    author='GISCE-TI, S.L.',
    author_email='ti@gisce.net',
)
