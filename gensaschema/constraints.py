# -*- coding: ascii -*-
r"""
========================
 Constraint Declarators
========================

Helper functions to define constraints. These will be part of the generated
schema modules. Copy or the reference the module where needed. The location is
configurable.

:Copyright:

 Copyright 2010 - 2016
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
if __doc__:  # pragma: no branch
    # pylint: disable = redefined-builtin
    __doc__ = __doc__.encode('ascii').decode('unicode_escape')
__author__ = r"Andr\xe9 Malo".encode('ascii').decode('unicode_escape')
__docformat__ = "restructuredtext en"

import sqlalchemy as _sa


def Unique(*columns, **kwargs):  # pylint: disable = invalid-name
    """
    Append unique constraint

    :Parameters:
      `columns` : ``tuple``
        Constraint columns

      `kwargs` : ``dict``
        Additional arguments
    """
    columns[0].table.append_constraint(_sa.UniqueConstraint(
        *columns, **kwargs
    ))


def PrimaryKey(*columns, **kwargs):  # pylint: disable = invalid-name
    """
    Append primary key

    :Parameters:
      `columns` : ``tuple``
        Constraint columns

      `kwargs` : ``dict``
        Additional parameters
    """
    columns[0].table.append_constraint(_sa.PrimaryKeyConstraint(
        *columns, **kwargs
    ))


def ForeignKey(columns, refcolumns, **kwargs):  # noqa pylint: disable = invalid-name
    """
    Append foreign key

    :Parameters:
      `columns` : sequence
        Source columns

      `refcolumns` : sequence
        Referred columns

      `kwargs` : ``dict``
        Additional parameters
    """
    columns[0].table.append_constraint(_sa.ForeignKeyConstraint(
        [col.name for col in columns], refcolumns, link_to_name=True, **kwargs
    ))
