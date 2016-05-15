# -*- coding: ascii -*-
r"""
:Copyright:

 Copyright 2016
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

==============================
 Tests for gensaschema._table
==============================

Tests for gensaschema._table
"""
if __doc__:
    # pylint: disable = redefined-builtin
    __doc__ = __doc__.encode('ascii').decode('unicode_escape')
__author__ = r"Andr\xe9 Malo".encode('ascii').decode('unicode_escape')
__docformat__ = "restructuredtext en"

import os as _os
import sqlite3 as _sqlite3

import sqlalchemy as _sa

from gensaschema import _symbols
from gensaschema import _table

# pylint: disable = invalid-name


def test_table(tmpdir):
    """ _table.Table() works as expected """
    tmpdir = str(tmpdir)
    filename = _os.path.join(tmpdir, 'tabletest.db')

    db = _sqlite3.connect(filename)
    db.cursor().execute('''
        CREATE TABLE stocks
        (date DATE, trans text, symbol varchar(12), qty real, price real,
         primary key (date))
    ''')
    db.close()

    db = _sa.create_engine('sqlite:///%s' % (filename,))
    meta = _sa.MetaData(db)
    table = _table.Table.by_name('stocks', 'STOCKS', meta, {},
                                 _symbols.Symbols())

    expected = (
        "T(u'stocks', m,\n"
        "    C('date', t.DATE, nullable=False),\n"
        "    C('trans', t.TEXT),\n"
        "    C('symbol', t.VARCHAR(12)),\n"
        "    C('qty', t.REAL),\n"
        "    C('price', t.REAL),\n"
        ")\n"
        "PrimaryKey(STOCKS.c.date)"
    )
    if bytes is not str:
        expected = expected.replace("u'", "'")
    assert repr(table) == expected
