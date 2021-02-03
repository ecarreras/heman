from setuptools import setup, find_packages

with open('requirements.txt', 'r') as req:
    INSTALL_REQUIRES = [x.strip() for x in req.readlines()]

with open('README.rst', 'r') as desc:
    DESCRIPTION = desc.read()

setup(
    name='heman',
    version='1.1.1',
    packages=find_packages(),
    url='https://github.com/gisce/heman',
    license='MIT',
    install_requires=INSTALL_REQUIRES,
    author='GISCE-TI, S.L.',
    author_email='ti@gisce.net',
    description=DESCRIPTION
)
