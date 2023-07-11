# -*- coding: ascii -*-
u"""
==========================
 Schema config management
==========================

Schema config management.

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

import errno as _errno

if 1:
    try:
        import ConfigParser as _config_parser
    except ImportError:
        import configparser as _config_parser

    try:
        from cStringIO import StringIO as _TextIO
    except ImportError:
        from io import StringIO as _TextIO

from . import _template


class Config(object):
    """
    Schema config container

    Attributes:
      tables (list):
        Table list

      schemas (dict):
        Alien schema mapping

      _lines (list):
        Original config lines (or ``None``)
    """

    #: Template for empty config file
    #:
    #: :Type: `Template`
    _CONFIG_TPL = _template.Template(
        '''
        # This is a comment. I love comments.
        #
        # This files contains table names, one per line
        # Comments and empty lines are ignored
        #
        # If the table name contains a dot, the first part is treated as
        # schema name.
        #
        # If the table variable should be treated differently, use:
        #
        # name = table
        #
        # The basename of this file (modulo .schema extension) is used as
        # basename for the python file.
    '''
    )

    def __init__(self, tables, schemas, lines=None):
        """
        Initialization

        Parameters:
          tables (list):
            Table list

          schemas (dict):
            (Alien) Schema mapping

          lines (iterable):
            Original config lines. If omitted or ``None``, the config lines
            are not available.
        """
        self.tables = tables
        self.schemas = schemas
        self._lines = None if lines is None else list(lines)

    @classmethod
    def from_file(cls, name_or_file):
        """
        Construct from config file

        Parameters:
          name_or_file (str or file):
            Config filename or file pointer

        Returns:
          Config: New Config instance

        Raises:
          IOError: Error reading the file (except for ENOENT, which
                   treats the file as empty)
        """
        if name_or_file is None:
            lines = []
        else:
            read = getattr(name_or_file, 'read', None)
            if read is None:
                kwargs = {} if str is bytes else {'encoding': 'utf-8'}
                try:
                    # pylint: disable = bad-option-value, unspecified-encoding
                    # pylint: disable = bad-option-value, consider-using-with
                    fp = open(name_or_file, **kwargs)
                except IOError as e:
                    if e.errno != _errno.ENOENT:
                        raise
                    lines = []
                else:
                    try:
                        lines = fp.read().splitlines(True)
                    finally:
                        fp.close()
            else:
                lines = name_or_file.read().splitlines(True)
        return cls.from_lines(lines)

    @classmethod
    def from_lines(cls, lines):
        """
        Create from config lines

        Parameters:
          lines (iterable)
            List of config lines

        Returns:
          Config: New Config instance
        """
        conf_lines = ['[schemas]', '[tables]']
        for line in lines:
            line = line.rstrip()
            if not line or line.lstrip().startswith('#'):
                continue
            if '=' in line or ('[' in line and ']' in line):
                conf_lines.append(line)
            else:
                name = line
                if '.' in name:
                    name = name.rsplit('.', 1)[1]
                conf_lines.append('%s = %s' % (name, line))
        if bytes is str:
            parser = _config_parser.RawConfigParser()
            parser.optionxform = lambda x: x
            # pylint: disable = deprecated-method
            parser.readfp(_TextIO('\n'.join(conf_lines)))
        else:
            parser = _config_parser.RawConfigParser(strict=False)
            parser.optionxform = lambda x: x
            parser.read_file(_TextIO('\n'.join(conf_lines)))
        return cls.from_parser(parser, lines=lines)

    @classmethod
    def from_parser(cls, parser, lines=None):
        """
        Construct from config parser

        Parameters:
          parser (ConfigParser.RawConfigParser):
            Configparser instance

          lines (iterable):
            Original config lines

        Returns:
          Config: New Config instance
        """
        # pylint: disable = unnecessary-comprehension
        tables = [(name, val) for name, val in parser.items('tables')]
        schemas = dict((name, val) for name, val in parser.items('schemas'))
        return cls(tables, schemas, lines=lines)

    def dump(self, fp):
        """
        Dump config to a file

        Parameters:
          fp (file):
            Stream to dump to
        """
        lines = self._lines
        if not lines:
            result = self._CONFIG_TPL.expand().splitlines(False)
            if lines is None:
                tables = ['%s = %s' % table for table in self.tables]
                if tables:
                    result.append('')
                    result.extend(tables)
                schemas = [
                    '%s = %s' % (key, value)
                    for key, value in self.schemas.items()
                ]
                if schemas:
                    result.append('')
                    result.append('[schemas]')
                    result.extend(schemas)
        else:
            result = lines

        content = '\n'.join([line.rstrip() for line in result]) + '\n'
        try:
            fp.write('')
        except TypeError:
            content = content.encode('utf-8')
        fp.write(content)
