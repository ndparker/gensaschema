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

=================================
 Tests for gensaschema._template
=================================

Tests for gensaschema._template
"""
__author__ = u"Andr\xe9 Malo"

from pytest import raises

from gensaschema import _template

# pylint: disable = invalid-name, protected-access


def test_Template_init():
    """ _template.Template initializes properly """
    inst = _template.Template("""
        lalala

         lolo
    """)
    assert inst._template == 'lalala\n\n lolo'

    inst = _template.Template("""
        lalala

         lolo
    """, dedent=False)
    assert inst._template == '\n        lalala\n\n         lolo'

    inst = _template.Template("""
        lalala

         lolo
    """, dedent=False, rstrip=False)
    assert inst._template == '\n        lalala\n\n         lolo\n    '


def test_Template_expand():
    """ _template.Template().expand() works as expected """
    inst = _template.Template("""%s xxx %d""")
    assert inst.expand() == '%s xxx %d'
    assert inst.expand('blah', 12) == 'blah xxx 12'
    with raises(TypeError):
        inst.expand(foo='blah', bar=12)

    inst = _template.Template("""%(foo)s xxx %(bar)d""")
    assert inst.expand() == '%(foo)s xxx %(bar)d'
    assert inst.expand(foo='blah', bar=12) == 'blah xxx 12'
    with raises(TypeError):
        inst.expand('blah', 12)

    with raises(TypeError) as e:
        inst.expand('blah', bar=12)
    assert e.value.args == ('Both args and kwargs given',)
