# -*- coding: ascii -*-
u"""
======================================
 Column inspection and representation
======================================

Column inspection and generation.

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

import sqlalchemy as _sa

from . import _type
from . import _util


class ServerDefault(object):
    """
    Default clause container

    Attributes:
      _default (Default clause):
        Default clause

      _symbols (Symbols):
        Symbol table
    """

    def __init__(self, default, symbols):
        """
        Initialization

        Parameters:
          default (Default clause):
            Default clause

          symbols (Symbols):
            Symbol table
        """
        self._default = default
        self._symbols = symbols

    def __repr__(self):
        """
        Make string representation

        Return:
          str: The string representation
        """
        identity = getattr(_sa, 'Identity', None)
        if identity is not None and isinstance(self._default, identity):
            return "%s.%s" % (
                self._symbols['sa'],
                _util.unicode(self._default),
            )

        if self._default.for_update:
            for_update = ", for_update=%r" % (True,)
        else:
            for_update = ""

        return "%s(%r%s)" % (
            self._symbols['default'],
            _util.unicode(self._default.arg),
            for_update,
        )


class Column(object):
    """
    Column container

    Attributes:
      _name (unicode):
        Name

      _ctype (SA type):
        Column type

      _nullable (bool):
        Nullable?

      _primary_key (bool):
        Part of a primary key?

      _autoincrement (bool):
        Possible autoincrement?

      _server_default (Default clause):
        Default clause

      _symbols (Symbols):
        Symbol table
    """

    def __init__(
        self,
        name,
        ctype,
        nullable,
        primary_key,
        autoincrement,
        server_default,
        symbols,
    ):
        """
        Initialization

        Parameters:
          name (unicode):
            Column name

          ctype (SA type):
            Column type

          nullable (bool):
            Nullable?

          primary_key (bool):
            Part of a primary key?

          autoincrement (bool):
            Possible autoincrement?

          server_default (Default clause):
            Default clause

          symbols (Symbols):
            Symbol table
        """
        self._name = name
        self._ctype = ctype
        self._nullable = nullable
        self._primary_key = primary_key
        self._autoincrement = autoincrement
        self._server_default = server_default
        self._symbols = symbols

    @classmethod
    def from_sa(cls, column, symbols):
        """
        Construct from SA column

        :Parameters:
          column (SA column):
            SA column

          symbols (Symbols):
            Symbol table

        Returns:
          Column: New column instance
        """
        return cls(
            column.name,
            _type.Type.by_column(column, symbols),
            nullable=column.nullable,
            primary_key=column.primary_key,
            autoincrement=column.autoincrement,
            server_default=column.server_default,
            symbols=symbols,
        )

    def __repr__(self):
        """
        Make string representation

        Returns:
          str: The string representation
        """
        params = list(map(repr, (self._name, self._ctype)))
        if not self._nullable:
            params.append('nullable=%r' % (False,))
        if not self._autoincrement and self._primary_key:
            params.append('autoincrement=%r' % (False,))
        if self._server_default is not None:
            params.append(
                'server_default=%r'
                % (ServerDefault(self._server_default, self._symbols),)
            )
        return "%s(%s)" % (self._symbols['column'], ', '.join(params))
