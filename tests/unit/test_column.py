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
 Tests for gensaschema._column
===============================

Tests for gensaschema._column
"""
__author__ = u"Andr\xe9 Malo"

from pytest import skip

import sqlalchemy as _sa
from sqlalchemy.dialects import mysql as _mysql

from gensaschema import _column
from gensaschema import _symbols

from .. import _util as _test

# pylint: disable = invalid-name


def test_ServerDefault():
    """ _column.ServerDefault() works as expected """
    default = _test.Bunch(for_update=None, arg=12)
    symbols = dict(default='DEF')

    if bytes is str:
        inst = _column.ServerDefault(default, symbols)
        assert repr(inst) == "DEF(u'12')"

        default.for_update = u'lalala'
        assert repr(inst) == "DEF(u'12', for_update=True)"
    else:
        inst = _column.ServerDefault(default, symbols)
        assert repr(inst) == "DEF('12')"

        default.for_update = u'lalala'
        assert repr(inst) == "DEF('12', for_update=True)"


def test_Column():
    """ _column.Column() works as expected """
    meta = _sa.MetaData()
    table = _sa.Table(
        u'mytable', meta,
        _sa.Column(u'Lala', _mysql.VARCHAR(255), nullable=True,
                   server_default='""'),
        _sa.Column(u'lolo', _mysql.INTEGER, primary_key=True,
                   autoincrement=False),
    )
    meta.bind = _test.Bunch(dialect=_test.Bunch(name='mysql'))
    symbols = _symbols.Symbols(symbols=dict(type="TT"))

    inst = _column.Column.from_sa(table.c.Lala, symbols)
    if bytes is str:
        assert repr(inst) == ('C(\'Lala\', TT.VARCHAR(255), '
                              'server_default=D(u\'""\'))')
    else:
        assert repr(inst) == ('C(\'Lala\', TT.VARCHAR(255), '
                              'server_default=D(\'""\'))')

    inst = _column.Column.from_sa(table.c.lolo, symbols)
    assert repr(inst) == ("C('lolo', TT.INTEGER, nullable=False, "
                          "autoincrement=False)")


def test_Column_identity():
    """ _column.Column() works ith identity """
    if not getattr(_sa, 'Identity', None):
        skip("Identity not defined")

    meta = _sa.MetaData()
    table = _sa.Table(
        u'mytable', meta,
        _sa.Column(u'Lala', _mysql.VARCHAR(255), _sa.Identity()),
        _sa.Column(u'lolo', _mysql.INTEGER, primary_key=True,
                   autoincrement=False),
    )
    meta.bind = _test.Bunch(dialect=_test.Bunch(name='mysql'))
    symbols = _symbols.Symbols(symbols=dict(type="TT"))

    inst = _column.Column.from_sa(table.c.Lala, symbols)
    if bytes is str:
        assert repr(inst) == ('C(\'Lala\', TT.VARCHAR(255), '
                              'nullable=False, '
                              'server_default=_sa.Identity())')
    else:
        assert repr(inst) == ('C(\'Lala\', TT.VARCHAR(255), '
                              'nullable=False, '
                              'server_default=_sa.Identity())')

    inst = _column.Column.from_sa(table.c.lolo, symbols)
    assert repr(inst) == ("C('lolo', TT.INTEGER, nullable=False, "
                          "autoincrement=False)")
