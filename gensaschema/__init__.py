# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2014 - 2023
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

==================================================
 GenSASchema - Static SQLAlchemy Schema Generator
==================================================

GenSASchema generates static schema definitions using SQLAlchemy's
inspection capabilities.
"""
__author__ = u"Andr\xe9 Malo"
__license__ = "Apache License, Version 2.0"
__version__ = '0.6.8'

from gensaschema import _util
from gensaschema._exceptions import *  # noqa pylint: disable = redefined-builtin, wildcard-import

from gensaschema._config import Config  # noqa
from gensaschema._schema import Schema  # noqa
from gensaschema._symbols import Symbols, SymbolException  # noqa
from gensaschema._type import Type  # noqa

__all__ = _util.find_public(globals())
