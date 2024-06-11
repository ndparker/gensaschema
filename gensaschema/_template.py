# -*- coding: ascii -*-
u"""
=============================
 Simple template abstraction
=============================

Simple template abstraction.

:Copyright:

 Copyright 2010 - 2024
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

import textwrap as _textwrap


class Template(object):
    """
    Template container

    Attributes:
      _template (str):
        Template string
    """

    def __init__(self, template, dedent=True, rstrip=True):
        """
        Initialization

        Parameters:
          template (str):
            Template string

          dedent (bool):
            Dedent automatically?

          rstrip (bool):
            rstrip the template automatically?
        """
        if dedent:
            template = _textwrap.dedent(template).lstrip()
        if rstrip:
            template = template.rstrip()
        self._template = template

    def expand(self, *args, **kwargs):
        """
        Expand the template

        Either `args` or `kwargs` may be given, but not both. If nothing is
        given, nothing will be expanded.

        Parameters:
          args (tuple):
            Positional parameters to expand

          kwargs (dict):
            Keyword arguments to expand

        Returns:
          str: The expanded string

        Raises:
          - `TypeError` : Both args and kwargs given
        """
        if args:
            if kwargs:
                raise TypeError("Both args and kwargs given")
            return self._template % args
        elif kwargs:
            return self._template % kwargs
        return self._template
