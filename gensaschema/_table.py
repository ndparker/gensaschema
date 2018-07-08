# -*- coding: ascii -*-
u"""
=====================================
 Table inspection and representation
=====================================

Table inspection and representation

:Copyright:

 Copyright 2010 - 2018
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

"""
__author__ = u"Andr\xe9 Malo"
__docformat__ = "restructuredtext en"

import logging as _logging
import operator as _op
import re as _re
import warnings as _warnings

import sqlalchemy as _sa

from . import _column
from . import _constraint
from . import _util

logger = _logging.getLogger(__name__)


class Table(object):
    """
    Reflected table

    :CVariables:
      `is_reference` : ``bool``
        Is it a table reference or a table?

    :IVariables:
      `varname` : ``str``
        Variable name

      `sa_table` : ``sqlalchemy.Table``
        Table

      `constraints` : ``list``
        Constraint list

      `_symbols` : `Symbols`
        Symbol table
    """
    is_reference = False

    def __new__(cls, varname, table, schemas, symbols):
        """
        Construct

        This might actually return a table reference

        :Parameters:
          `varname` : ``str``
            Variable name

          `table` : ``sqlalchemy.Table``
            Table

          `schemas` : ``dict``
            Schema -> module mapping

          `symbols` : `Symbols`
            Symbol table

        :Return: `Table` or `TableReference` instance
        :Rtype: ``Table`` or ``TableReference``
        """
        if table.schema in schemas:
            return TableReference(
                varname, table, schemas[table.schema], symbols
            )
        return super(Table, cls).__new__(cls)

    def __init__(self, varname, table, schemas, symbols):
        """
        Initialization

        :Parameters:
          `varname` : ``str``
            Variable name

          `table` : ``sqlalchemy.Table``
            Table

          `schemas` : ``dict``
            Schema -> module mapping

          `symbols` : `Symbols`
            Symbol table
        """
        # pylint: disable = unused-argument

        symbols[u'table_%s' % table.name] = varname
        self._symbols = symbols
        self.varname = varname
        self.sa_table = table
        self.constraints = list(filter(None, [_constraint.Constraint(
            con, self.varname, self._symbols,
        ) for con in table.constraints]))

    @classmethod
    def by_name(cls, name, varname, metadata, schemas, symbols, types=None):
        """
        Construct by name

        :Parameters:
          `name` : ``str``
            Table name (possibly qualified)

          `varname` : ``str``
            Variable name of the table

          `metadata` : SA (bound) metadata
            Metadata container

          `schemas` : ``dict``
            Schema -> module mapping

          `symbols` : `Symbols`
            Symbol table

          `types` : callable
            Extra type loader. If the type reflection fails, because
            SQLAlchemy cannot resolve it, the type loader will be called with
            the type name, (bound) metadata and the symbol table. It is
            responsible for modifying the symbols and imports *and* the
            dialect's ``ischema_names``. If omitted or ``None``, the reflector
            will always fail on unknown types.

        :Return: New Table instance
        :Rtype: `Table`
        """
        kwargs = {}
        if '.' in name:
            schema, name = name.split('.')
            kwargs['schema'] = schema
        else:
            schema = None

        tmatch = _re.compile(u"^Did not recognize type (.+) of column").match

        def type_name(e):
            """ Extract type name from exception """
            match = tmatch(e.args[0])
            if match:
                type_name = match.group(1).strip()
                if type_name.startswith(('"', "'")):
                    type_name = type_name[1:-1]
                return type_name or None
            return None

        with _warnings.catch_warnings():
            _warnings.filterwarnings('error', category=_sa.exc.SAWarning,
                                     message=r'^Did not recognize type ')
            _warnings.filterwarnings('error', category=_sa.exc.SAWarning,
                                     message=r'^Unknown column definition ')
            _warnings.filterwarnings('error', category=_sa.exc.SAWarning,
                                     message=r'^Incomplete reflection of '
                                             r'column definition')
            _warnings.filterwarnings('ignore', category=_sa.exc.SAWarning,
                                     message=r'^Could not instantiate type ')
            _warnings.filterwarnings('ignore', category=_sa.exc.SAWarning,
                                     message=r'^Skipped unsupported '
                                             r'reflection of expression-based'
                                             r' index ')
            _warnings.filterwarnings('ignore', category=_sa.exc.SAWarning,
                                     message=r'^Predicate of partial index ')

            seen = set()
            while True:
                try:
                    table = _sa.Table(name, metadata, autoload=True, **kwargs)
                except _sa.exc.SAWarning as e:
                    if types is not None:
                        tname = type_name(e)
                        if tname and tname not in seen:
                            stack = [tname]
                            while stack:
                                try:
                                    types(stack[-1], metadata, symbols)
                                except _sa.exc.SAWarning as e:
                                    tname = type_name(e)
                                    if tname and tname not in stack and \
                                            tname not in seen:
                                        stack.append(tname)
                                        continue
                                    raise
                                else:
                                    seen.add(stack.pop())
                            continue
                    raise
                else:
                    break

        return cls(varname, table, schemas, symbols)

    def __repr__(self):
        """
        Make string representation

        :Return: The string representation
        :Rtype: ``str``
        """
        args = [
            repr(_column.Column.from_sa(col, self._symbols))
            for col in self.sa_table.columns
        ]
        if self.sa_table.schema is not None:
            args.append('schema=%r' % (_util.unicode(self.sa_table.schema),))

        args = ',\n    '.join(args)
        if args:
            args = ',\n    %s,\n' % args
        result = "%s(%r, %s%s)" % (
            self._symbols['table'],
            _util.unicode(self.sa_table.name),
            self._symbols['meta'],
            args,
        )
        if self.constraints:
            result = "\n".join((
                result, '\n'.join(map(repr, sorted(self.constraints)))
            ))
        return result


