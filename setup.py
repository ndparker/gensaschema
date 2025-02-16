#!/usr/bin/env python
# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2010 - 2025
 Andr\xe9 Malo or his licensors, as applicable

:License:

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

==================================================
 GenSASchema - Static SQLAlchemy Schema Generator
==================================================

GenSASchema - Static SQLAlchemy Schema Generator.
"""
__author__ = u"Andr\xe9 Malo"

import os as _os

# pylint: disable = no-name-in-module, import-error, raise-missing-from
import setuptools as _setuptools

# pylint: disable = invalid-name


def _doc(filename):
    """Read docs file"""
    # pylint: disable = unspecified-encoding
    args = {} if str is bytes else dict(encoding="utf-8")
    try:
        with open(_os.path.join("docs", filename), **args) as fp:
            return fp.read()
    except IOError:
        return None


package = dict(
    name="gensaschema",
    top="gensaschema",
    pathname="gensaschema",
    provides=_doc("PROVIDES"),
    desc="Static SQLAlchemy Schema Generator",
    longdesc=_doc("DESCRIPTION"),
    author=__author__,
    email="nd@perlig.de",
    url="https://opensource.perlig.de/gensaschema/",
    license="Apache License, Version 2.0",
    license_files=["LICENSE"],

    packages=True,
    # py_modules=[],
    # version_file='__init__.py',
    install_requires=[],

    entry_points={},

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Utilities",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)


def setup():
    """Main"""
    # pylint: disable = too-many-branches
    # pylint: disable = unspecified-encoding

    args = {} if str is bytes else dict(encoding="utf-8")
    version_file = "%s/%s" % (
        package["pathname"],
        package.get("version_file", "__init__.py"),
    )
    with open(version_file, **args) as fp:
        for line in fp:  # pylint: disable = redefined-outer-name
            if line.startswith("__version__"):
                version = line.split("=", 1)[1].strip()
                if version.startswith(("'", '"')):
                    version = version[1:-1].strip()
                break
        else:
            raise RuntimeError("Version not found")

    kwargs = {}

    if package.get("packages", True):
        kwargs["packages"] = [package["top"]] + [
            "%s.%s" % (package["top"], item)
            for item in _setuptools.find_packages(package["pathname"])
        ]

    if package.get("py_modules"):
        kwargs["py_modules"] = package["py_modules"]
    if package.get("license_files"):
        kwargs["license_files"] = package["license_files"]
    if package.get("license"):
        kwargs["license"] = package["license"]
    if package.get("classifiers"):
        kwargs["classifiers"] = package["classifiers"]
    if package.get("entry_points"):
        kwargs["entry_points"] = package["entry_points"]

    _setuptools.setup(
        name=package["name"],
        author=package["author"],
        author_email=package["email"],
        description=package["desc"],
        long_description=package["longdesc"],
        url=package["url"],
        install_requires=package["install_requires"],
        version=version,
        zip_safe=False,
        **kwargs
    )


if __name__ == "__main__":
    setup()
