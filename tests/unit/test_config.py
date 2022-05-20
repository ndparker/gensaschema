# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2014 - 2022
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

===============================
 Tests for gensaschema._config
===============================

Tests for gensaschema._config
"""
__author__ = u"Andr\xe9 Malo"

import os as _os
import tempfile as _tempfile

from gensaschema import _config

# pylint: disable = protected-access


def fixture(name):
    """ Find fixture """
    return _os.path.join(
        _os.path.dirname(_os.path.normpath(_os.path.abspath(__file__))),
        'fixtures',
        name,
    )


def test_init():
    """ Config initialization works as expected """
    inst = _config.Config.from_file(fixture('config1.schema'))
    assert inst.tables == [
        ('Yo', 'Yo'),
        ('some', 'table'),
        ('somethingElse', 'somethingElse'),
        ('y', 'x.y'),
        ('a', 'b.c'),
    ]
    assert inst.schemas == {'foo': 'bar'}
    assert inst._lines == [
        '# This is a comment. I love comments.\n', '#\n', '\n', 'Yo\n',
        'some = table\n', 'somethingElse\n', 'x.y\n', 'a = b.c\n', '\n',
        '[schemas]\n', 'foo = bar\n',
    ]


def test_dump():
    """ Config dumps properly """
    inst = _config.Config(tables=[
        ('Yo', 'Yo'),
        ('some', 'table'),
        ('somethingElse', 'somethingElse'),
        ('y', 'x.y'),
        ('a', 'b.c'),
    ], schemas={'foo': 'bar'})

    fp = _tempfile.TemporaryFile(mode="w+")
    inst.dump(fp)
    fp.seek(0, 0)

    assert fp.read() == """
# This is a comment. I love comments.
#
# This files contains table names, one per line
# Comments and empty lines are ignored
#
# If the table name contains a dot, the first part is treated as
# schema name.
#
# If the table variable should be treated differently, use:
#
# name = table
#
# The basename of this file (modulo .schema extension) is used as
# basename for the python file.

Yo = Yo
some = table
somethingElse = somethingElse
y = x.y
a = b.c

[schemas]
foo = bar
    """.strip() + '\n'
    fp.close()