class TableReference(object):
    """ Referenced table """
    is_reference = True

    def __init__(self, varname, table, schema, symbols):
        """
        Initialization

        :Parameters:
          `varname` : ``str``
            Variable name

          `table` : ``sqlalchemy.Table``
            Table

          `symbols` : `Symbols`
            Symbol table
        """
        self.varname = varname
        self.sa_table = table
        self.constraints = []
        pkg, mod = schema.rsplit('.', 1)
        if not mod.startswith('_'):
            modas = '_' + mod
            symbols.imports[schema] = 'from %s import %s as %s' % (
                pkg, mod, modas
            )
            mod = modas
        else:
            symbols.imports[schema] = 'from %s import %s' % (pkg, mod)
        symbols[u'table_%s' % table.name] = "%s.%s" % (mod, varname)


class TableCollection(tuple):
    """ Table collection """

    @classmethod
    def by_names(cls, metadata, names, schemas, symbols, types=None):
        """
        Construct by table names

        :Parameters:
          `metadata` : ``sqlalchemy.MetaData``
            Metadata

          `names` : iterable
            Name list (list of tuples (varname, name))

          `symbols` : `Symbols`
            Symbol table

          `types` : callable
            Extra type loader. If the type reflection fails, because
            SQLAlchemy cannot resolve it, the type loader will be called with
            the type name, (bound) metadata and the symbol table. It is
            responsible for modifying the symbols and imports *and* the
            dialect's ``ischema_names``. If omitted or ``None``, the reflector
            will always fail on unknown types.

        :Return: New table collection instance
        :Rtype: `TableCollection`
        """
        objects = dict((table.sa_table.key, table) for table in [
            Table.by_name(name, varname, metadata, schemas, symbols,
                          types=types)
            for varname, name in names
        ])

        def map_table(sa_table):
            """ Map SA table to table object """
            if sa_table.key not in objects:
                varname = sa_table.name
                if _util.py2 and \
                        isinstance(varname,
                                   _util.unicode):  # pragma: no cover
                    varname = varname.encode('ascii')
                objects[sa_table.key] = Table(
                    varname, sa_table, schemas, symbols
                )
            return objects[sa_table.key]

        tables = list(map(map_table, metadata.tables.values()))
        tables.sort(key=lambda x: (not(x.is_reference), x.varname))

        _break_cycles(metadata)
        seen = set()

        for table in tables:
            seen.add(table.sa_table.key)
            for con in table.constraints:
                # pylint: disable = unidiomatic-typecheck
                if type(con) == _constraint.ForeignKeyConstraint:
                    if con.options == 'seen':
                        continue

                    remote_key = con.constraint.elements[0].column.table.key
                    if remote_key not in seen:
                        con.options = 'unseen: %s' % (
                            objects[remote_key].varname,
                        )
                        remote_con = con.copy()
                        remote_con.options = 'seen: %s' % (table.varname,)
                        objects[remote_key].constraints.append(remote_con)

        return cls(tables)


def _break_cycles(metadata):
    """
    Find foreign key cycles and break them apart

    :Parameters:
      `metadata` : ``sqlalchemy.MetaData``
        Metadata
    """
    def break_cycle(e):
        """ Break foreign key cycle """
        cycle_keys = set(map(_op.attrgetter('key'), e.cycles))
        cycle_path = [
            (parent, child)
            for parent, child in e.edges
            if parent.key in cycle_keys and child.key in cycle_keys
        ]
        deps = [cycle_path.pop()]
        while cycle_path:
            tmp = []
            for parent, child in cycle_path:
                if parent == deps[-1][1]:
                    deps.append((parent, child))
                else:
                    tmp.append((parent, child))
            if len(tmp) == len(cycle_path):
                raise AssertionError("Could not construct sorted cycle path")
            cycle_path = tmp
        if deps[0][0].key != deps[-1][1].key:
            raise AssertionError("Could not construct sorted cycle path")

        deps = list(map(_op.itemgetter(0), deps))
        first_dep = list(sorted(deps, key=_op.attrgetter('name')))[0]
        while first_dep != deps[-1]:
            deps = [deps[-1]] + deps[:-1]
        deps.reverse()
        logger.debug("Found foreign key cycle: %s", " -> ".join([
            repr(table.name) for table in deps + [deps[0]]
        ]))

        def visit_foreign_key(fkey):
            """ Visit foreign key """
            if fkey.column.table == deps[1]:
                fkey.use_alter = True
                fkey.constraint.use_alter = True

        _sa.sql.visitors.traverse(deps[0], dict(schema_visitor=True), dict(
            foreign_key=visit_foreign_key,
        ))

    while True:
        try:
            metadata.sorted_tables
        except _sa.exc.CircularDependencyError as e:
            break_cycle(e)
        else:
            break
