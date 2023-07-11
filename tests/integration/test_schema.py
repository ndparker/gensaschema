# -*- coding: ascii -*-
# pylint: disable = line-too-long
u"""
:Copyright:

 Copyright 2016 - 2023
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

=========================
 Schema generation tests
=========================

Schema generation tests
"""
__author__ = u"Andr\xe9 Malo, Andr\xe9s Reyes Monge"

import os as _os
import sys as _sys
import warnings as _warnings

import sqlalchemy as _sa

from gensaschema import _symbols
from gensaschema import _schema

# pylint: disable = invalid-name

sa_version = tuple(map(int, _sa.__version__.split('.')[:3]))


def runner(db):
    """Create runner"""

    def run(stmt):
        """Run"""
        with db.begin():
            db.execute(_sa.text(stmt))

    return run


def test_schema(tmpdir):
    """_schema.Schema() works as expected"""
    _warnings.simplefilter('error', _sa.exc.SAWarning)

    tmpdir = str(tmpdir)
    filename = _os.path.join(tmpdir, 'tabletest.db')

    db = _sa.create_engine('sqlite:///%s' % (filename,)).connect()
    try:
        run = runner(db)
        run(
            '''
            CREATE TABLE names (
                id  INT(11) PRIMARY KEY,
                first  VARCHAR(128) DEFAULT NULL,
                last   VARCHAR(129) NOT NULL
            );
        '''
        )
        run(
            '''
            CREATE TABLE emails (
                id  INT(11) PRIMARY KEY,
                address  VARCHAR(127) NOT NULL,

                UNIQUE (address)
            );
        '''
        )
        run(
            '''
            CREATE TABLE addresses (
                id  INT(11) PRIMARY KEY,
                zip_code  VARCHAR(32) DEFAULT NULL,
                place     VARCHAR(78) NOT NULL,
                street    VARCHAR(64) DEFAULT NULL
            );
        '''
        )
        run(
            '''
            CREATE TABLE persons (
                id  INT(11) PRIMARY KEY,
                address  INT(11) NOT NULL,
                name  INT(11) NOT NULL,
                email  INT(11) DEFAULT NULL,

                FOREIGN KEY (address) REFERENCES addresses (id),
                FOREIGN KEY (name) REFERENCES names (id),
                FOREIGN KEY (email) REFERENCES emails (id)
            );
        '''
        )
        run(
            '''
            ALTER TABLE addresses
                ADD COLUMN owner INT(11) DEFAULT NULL REFERENCES persons (id);
        '''
        )
        run(
            '''
            CREATE TABLE temp.blub (id INT PRIMARY KEY);
        '''
        )
        schema = _schema.Schema(
            db,
            [('persons', 'persons'), ('blah', 'temp.blub')],
            {'temp': 'foo.bar.baz'},
            _symbols.Symbols(dict(type='t')),
            dbname='foo',
        )
    finally:
        db.close()

    with open(_os.path.join(tmpdir, "schema.py"), 'w') as fp:
        schema.dump(fp)

    with open(_os.path.join(tmpdir, "schema.py")) as fp:
        result = fp.read()

    expected = (
        '''
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
    '''.strip()
        + '\n'
    )
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


