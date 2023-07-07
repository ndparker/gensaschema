# -*- coding: ascii -*-
u"""
====================================
 Type inspection and representation
====================================

Type inspection and representation.

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

import inspect as _inspect

import sqlalchemy as _sa

_have_signature = hasattr(_inspect, 'signature')


class Type(object):
    """
    Type container

    Attributes:
      _ctype (SA type):
        Column type

      _dialect (str):
        Dialect name

      _symbols (Symbols):
        Symbol table
    """

    def __init__(self, ctype, dialect_name, symbols):
        """
        Initialization

        Parameters:
          ctype (SA type):
            Column type

          dialect_name (str):
            Dialect name

          symbols (Symbols):
            Symbol table
        """
        self._ctype = _finalize_type(ctype, dialect_name, symbols)
        self._dialect = dialect_name
        self._symbols = symbols

    @classmethod
    def by_column(cls, column, symbols):
        """
        Construct by SA column

        Parameters:
          column (SA column):
            SA column

        Returns:
          Type: New Type instance
        """
        return cls(
            column.type,
            column.table.metadata.bind.dialect.name,
            symbols,
        )

    def __repr__(self):  # noqa: C901
        """
        Make string representation

        Returns:
          str: The string representation
        """
        # pylint: disable = too-many-branches, too-many-statements

        unset = object()

        try:
            try:
                custom_repr = self._symbols.types.instance_repr[self._ctype]
            except (KeyError, TypeError):
                try:
                    custom_repr = self._symbols.types.instance_repr[
                        self._ctype.__class__
                    ]
                except (KeyError, TypeError):
                    custom_repr = self._symbols.types.instance_repr[
                        self._ctype.__class__.__name__
                    ]
        except (KeyError, TypeError):
            pass
        else:
            return custom_repr(self._ctype, self._dialect, self._symbols)

        mod = self._symbols.types.resolve(self._ctype, self._dialect)
        params = []

        if _have_signature:
            try:
                # pylint: disable = no-member
                sign = _inspect.signature(self._ctype.__init__)
            except (TypeError, ValueError):
                pass
            else:
                varargs, kwds = None, False
                for arg in sign.parameters.values():
                    if arg.kind == arg.VAR_POSITIONAL:
                        varargs = arg
                        continue
                    elif arg.kind == arg.VAR_KEYWORD:
                        continue

                    value = getattr(self._ctype, arg.name, unset)
                    if value is unset:
                        continue

                    if arg.default is not arg.empty and arg.default == value:
                        kwds = arg.kind != arg.POSITIONAL_ONLY
                        continue
                    if isinstance(value, _sa.types.TypeEngine):
                        rvalue = repr(
                            self.__class__(
                                value, self._dialect, self._symbols
                            )
                        )
                    else:
                        rvalue = repr(value)

                    if kwds:
                        params.append('%s=%s' % (arg.name, rvalue))
                    else:
                        params.append(rvalue)
                if not kwds and varargs is not None:
                    if (
                        _find_class(self._ctype, '__init__')
                        is not _sa.types.TypeEngine
                    ):
                        params.extend(
                            list(
                                map(
                                    repr,
                                    getattr(self._ctype, varargs.name, ()),
                                )
                            )
                        )

        else:
            try:
                # pylint: disable = deprecated-method
                # pylint: disable = no-member
                spec = _inspect.getargspec(self._ctype.__init__)
            except TypeError:
                pass
            else:
                defaults = dict(zip(spec[0][::-1], (spec[3] or ())[::-1]))
                kwds = False
                for arg in spec[0][1:]:
                    value = getattr(self._ctype, arg, unset)
                    if value is unset:
                        continue

                    if arg in defaults and defaults[arg] == value:
                        kwds = True
                        continue
                    if isinstance(value, _sa.types.TypeEngine):
                        rvalue = repr(
                            self.__class__(
                                value, self._dialect, self._symbols
                            )
                        )
                    else:
                        rvalue = repr(value)
                    if kwds:
                        params.append('%s=%s' % (arg, rvalue))
                    else:
                        params.append(rvalue)
                if not kwds and spec[1] is not None:
                    if (
                        _find_class(self._ctype, '__init__')
                        is not _sa.types.TypeEngine
                    ):
                        params.extend(
                            list(map(repr, getattr(self._ctype, spec[1])))
                        )

        params = ', '.join(params)
        if params:
            params = "(%s)" % (params,)
        return "%s.%s%s" % (mod, self._ctype.__class__.__name__, params)


def _finalize_type(ctype, dialect, symbols):
    """
    Finalize type definitions and modifications

    :TODO: should be generalized at some point in the future.
    """

    if dialect == 'postgresql':
        if ctype.__class__.__name__ == 'ENUM':
            _add_postgres_enum(ctype, symbols)

    return ctype


def _add_postgres_enum(ctype, symbols):
    """Add postgres enum"""
    if ctype in symbols.types.instance_repr:
        return

    esymbol = "enum_%s" % (ctype.name,)

    def define(_, symbols):
        return ["%s = %s.%r" % (esymbol, symbols["type"], ctype)]

    def custom_repr(*_):
        return esymbol

    symbols.types.defines.append(define)
    symbols.types.instance_repr[ctype] = custom_repr


def _find_class(first_cls, name):
    """
    Find class where a method is defined

    Parameters:
      first_cls (type):
        Class to start with

      name (str):
        Method name

    Returns:
      type: class or ``None``
    """
    if not isinstance(first_cls, type):
        first_cls = first_cls.__class__

    for cls in _inspect.getmro(first_cls):  # pragma: no branch
        if name in cls.__dict__:
            return cls
    return None
