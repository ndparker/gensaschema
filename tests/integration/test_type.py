# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2016 - 2022
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

===============================
 Tests for gensaschema._type
===============================

Tests for gensaschema._type
"""
__author__ = u"Andr\xe9 Malo"

from pytest import skip

try:
    from sqlalchemy.dialects import mysql as _mysql
    import sqlalchemy as _sa
except ImportError:
    _sa, _mysql = None, None

from gensaschema import _type

# pylint: disable = protected-access


def test_find_class():
    """ _find_class() works as expected """
    if _sa is None or _mysql is None:
        skip("SA not installed")

    assert _type._find_class(_sa.Unicode, '__init__')
    assert _type._find_class(_sa.Unicode(255), '__init__')
    assert _type._find_class(_mysql.DATE, '__init__')
    assert _type._find_class(_mysql.ENUM('a', 'b'), '__init__')
