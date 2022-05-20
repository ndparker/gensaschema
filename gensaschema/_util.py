# -*- coding: ascii -*-
r"""
:Copyright:

 Copyright 2014 - 2022
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

================
 Misc Utilities
================

Misc utilities.
"""
__author__ = u"Andr\xe9 Malo"


# pylint: disable = redefined-builtin, invalid-name, self-assigning-variable
try:
    unicode  # pylint: disable = used-before-assignment
except NameError:  # pragma: no cover
    unicode = str
else:  # pragma: no cover
    unicode = unicode

try:
    bytes  # pylint: disable = used-before-assignment
except NameError:  # pragma: no cover
    bytes = str
else:  # pragma: no cover
    bytes = bytes

py2 = bytes is str

try:
    cmp  # pylint: disable = used-before-assignment
except NameError:  # pragma: no cover
    cmp = lambda a, b: (a > b) - (a < b)
else:  # pragma: no cover
    cmp = cmp


def find_public(space):
    """
    Determine all public names in space

    If the space contains an ``__all__`` sequence, a copy is returned (as a
    list). Otherwise, all symbol names not starting with an underscore are
    listed.

    Parameters:
      space (dict):
        Name space to inspect

    Returns:
      list: List of public names
    """
    if '__all__' in space:
        return list(space['__all__'])
    return [key for key in space.keys() if not key.startswith('_')]
