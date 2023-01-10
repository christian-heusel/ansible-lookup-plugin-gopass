#
# This script comes with ABSOLUTELY NO WARRANTY, use at own risk
# Copyright (C) 2022 Christian Heusel <christian@heusel.eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Ansible lookup plugin for the gopass password manager [0].
#
# If the pass doesn't exist in the store it's generated. It accepts two extra
# parameters: length and symbols (if symbols is True or yes -n is appended to
# the pass generate command).
#
# example: {{ lookup('gopass', 'path/to/site', lenght=20, symbols=False) }}
#
# [0] https://www.gopass.pw/
#
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible.utils.display import Display

display = Display()

import subprocess

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.parsing.splitter import parse_kv

GOPASS_EXEC = 'gopass'

VALID_PARAMS = frozenset(('length', 'symbols', 'regenerate', 'list'))


def _parse_parameters(term, params):
    # Check for invalid parameters.  Probably a user typo
    invalid_params = frozenset(params.keys()).difference(VALID_PARAMS)
    if invalid_params:
        raise AnsibleError(
            'Unrecognized parameter(s) given to password lookup: %s' %
            ', '.join(invalid_params))

    # Set defaults
    params['length'] = params.get('length', 32)
    params["symbols"] = params.get('symbols', False)
    params["regenerate"] = params.get('regenerate', False)
    params["list"] = params.get('list', False)

    return term, params


def get_password(path):
    """Get password from pass."""
    command = f'{GOPASS_EXEC} show {path}'
    with subprocess.Popen(command,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as process:
        (stdout, stderr) = process.communicate()
        if process.returncode == 0:
            return stdout.splitlines()[0].decode('utf-8')

    raise Exception(stderr)

def list_password(path):
    """Get password list from pass."""
    command = f'{GOPASS_EXEC} list --flat {path}'
    with subprocess.Popen(command,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as process:
        (stdout, stderr) = process.communicate()
        if process.returncode == 0:
            lines = [line.decode("utf-8") for line in stdout.splitlines()]
            print(lines)
            return lines

    raise Exception(stderr)

def generate_password(path, length, symbols, force=False):
    """Generate password using gopass."""
    args = []
    if symbols:
        args.append('--symbols')
    if force:
        args.append('--force')

    command = f"{GOPASS_EXEC} generate {' '.join(args)} {path} {length}"
    display.vvv(f'COMMAND: {command}')
    with subprocess.Popen(command,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as process:
        (stdout, stderr) = process.communicate()
        if process.returncode != 0:
            raise Exception(stderr)


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        ret = []

        for term in terms:
            '''
            http://docs.python.org/2/library/subprocess.html#popen-constructor
            The shell argument (which defaults to False) specifies whether to use the
            shell as the program to execute. If shell is True, it is recommended to pass
            args as a string rather than as a sequence
            https://github.com/ansible/ansible/issues/6550
            '''
            name, params = _parse_parameters(term, kwargs)
            if params['list']:
                ret.append(list_password(name))
                continue
            if params['regenerate']:
                try:
                    generate_password(name,
                                      params['length'],
                                      params['symbols'],
                                      force=True)
                    display.vvv(f'Generated password for {name}')
                except Exception as e:
                    raise AnsibleError(
                        f"lookup_plugin.gopass({term}) returned {e.message}")

            try:
                password = get_password(term)
            except:
                try:
                    generate_password(name, params['length'],
                                      params['symbols'])
                    display.vvv(f'Generated password for {name}')
                    password = get_password(name)
                except Exception as e:
                    raise AnsibleError(
                        f"lookup_plugin.gopass({term}) returned {e.message}")
            ret.append(password)
        return ret
