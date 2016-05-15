# -*- coding: ascii -*-
r"""
:Copyright:

 Copyright 2014 - 2016
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

========================
 GenSASchema Exceptions
========================

The module provides all exceptions and warnings used throughout the
`gensaschema` package.
"""
if __doc__:  # pragma: no branch
    # pylint: disable = redefined-builtin
    __doc__ = __doc__.encode('ascii').decode('unicode_escape')
__author__ = r"Andr\xe9 Malo".encode('ascii').decode('unicode_escape')
__docformat__ = "restructuredtext en"

import warnings as _warnings


class Error(Exception):
    """ Base exception for this package """


class Warning(Warning):  # noqa pylint: disable = redefined-builtin, undefined-variable
    """
    Base warning for this package

    >>> with _warnings.catch_warnings(record=True) as record:
    ...     Warning.emit('my message')
    ...     assert len(record) == 1
    ...     str(record[0].message)
    'my message'

    >>> _warnings.simplefilter('error')
    >>> Warning.emit('lalala')
    Traceback (most recent call last):
    ...
    Warning: lalala
    """

    @classmethod
    def emit(cls, message, stacklevel=1):  # pragma: no cover
        """
        Emit a warning of this very category

        This method is pure convenience. It saves you the unfriendly
        ``warnings.warn`` syntax (and the ``warnings`` import).

        :Parameters:
          `message` : any
            The warning message

          `stacklevel` : ``int``
            Number of stackframes to go up in order to place the warning
            source. This is useful for generic warning-emitting helper
            functions. The stacklevel of *this* helper function is already
            taken into account.
        """
        # Note that this method cannot be code-covered, probably because of
        # the stack magic.
        _warnings.warn(message, cls, max(1, stacklevel) + 1)
