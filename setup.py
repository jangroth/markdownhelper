#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

setup(
    author="Jan Groth",
    author_email="jan.groth.de@gmail.com",
    name="MarkdownHelper",
    long_description="Adds or removes table of contents to  markdown document.",
    version="1.0.0",
    license="GNU General Public License",
    install_requires=["click==7.1.2"],
    extras_require={
        "dev": [
            "appdirs==1.4.4",
            "attrs==20.2.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "autopep8==1.5.4",
            "black==19.10b0; python_version >= '3.6'",
            "bump2version==1.0.1",
            "cached-property==1.5.2",
            "cerberus==1.3.2",
            "certifi==2020.6.20",
            "chardet==3.0.4",
            "click==7.1.2",
            "colorama==0.4.4; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
            "coverage==5.3; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4' and python_version < '4'",
            "distlib==0.3.1",
            "flake8==3.8.4",
            "idna==2.10; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "iniconfig==1.1.1",
            "mccabe==0.6.1",
            "orderedmultidict==1.0.1",
            "packaging==20.4; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "pathspec==0.8.0",
            "pep517==0.8.2",
            "pip-shims==0.5.3; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
            "pipenv-setup==3.1.1",
            "pipfile==0.0.2",
            "plette[validation]==0.2.3; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "pluggy==0.13.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "py==1.9.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "pycodestyle==2.6.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "pyflakes==2.2.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "pyparsing==2.4.7; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "pytest==6.1.1",
            "pytest-cov==2.10.1",
            "python-dateutil==2.8.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "regex==2020.10.11",
            "requests==2.24.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
            "requirementslib==1.5.13; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
            "six==1.15.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "toml==0.10.1",
            "tomlkit==0.7.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
            "typed-ast==1.4.1",
            "urllib3==1.25.10; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4' and python_version < '4'",
            "vistir==0.5.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "wheel==0.35.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        ]
    },
    packages=find_packages(where="src", include=["markdownhelper"]),
    package_dir={"": "src"},
    test_suite="tests",
    tests_require=test_requirements,
    entry_points={"console_scripts": ["mdh=markdownhelper.mdh_cli:mdh"]},
)
