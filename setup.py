#!/usr/bin/env python
# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2015 - 2018
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
__docformat__ = "restructuredtext en"

import os as _os

# pylint: disable = no-name-in-module, import-error
from distutils import core as _core
import setuptools as _setuptools

# pylint: disable = invalid-name


def _doc(filename):
    """ Read docs file """
    try:
        with open(_os.path.join('docs', filename)) as fp:
            return fp.read()
    except IOError:
        return None


def _lines(multiline):
    """ Split multiline string into single line % empty and comments """
    return [line for line in (
        line.strip() for line in multiline.splitlines(False)
    ) if line and not line.startswith('#')]


package = dict(
    name='gensaschema',
    top='gensaschema',
    pathname='gensaschema',
    provides=_doc('PROVIDES'),
    desc=_doc('SUMMARY').strip(),
    longdesc=_doc('DESCRIPTION'),
    author=__author__,
    email='nd@perlig.de',
    license="Apache License, Version 2.0",
    url='http://opensource.perlig.de/gensaschema/',
    classifiers=_lines(_doc('CLASSIFIERS') or ''),

    install_requires=_lines("""
    """),
)


def setup():
    """ Main """
    with open('%(pathname)s/__init__.py' % package) as fp:
        for line in fp:  # pylint: disable = redefined-outer-name
            if line.startswith('__version__'):
                version = line.split('=', 1)[1].strip()
                if version.startswith(("'", '"')):
                    version = version[1:-1].strip()
                break
        else:
            raise RuntimeError("Version not found")

    packages = [package['top']] + [
        '%s.%s' % (package['top'], item)
        for item in
        _setuptools.find_packages(package['pathname'])
    ]

    _core.setup(
        name=package['name'],
        author=package['author'],
        author_email=package['email'],
        license=package['license'],
        classifiers=package['classifiers'],
        description=package['desc'],
        long_description=package['longdesc'],
        url=package['url'],
        install_requires=package['install_requires'],
        packages=packages,
        version=version,
        zip_safe=False,
    )


if __name__ == '__main__':
    setup()