def test_postgresql_schema_with_enums(postgres_url, tmpdir):
    _warnings.simplefilter("error", _sa.exc.SAWarning)

    tmpdir = str(tmpdir)
    db = _sa.create_engine(postgres_url).connect()
    try:
        run = runner(db)
        run(
            """
            CREATE TYPE card AS ENUM ('visa', 'mastercard', 'amex');
            CREATE TABLE names (
                id  serial PRIMARY KEY,
                first  VARCHAR(128) DEFAULT NULL,
                last   VARCHAR(129) NOT NULL,
                card_types card ARRAY NOT NULL
            );
        """
        )
        run(
            """
            CREATE TABLE emails (
                id  serial PRIMARY KEY,
                address  VARCHAR(127) NOT NULL,

                UNIQUE (address)
            );
        """
        )
        run(
            """
            CREATE TABLE addresses (
                id  serial PRIMARY KEY,
                zip_code  VARCHAR(32) DEFAULT NULL,
                place     VARCHAR(78) NOT NULL,
                street    VARCHAR(64) DEFAULT NULL
            );
        """
        )
        run(
            """

            CREATE TABLE persons (
                id  serial PRIMARY KEY,
                address  INT NOT NULL,
                name  INT NOT NULL,
                email  INT DEFAULT NULL,
                card_types card ARRAY NOT NULL,

                FOREIGN KEY (address) REFERENCES addresses (id),
                FOREIGN KEY (name) REFERENCES names (id),
                FOREIGN KEY (email) REFERENCES emails (id)
            );
        """
        )
        run(
            """
            ALTER TABLE addresses
                ADD COLUMN owner INT DEFAULT NULL REFERENCES persons (id);
        """
        )
        schema = _schema.Schema(
            db,
            [
                ("names", "names"),
                ("emails", "emails"),
                ("addresses", "addresses"),
                ("persons", "persons"),
            ],
            {},
            _symbols.Symbols(dict(type="t")),
            dbname="foo",
        )
    finally:
        db.close()

    with open(_os.path.join(tmpdir, "schema.py"), "w") as fp:
        schema.dump(fp)

    with open(_os.path.join(tmpdir, "schema.py")) as fp:
        result = fp.read()

    expected = (
        '''
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
from sqlalchemy.dialects import postgresql as t
from gensaschema.constraints import ForeignKey as ForeignKey
from gensaschema.constraints import PrimaryKey as PrimaryKey
from gensaschema.constraints import Unique as Unique

m = _sa.MetaData()
T = _sa.Table
C = _sa.Column
D = _sa.DefaultClause

# Custom type definitions
enum_card = t.ENUM(u'visa', u'mastercard', u'amex', name='card')

# Table "addresses"
addresses = T(u'addresses', m,
    C('id', t.INTEGER, nullable=False, server_default=D(u"nextval('addresses_id_seq'::regclass)")),
    C('zip_code', t.VARCHAR(32), server_default=D(u'NULL::character varying')),
    C('place', t.VARCHAR(78), nullable=False),
    C('street', t.VARCHAR(64), server_default=D(u'NULL::character varying')),
    C('owner', t.INTEGER),
)
PrimaryKey(addresses.c.id, name=u'addresses_pkey')

# Defined at table 'persons':
# ForeignKey(
#     [addresses.c.owner],
#     [persons.c.id],
#     name=u'addresses_owner_fkey',
# )


# Table "emails"
emails = T(u'emails', m,
    C('id', t.INTEGER, nullable=False, server_default=D(u"nextval('emails_id_seq'::regclass)")),
    C('address', t.VARCHAR(127), nullable=False),
)
PrimaryKey(emails.c.id, name=u'emails_pkey')
Unique(emails.c.address, name=u'emails_address_key')


# Table "names"
names = T(u'names', m,
    C('id', t.INTEGER, nullable=False, server_default=D(u"nextval('names_id_seq'::regclass)")),
    C('first', t.VARCHAR(128), server_default=D(u'NULL::character varying')),
    C('last', t.VARCHAR(129), nullable=False),
    C('card_types', t.ARRAY(enum_card), nullable=False),
)
PrimaryKey(names.c.id, name=u'names_pkey')


# Table "persons"
persons = T(u'persons', m,
    C('id', t.INTEGER, nullable=False, server_default=D(u"nextval('persons_id_seq'::regclass)")),
    C('address', t.INTEGER, nullable=False),
    C('name', t.INTEGER, nullable=False),
    C('email', t.INTEGER),
    C('card_types', t.ARRAY(enum_card), nullable=False),
)
PrimaryKey(persons.c.id, name=u'persons_pkey')
ForeignKey(
    [persons.c.address],
    [addresses.c.id],
    name=u'persons_address_fkey',
)
ForeignKey(
    [persons.c.email],
    [emails.c.id],
    name=u'persons_email_fkey',
)
ForeignKey(
    [persons.c.name],
    [names.c.id],
    name=u'persons_name_fkey',
)

# Foreign key belongs to 'addresses':
ForeignKey(
    [addresses.c.owner],
    [persons.c.id],
    name=u'addresses_owner_fkey',
)


del _sa, T, C, D, m

# vim: nowrap tw=0
    '''.strip()
        + "\n"
    )
    if bytes is not str:
        expected = expected.replace("u'", "'").replace('u"', '"')
    assert result == expected
