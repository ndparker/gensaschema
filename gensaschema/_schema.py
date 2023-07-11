# -*- coding: ascii -*-
u"""
==========================
 Schema module generation
==========================

Schema module generation code.

:Copyright:

 Copyright 2010 - 2023
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

from . import _meta
from . import _table
from . import _template


class Schema(object):
    """
    Schema container

    Attributes:
      _dialect (str):
        Dialect name

      _tables (TableCollection):
        Table collection

      _schemas (dict):
        Schema -> module mapping

      _symbols (Symbols):
        Symbol table

      _dbname (str or None):
        DB identifier
    """

    #: Template for the module
    #:
    #: :Type: Template
    _MODULE_TPL = _template.Template(
        '''
        # -*- coding: ascii -*-
        # flake8: noqa pylint: skip-file
        """
        ==============================
         SQLAlchemy schema definition
        ==============================

        SQLAlchemy schema definition%(dbspec)s.

        :Warning: DO NOT EDIT, this file is generated
        """

        import sqlalchemy as %(sa)s
        from sqlalchemy.dialects import %(dialect)s as %(type)s
        %(imports)s
        %(meta)s = %(sa)s.MetaData()
        %(table)s = %(sa)s.Table
        %(column)s = %(sa)s.Column
        %(default)s = %(sa)s.DefaultClause
        %(lines)s
        del %(sa)s, %(table)s, %(column)s, %(default)s, %(meta)s

        # vim: nowrap tw=0
    '''
    )

    def __init__(
        self, conn, tables, schemas, symbols, dbname=None, types=None
    ):
        """
        Initialization

        Parameters:
          conn (Connection or Engine):
            SQLAlchemy connection or engine

          tables (list):
            List of tables to reflect, (local name, table name) pairs

          schemas (dict):
            schema -> module mapping

          symbols (Symbols):
            Symbol table

          dbname (str):
            Optional db identifier. Used for informational purposes. If
            omitted or ``None``, the information just won't be emitted.

          types (callable):
            Extra type loader. If the type reflection fails, because
            SQLAlchemy cannot resolve it, the type loader will be called with
            the type name, (bound) metadata and the symbol table. It is
            responsible for modifying the symbols and imports *and* the
            dialect's ``ischema_names``. If omitted or ``None``, the reflector
            will always fail on unknown types.
        """
        metadata = _meta.BoundMetaData(conn)
        self._dialect = metadata.bind.dialect.name
        self._tables = _table.TableCollection.by_names(
            metadata, tables, schemas, symbols, types=types
        )
        self._schemas = schemas
        self._symbols = symbols
        self._dbname = dbname

    def dump(self, fp):
        """
        Dump schema module to fp

        Parameters:
          fp (file):
            File to write to
        """
        lines, dlines = [], []
        for table in self._tables:
            if table.is_reference:
                continue
            name = table.sa_table.name.encode('ascii', 'backslashescape')
            if bytes is not str:
                name = name.decode('ascii')
            lines.append('# Table "%s"' % (name,))
            lines.append('%s = %r' % (table.varname, table))
            lines.append('')
            lines.append('')

        imports = [item % self._symbols for item in self._symbols.imports]
        if imports:  # pragma: no branch
            imports.sort()
            imports.append('')

        defines = self._symbols.types.defines
        if defines:
            defined = []
            seen = set()
            for define in defines:
                for item in define(self._dialect, self._symbols):
                    if item not in seen:
                        defined.append(item)
                        seen.add(item)
            if defined:
                dlines = ['', '# Custom type definitions'] + defined

        if lines:
            dlines.append('')

        param = dict(
            ((str(key), value) for key, value in self._symbols),
            dbspec=" for %s" % self._dbname if self._dbname else "",
            dialect=self._dialect,
            imports='\n'.join(imports),
            lines='\n'.join(dlines + lines),
        )
        fp.write(self._MODULE_TPL.expand(**param))
        fp.write('\n')
