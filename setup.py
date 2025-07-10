#!/usr/bin/env python3
"""
Setup script for Sapphire DeFi application
"""

from setuptools import setup, find_packages
import os

def read_requirements():
    """Read requirements from requirements.txt"""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements', 'requirements.txt')
    with open(requirements_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def read_readme():
    """Read README.md"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme_path, 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name='sapphire-defi',
    version='0.1.0a1',
    description='Decentralized finance application for managing Ethereum wallets',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='B.E.S',
    author_email='',
    url='https://github.com/Erslsf/Sapphire',
    packages=find_packages(),
    package_dir={'sapphire': 'source'},
    package_data={
        'sapphire': ['../assets/icons/*'],
    },
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Office/Business :: Financial',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Environment :: X11 Applications :: Qt',
    ],
    keywords='defi ethereum wallet cryptocurrency blockchain',
    entry_points={
        'console_scripts': [
            'sapphire=sapphire.sapphire:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/Erslsf/Sapphire/issues',
        'Source': 'https://github.com/Erslsf/Sapphire',
    },
)
