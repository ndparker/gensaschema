# -*- coding: ascii -*-
u"""
===================
 Symbol management
===================

Symbol management.

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

import keyword as _keyword
import operator as _op
import weakref as _weakref

from . import _exceptions
from . import _util


class SymbolException(_exceptions.Error):
    """Symbol error"""


class Symbols(object):
    """
    Symbol table

    Attributes:
      _symbols (dict):
        Symbols

      imports (_Imports):
        Import container

      types (_Types):
        Type container
    """

    def __init__(self, symbols=None, imports=None):
        """
        Initialization

        Parameters:
          symbols (dict):
            Initial symbols

          imports (iterable):
            List of initial (id, import statement) tuples. If omitted or
            ``None``, it's empty.
        """
        self._symbols = {}
        defaults = dict(
            sa="_sa",  # SQLAlchemy shortname
            meta="m",  # MetaData shortname
            table="T",  # Table shortname
            type="t",  # Type module shortname
            column="C",  # Column shortname
            default="D",  # DefaultClause shortname
            pk="PrimaryKey",  # PrimaryKey function name
            fk="ForeignKey",  # ForeignKey function name
            uk="Unique",  # UniqueKey function name
            constraints=(  # constraint function module
                __name__.rsplit('.', 1)[0] + '.constraints'
            ),
        )
        self.imports = _Imports(imports=imports)
        self.types = _Types(_weakref.proxy(self))
        if symbols is None:
            symbols = {}
        else:
            symbols = dict(symbols)
        for key, value in defaults.items():
            symbols.setdefault(key, value)
        for name, symbol in dict(symbols).items():
            self[name] = symbol

    def __delitem__(self, name):
        """
        Remove symbol entry if available

        Parameters:
          name (str):
            Symbol identifier
        """
        try:
            del self._symbols[name]
        except KeyError:
            pass

    def __setitem__(self, name, symbol):
        """
        Set symbol table entry

        Parameters:
          name (str):
            Symbol identifier

          symbol (str):
            Symbol

        Raises:
          SymbolException: Symbol could not be set because of some conflict
        """
        if _util.py2 and not isinstance(
            name, _util.unicode
        ):  # pragma: no cover
            name = str(name).decode('ascii')
        if _keyword.iskeyword(symbol):
            raise SymbolException(
                "Cannot use keyword %r as symbol" % (symbol,)
            )
        elif symbol in list(self._symbols.values()):
            if name in self._symbols and self._symbols[name] != symbol:
                raise SymbolException("Symbol conflict: %r" % (symbol,))
        elif name in self._symbols and self._symbols[name] != symbol:
            raise SymbolException("Symbol identifier conflict: %r" % (name,))
        self._symbols[name] = symbol

    def __getitem__(self, name):
        """
        Get symbol table entry

        Parameters:
          name (str):
            Symbol identifier

        Returns:
          str: The symbol

        Raises:
          KeyError: Symbol not found
        """
        if _util.py2 and not isinstance(name, _util.unicode):
            name = str(name).decode('ascii')
        return self._symbols[name]

    def __contains__(self, name):
        """
        Check symbol table entry

        Parameters:
          name (str):
            Symbol identifier

        Returns:
          bool: Does the symbol entry exist?
        """
        if _util.py2 and not isinstance(name, _util.unicode):
            name = str(name).decode('ascii')
        return name in self._symbols

    def __iter__(self):
        """
        Make item iterator (id, value)

        Returns:
          iterable: The iterator
        """
        return iter(list(self._symbols.items()))


class _Types(object):
    """
    Type container

    Attributes:
      _types (dict):
        Type map

      _symbols (Symbols):
        Symbol table
    """

    def __init__(self, symbols):
        """
        Initialization

        Parameters:
          symbols (Symbols):
            Symbol table
        """
        self._types = {}
        self._symbols = symbols
        self.instance_repr = {}
        self.defines = []

    def __setitem__(self, class_, symbol):
        """
        Set type

        Parameters:
          class_ (type):
            Type to match

          symbol (str):
            Type module symbol

        Raises:
          SymbolException: Type conflict
        """
        if class_ in self._types:
            if self._types[class_] != symbol:
                raise SymbolException("Type conflict: %r" % (symbol,))
        else:
            self._types[class_] = symbol

    def resolve(self, type_, dialect):
        """
        Resolve type to module symbol

        Parameters:
          type_ (object):
            Type to resolve

          dialect (str):
            Dialect name

        Returns:
          str: Resolved symbol

        Raises:
          SymbolException: Type could not be resolved
        """
        if type_.__class__ in self._types:
            return self._symbols[self._types[type_.__class__]]
        for class_, symbol in self._types.items():
            if isinstance(type_, class_):
                return self._symbols[symbol]

        mod = type_.__module__
        if mod.startswith('sqlalchemy.'):
            mod = '.'.join(mod.split('.')[:3])
            if mod == 'sqlalchemy.dialects.%s' % dialect:
                return self._symbols['type']
            else:
                try:
                    _load_dotted(
                        'sqlalchemy.dialects.%s.%s'
                        % (dialect, type_.__class__.__name__)
                    )
                    return self._symbols['type']
                except ImportError:
                    try:
                        _load_dotted(
                            'sqlalchemy.types.%s'
                            % (type_.__class__.__name__,)
                        )
                        return "%s.types" % (self._symbols['sa'],)
                    except ImportError:
                        pass
        raise SymbolException("Don't know how to address type %r" % (type_,))


class _Imports(object):
    """
    Import table

    Attributes:
      _imports (list):
        Import list
    """

    def __init__(self, imports=None):
        """
        Initialization

        Parameters:
          imports (iterable):
            List of initial (id, import statement) tuples. If omitted or
            ``None``, it's empty.
        """
        self._imports = list(imports or ())

    def __contains__(self, name):
        """
        Check if name is in imports

        Parameters:
          name (str):
            Import identifier

        Returns:
          bool: Does an import with that identifier exist?
        """
        for key, _ in self._imports:
            if key == name:
                return True
        return False

    def __setitem__(self, name, import_):
        """
        Set import

        Parameters:
          name (str):
            Symbolic name (to support import uniqueness)

          import_ (str):
            Import statement

        Raises:
          SymbolException: Import conflict
        """
        if _util.py2 and not isinstance(
            name, _util.unicode
        ):  # pragma: no cover
            name = str(name).decode('ascii')
        imports = dict(self._imports)
        if name in imports:
            if imports[name] != import_:
                raise SymbolException(
                    "Import conflict: %r: %r vs. %r"
                    % (name, imports[name], import_)
                )
        else:
            self._imports.append((name, import_))

    def __iter__(self):
        """
        Make iterator over the import statements

        Returns:
          iterable: The iterator
        """
        return iter(map(_op.itemgetter(1), self._imports))


def _load_dotted(name):
    """
    Load a dotted name

    (Stolen from wtf-server)

    The dotted name can be anything, which is passively resolvable
    (i.e. without the invocation of a class to get their attributes or
    the like).

    Parameters:
      name (str):
        The dotted name to load

    Returns:
      any: The loaded object

    Raises:
      ImportError: A module in the path could not be loaded
    """
    components = name.split('.')
    path = [components.pop(0)]
    obj = __import__(path[0])
    while components:
        comp = components.pop(0)
        path.append(comp)
        try:
            obj = getattr(obj, comp)
        except AttributeError:
            __import__('.'.join(path))
            try:
                obj = getattr(obj, comp)
            except AttributeError:
                # pylint: disable = raise-missing-from
                raise ImportError('.'.join(path))
    return obj
