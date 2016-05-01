# -*- coding: ascii -*-
r"""
==========================================
 Constraint inspection and representation
==========================================

Constraint inspection and representation.

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
if __doc__:
    # pylint: disable = redefined-builtin
    __doc__ = __doc__.encode('ascii').decode('unicode_escape')
__author__ = r"Andr\xe9 Malo".encode('ascii').decode('unicode_escape')
__docformat__ = "restructuredtext en"

import keyword as _keyword
import re as _re
import tokenize as _tokenize

from . import _util


class Constraint(object):
    """
    Reflected Constraint

    :IVariables:
      `constraint` : SA Constraint
        Constraint
    """
    _SYMBOL, _IMPORT = None, None

    def __new__(cls, constraint, table, symbols, options=None):
        """ Constraint factory """
        if cls == Constraint:
            name = constraint.__class__.__name__
            if name == 'CheckConstraint':
                return None
            return globals()[name](
                constraint, table, symbols, options=options
            )
        return object.__new__(cls)

    def __init__(self, constraint, table, symbols, options=None):
        """
        Initialization

        :Parameters:
          `constraint` : SA Constraint
            Constraint

          `table` : ``str``
            Table varname
        """
        self.constraint = constraint
        self.table = table
        self._symbols = symbols
        self._symbols.imports[self._SYMBOL] = self._IMPORT
        self.options = options

    def copy(self):
        """ Create shallow copy """
        return self.__class__(
            self.constraint, self.table, self._symbols, self.options
        )

    def __cmp__(self, other):
        """ Compare """
        names = [
            'PrimaryKeyConstraint', 'UniqueConstraint',
            'ForeignKeyConstraint', 'CheckConstraint'
        ]

        def bytype(const):
            """ Sort by type """
            try:
                return names.index(const.__class__.__name__)
            except IndexError:
                return -1

        return cmp((
            bytype(self.constraint),
            self.options is not None,
            self.constraint.name,
        ), (
            bytype(other.constraint),
            other.options is not None,
            other.constraint.name,
        ))

    def repr(self, symbol, args, keywords=(), short=False):
        """
        Base repr for all constraints

        :Parameters:
          `args` : iterable
            Positional arguments

        :Return: The constraint repr
        :Rtype: ``str``
        """
        # pylint: disable = R0912
        # (too many branches)

        params = []
        if self.constraint.name is not None:
            params.append('name=%r' % (self.constraint.name,))
        if self.constraint.deferrable is not None:
            params.append('deferrable=%r' % (self.constraint.deferrable,))
        if self.constraint.initially is not None:
            params.append('initially=%r' % (self.constraint.initially,))
        for keyword in keywords:
            if getattr(self.constraint, keyword) is not None:
                params.append("%s=%r" % (
                    keyword, getattr(self.constraint, keyword)
                ))
        if short and len(params) > 1:
            short = False
        if args:
            if short:
                args = ', '.join(args)
            else:
                args = '\n    ' + ',\n    '.join(args) + ','
        else:
            args = ''

        if short:
            params = ', '.join(params)
            if args and params:
                params = ', ' + params
        else:
            params = ',\n    '.join(params)
            if params:
                params = '\n    ' + params + ','
            if args or params:
                params += '\n'

        return "%s(%s%s)" % (self._symbols[symbol], args, params)


def access_col(col):
    """
    Generate column access string (either as attribute or via dict access)

    :Parameters:
      `col` : SA Column
        Column

    :Return: Access string
    :Rtype: ``str``
    """
    try:
        name = col.name
    except AttributeError:
        name = col
    try:
        if _util.py2 and isinstance(name, _util.bytes):
            name.decode('ascii')
        else:
            name.encode('ascii')
    except UnicodeError:
        is_ascii = False
    else:
        is_ascii = True
    if is_ascii and not _keyword.iskeyword(name) and \
            _re.match(_tokenize.Name + '$', name):
        return ".c.%s" % name
    return ".c[%r]" % name


class UniqueConstraint(Constraint):
    """ Unique constraint """
    _SYMBOL = 'uk'
    _IMPORT = 'from %(constraints)s import Unique as %(uk)s'

    def __repr__(self):
        """
        Make string representation

        :Return: The string representation
        :Rtype: ``str``
        """
        empty = len(self.constraint.columns) == 0
        short = len(self.constraint.columns) <= 1
        result = self.repr(self._SYMBOL, [
            "%s%s" % (self.table, access_col(col))
            for col in self.constraint.columns
        ], short=short)
        if empty:
            result = "# %s" % result
        return result


class PrimaryKeyConstraint(UniqueConstraint):
    """ Primary Key constraint """
    _SYMBOL = 'pk'
    _IMPORT = 'from %(constraints)s import PrimaryKey as %(pk)s'


class ForeignKeyConstraint(Constraint):
    """ ForeignKey constraint """
    _SYMBOL = 'fk'
    _IMPORT = 'from %(constraints)s import ForeignKey as %(fk)s'

    def __repr__(self):
        """
        Make string representation

        :Return: The string representation
        :Rtype: ``str``
        """
        columns = "[%s]" % ',\n    '.join([
            "%s%s" % (self.table, access_col(col))
            for col in self.constraint.columns
        ])
        refcolumns = "[%s]" % ',\n    '.join(["%s%s" % (
            self._symbols[u'table_%s' % key.column.table.name],
            access_col(key.column),
        ) for key in self.constraint.elements])
        keywords = ['onupdate', 'ondelete']
        if self.constraint.use_alter:
            keywords.append('use_alter')
        result = self.repr('fk', [columns, refcolumns], keywords)

        if self.options:
            cyclic = self.constraint.use_alter
            if self.options.startswith('seen:'):
                table = self.options.split(None, 1)[1]
                if cyclic:
                    result = '\n# Cyclic foreign key:\n' + result
                else:
                    result = '\n# Foreign key belongs to %r:\n%s' % (
                        table, result
                    )
            elif self.options.startswith('unseen:'):
                table = self.options.split(None, 1)[1]
                result = result.splitlines(True)
                if cyclic:
                    result.insert(
                        0,
                        'Cyclic foreign key, defined at table %r:\n' % table
                    )
                else:
                    result.insert(0, 'Defined at table %r:\n' % table)
                result = '\n' + ''.join(['# %s' % item for item in result])

        return result
