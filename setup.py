# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


def _requires_from_file(filename):
    return open(filename).read().splitlines()


with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sagemill',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    version='0.0.1',
    license='Apache License 2.0',
    install_requires=_requires_from_file('requirements.txt'),
    tests_require=_requires_from_file('test-requirements.txt'),
    author='yuki-mt',
    author_email='yuki-mt@gmail.com',
    url='https://github.com/yuki-mt/sagemill/',
    description='Run SageMaker Job like Papermil',
    long_description=long_description,
    keywords='sagemaker,papermill',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
