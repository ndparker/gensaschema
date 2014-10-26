# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2014
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

GenSASchema - Static SQLAlchemy Schema Generator.
"""
__author__ = u"Andr\xe9 Malo"
__docformat__ = "restructuredtext en"
__license__ = "Apache License, Version 2.0"
__version__ = ('0.1.0', False, 1)

# pylint: disable = W0611
from gensaschema import _util
from gensaschema import _version
from gensaschema._exceptions import *  # noqa pylint: disable = W0401, W0614, W0622

#: Version of the gensaschema package
version = _version.Version(*__version__)

__all__ = _util.find_public(globals())
