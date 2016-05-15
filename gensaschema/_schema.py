# -*- coding: ascii -*-
r"""
==========================
 Schema module generation
==========================

Schema module generation code.

:Copyright:

 Copyright 2010 - 2016
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
if __doc__:  # pragma: no branch
    # pylint: disable = redefined-builtin
    __doc__ = __doc__.encode('ascii').decode('unicode_escape')
__author__ = r"Andr\xe9 Malo".encode('ascii').decode('unicode_escape')
__docformat__ = "restructuredtext en"

import sqlalchemy as _sa

from . import _table
from . import _template


class Schema(object):
    """
    Schema container

    :CVariables:
      `_MODULE_TPL` : ``Template``
        Template for the module

    :IVariables:
      `_dialect` : ``str``
        Dialect name

      `_tables` : `TableCollection`
        Table collection

      `_schemas` : ``dict``
        Schema -> module mapping

      `_symbols` : `Symbols`
        Symbol table

      `_dbname` : ``str`` or ``None``
        DB identifier
    """

    _MODULE_TPL = _template.Template('''
        # -*- coding: ascii -*-  pylint: skip-file
        """
        ==============================
         SQLAlchemy schema definition
        ==============================

        SQLAlchemy schema definition%(dbspec)s.

        :Warning: DO NOT EDIT, this file is generated
        """
        __docformat__ = "restructuredtext en"

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
    ''')

    def __init__(self, conn, tables, schemas, symbols, dbname=None):
        """
        Initialization

        :Parameters:
          `conn` : ``Connection`` or ``Engine``
            SQLAlchemy connection or engine

          `tables` : ``list``
            List of tables to reflect, (local name, table name) pairs

          `schemas` : ``dict``
            schema -> module mapping

          `symbols` : `Symbols`
            Symbol table

          `dbname` : ``str``
            Optional db identifier. Used for informational purposes. If
            omitted or ``None``, the information just won't be emitted.
        """
        metadata = _sa.MetaData(conn)
        self._dialect = metadata.bind.dialect.name
        self._tables = _table.TableCollection.by_names(
            metadata, tables, schemas, symbols
        )
        self._schemas = schemas
        self._symbols = symbols
        self._dbname = dbname

    def dump(self, fp):
        """
        Dump schema module to fp

        :Parameters:
          `fp` : ``file``
            File to write to
        """
        imports = [item % self._symbols for item in self._symbols.imports]
        if imports:  # pragma: no branch
            imports.sort()
            imports.append('')
        lines = []
        for table in self._tables:
            if table.is_reference:
                continue
            if not lines:
                lines.append('')
            name = table.sa_table.name.encode('ascii', 'backslashescape')
            if bytes is not str:  # pragma: no cover
                name = name.decode('ascii')
            lines.append('# Table "%s"' % (name,))
            lines.append('%s = %r' % (table.varname, table))
            lines.append('')
            lines.append('')

        param = dict(((str(key), value) for key, value in self._symbols),
                     dbspec=" for %s" % self._dbname if self._dbname else "",
                     dialect=self._dialect,
                     imports='\n'.join(imports),
                     lines='\n'.join(lines))
        fp.write(self._MODULE_TPL.expand(**param))
        fp.write('\n')
