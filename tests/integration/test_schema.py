# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2016 - 2022
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
__author__ = u"Andr\xe9 Malo"

import os as _os
import sys as _sys
import warnings as _warnings

import sqlalchemy as _sa

from gensaschema import _symbols
from gensaschema import _schema

# pylint: disable = invalid-name

sa_version = tuple(map(int, _sa.__version__.split('.')[:3]))


def test_schema(tmpdir):
    """ _schema.Schema() works as expected """
    _warnings.simplefilter('error', _sa.exc.SAWarning)

    tmpdir = str(tmpdir)
    filename = _os.path.join(tmpdir, 'tabletest.db')

    db = _sa.create_engine('sqlite:///%s' % (filename,)).connect()
    try:
        db.execute('''
            CREATE TABLE names (
                id  INT(11) PRIMARY KEY,
                first  VARCHAR(128) DEFAULT NULL,
                last   VARCHAR(129) NOT NULL
            );
        ''')
        db.execute('''
            CREATE TABLE emails (
                id  INT(11) PRIMARY KEY,
                address  VARCHAR(127) NOT NULL,

                UNIQUE (address)
            );
        ''')
        db.execute('''
            CREATE TABLE addresses (
                id  INT(11) PRIMARY KEY,
                zip_code  VARCHAR(32) DEFAULT NULL,
                place     VARCHAR(78) NOT NULL,
                street    VARCHAR(64) DEFAULT NULL
            );
        ''')
        db.execute('''
            CREATE TABLE persons (
                id  INT(11) PRIMARY KEY,
                address  INT(11) NOT NULL,
                name  INT(11) NOT NULL,
                email  INT(11) DEFAULT NULL,

                FOREIGN KEY (address) REFERENCES addresses (id),
                FOREIGN KEY (name) REFERENCES names (id),
                FOREIGN KEY (email) REFERENCES emails (id)
            );
        ''')
        db.execute('''
            ALTER TABLE addresses
                ADD COLUMN owner INT(11) DEFAULT NULL REFERENCES persons (id);
        ''')
        db.execute('''
            CREATE TABLE temp.blub (id INT PRIMARY KEY);
        ''')
        schema = _schema.Schema(
            db, [('persons', 'persons'), ('blah', 'temp.blub')],
            {'temp': 'foo.bar.baz'},
            _symbols.Symbols(dict(type='t')), dbname='foo'
        )
    finally:
        db.close()

    with open(_os.path.join(tmpdir, "schema.py"), 'w') as fp:
        schema.dump(fp)

    with open(_os.path.join(tmpdir, "schema.py")) as fp:
        result = fp.read()

    expected = '''
# -*- coding: ascii -*-
# flake8: noqa pylint: skip-file
"""
==============================
 SQLAlchemy schema definition
==============================

SQLAlchemy schema definition for foo.

:Warning: DO NOT EDIT, this file is generated
"""

import sqlalchemy as _sa
from sqlalchemy.dialects import sqlite as t
from foo.bar import baz as _baz
from gensaschema.constraints import ForeignKey as ForeignKey
from gensaschema.constraints import PrimaryKey as PrimaryKey
from gensaschema.constraints import Unique as Unique

m = _sa.MetaData()
T = _sa.Table
C = _sa.Column
D = _sa.DefaultClause

# Table "addresses"
addresses = T(u'addresses', m,
    C('id', t.INTEGER%(nullable)s),
    C('zip_code', t.VARCHAR(32), server_default=D(u'NULL')),
    C('place', t.VARCHAR(78), nullable=False),
    C('street', t.VARCHAR(64), server_default=D(u'NULL')),
    C('owner', t.INTEGER, server_default=D(u'NULL')),
)
PrimaryKey(addresses.c.id)

# Defined at table 'persons':
# ForeignKey(
#     [addresses.c.owner],
#     [persons.c.id],
# )


# Table "emails"
emails = T(u'emails', m,
    C('id', t.INTEGER%(nullable)s),
    C('address', t.VARCHAR(127), nullable=False),
)
PrimaryKey(emails.c.id)
Unique(emails.c.address)


# Table "names"
names = T(u'names', m,
    C('id', t.INTEGER%(nullable)s),
    C('first', t.VARCHAR(128), server_default=D(u'NULL')),
    C('last', t.VARCHAR(129), nullable=False),
)
PrimaryKey(names.c.id)


# Table "persons"
persons = T(u'persons', m,
    C('id', t.INTEGER%(nullable)s),
    C('address', t.INTEGER, nullable=False),
    C('name', t.INTEGER, nullable=False),
    C('email', t.INTEGER, server_default=D(u'NULL')),
)
PrimaryKey(persons.c.id)
ForeignKey(
    [persons.c.address],
    [addresses.c.id],
)
ForeignKey(
    [persons.c.email],
    [emails.c.id],
)
ForeignKey(
    [persons.c.name],
    [names.c.id],
)

# Foreign key belongs to 'addresses':
ForeignKey(
    [addresses.c.owner],
    [persons.c.id],
)


del _sa, T, C, D, m

# vim: nowrap tw=0
    '''.strip() + '\n'
    if bytes is not str:
        expected = expected.replace("u'", "'")
    expected %= dict(
        nullable=("" if sa_version >= (1, 4) else ", nullable=False")
    )
    assert result == expected

    result = result.replace('from foo.bar import baz as _baz', '')
    glob, loc = {}, {}
    code = compile(result, "schema.py", "exec")
    # pylint: disable = exec-used, eval-used
    if _sys.version_info >= (3,):
        exec(code, glob, loc)
    else:
        exec("exec result in glob, loc")
