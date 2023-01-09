# -*- coding: ascii -*-
u"""
==========
 Metadata
==========

Schema module generation code.

:Copyright:

 Copyright 2023
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

import sqlalchemy as _sa


class BoundMetaData(object):
    """
    Bound metadata proxy - SA 2.0 removed the bind, but it's part of our APIs
    """
    def __init__(self, bind):
        self._metadata = _sa.MetaData()
        self.bind = bind

    def __getattr__(self, name):
        return getattr(self._metadata, name)
