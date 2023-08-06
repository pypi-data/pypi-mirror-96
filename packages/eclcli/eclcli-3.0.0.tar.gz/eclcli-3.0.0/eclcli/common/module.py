#   Copyright 2013 Nebula Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""Module action implementation"""

import six
import sys

from eclcli.common import command
from eclcli.common import utils


class ListCommand(command.Lister):
    """List recognized commands by group"""

    auth_required = False

    def take_action(self, parsed_args):
        cm = self.app.command_manager
        groups = cm.get_command_groups()

        columns = ('Command Group', 'Commands')
        return (columns, ((c, utils.format_lister(cm.get_command_names(group=c))) for c in groups))


class ListModule(command.ShowOne):
    """List module versions"""

    auth_required = False

    def get_parser(self, prog_name):
        parser = super(ListModule, self).get_parser(prog_name)
        parser.add_argument(
            '--all',
            action='store_true',
            default=False,
            help='Show all modules that have version information',
        )
        return parser

    def take_action(self, parsed_args):

        data = {}
        # Get module versions
        mods = sys.modules
        for k in mods.keys():
            k = k.split('.')[0]
            # TODO(dtroyer): Need a better way to decide which modules to
            #                show for the default (not --all) invocation.
            #                It should be just the things we actually care
            #                about like client and plugin modules...
            if (parsed_args.all or 'client' in k):
                try:
                    data[k] = mods[k].__version__
                except AttributeError:
                    # aw, just skip it
                    pass

        return zip(*sorted(six.iteritems(data)))
