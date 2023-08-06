#   Copyright 2012 OpenStack Foundation
#   Copyright 2013 Nebula Inc
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

"""Compute v2 Security Group action implementations"""

import six

try:
    from novaclient.v2 import security_group_rules
except ImportError:
    from novaclient.v1_1 import security_group_rules

from eclcli.common import command
from eclcli.common import parseractions
from eclcli.common import utils


def _xform_security_group_rule(sgroup):
    info = {}
    info.update(sgroup)
    from_port = info.pop('from_port')
    to_port = info.pop('to_port')
    if isinstance(from_port, int) and isinstance(to_port, int):
        port_range = {'port_range': "%u:%u" % (from_port, to_port)}
    elif from_port is None and to_port is None:
        port_range = {'port_range': ""}
    else:
        port_range = {'port_range': "%s:%s" % (from_port, to_port)}
    info.update(port_range)
    if 'cidr' in info['ip_range']:
        info['ip_range'] = info['ip_range']['cidr']
    else:
        info['ip_range'] = ''
    if info['ip_protocol'] is None:
        info['ip_protocol'] = ''
    elif info['ip_protocol'].lower() == 'icmp':
        info['port_range'] = ''
    group = info.pop('group')
    if 'name' in group:
        info['remote_security_group'] = group['name']
    else:
        info['remote_security_group'] = ''
    return info


def _xform_and_trim_security_group_rule(sgroup):
    info = _xform_security_group_rule(sgroup)
    # Trim parent security group ID since caller has this information.
    info.pop('parent_group_id', None)
    # Trim keys with empty string values.
    keys_to_trim = [
        'ip_protocol',
        'ip_range',
        'port_range',
        'remote_security_group',
    ]
    for key in keys_to_trim:
        if key in info and not info[key]:
            info.pop(key)
    return info


class CreateSecurityGroup(command.ShowOne):
    """Create a new security group"""

    def get_parser(self, prog_name):
        parser = super(CreateSecurityGroup, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="New security group name",
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="Security group description",
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        description = parsed_args.description or parsed_args.name

        data = compute_client.security_groups.create(
            parsed_args.name,
            description,
        )

        info = {}
        info.update(data._info)
        return zip(*sorted(six.iteritems(info)))


class CreateSecurityGroupRule(command.ShowOne):
    """Create a new security group rule"""

    def get_parser(self, prog_name):
        parser = super(CreateSecurityGroupRule, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Create rule in this security group (name or ID)',
        )
        parser.add_argument(
            "--proto",
            metavar="<proto>",
            default="tcp",
            help="IP protocol (icmp, tcp, udp; default: tcp)",
        )
        source_group = parser.add_mutually_exclusive_group()
        source_group.add_argument(
            "--src-ip",
            metavar="<ip-address>",
            default="0.0.0.0/0",
            help="Source IP address block (may use CIDR notation; default: "
                 "0.0.0.0/0)",
        )
        source_group.add_argument(
            "--src-group",
            metavar="<group>",
            help="Source security group (ID only)",
        )
        parser.add_argument(
            "--dst-port",
            metavar="<port-range>",
            default=(0, 0),
            action=parseractions.RangeAction,
            help="Destination port, may be a range: 137:139 (default: 0; "
                 "only required for proto tcp and udp)",
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        group = utils.find_resource(
            compute_client.security_groups,
            parsed_args.group,
        )
        if parsed_args.proto.lower() == 'icmp':
            from_port, to_port = -1, -1
        else:
            from_port, to_port = parsed_args.dst_port
        data = compute_client.security_group_rules.create(
            group.id,
            parsed_args.proto,
            from_port,
            to_port,
            parsed_args.src_ip,
            parsed_args.src_group,
        )

        info = _xform_security_group_rule(data._info)
        return zip(*sorted(six.iteritems(info)))


class ListSecurityGroupRule(command.Lister):
    """List security group rules"""

    def get_parser(self, prog_name):
        parser = super(ListSecurityGroupRule, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            nargs='?',
            help='List all rules in this security group (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        columns = column_headers = (
            "ID",
            "IP Protocol",
            "IP Range",
            "Port Range",
            "Remote Security Group",
        )

        rules_to_list = []
        if parsed_args.group:
            group = utils.find_resource(
                compute_client.security_groups,
                parsed_args.group,
            )
            rules_to_list = group.rules
        else:
            columns = columns + ('parent_group_id',)
            column_headers = column_headers + ('Security Group',)
            for group in compute_client.security_groups.list():
                rules_to_list.extend(group.rules)

        # Argh, the rules are not Resources...
        rules = []
        for rule in rules_to_list:
            rules.append(security_group_rules.SecurityGroupRule(
                compute_client.security_group_rules,
                _xform_security_group_rule(rule),
            ))

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in rules))


class SetSecurityGroup(command.Command):
    """Set security group properties"""

    def get_parser(self, prog_name):
        parser = super(SetSecurityGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Security group to modify (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<new-name>',
            help='New security group name',
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="New security group description",
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        data = utils.find_resource(
            compute_client.security_groups,
            parsed_args.group,
        )

        if parsed_args.name:
            data.name = parsed_args.name
        if parsed_args.description:
            data.description = parsed_args.description

        compute_client.security_groups.update(
            data,
            data.name,
            data.description,
        )


class ShowSecurityGroup(command.ShowOne):
    """Display security group details"""

    def get_parser(self, prog_name):
        parser = super(ShowSecurityGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Security group to display (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        info = {}
        info.update(utils.find_resource(
            compute_client.security_groups,
            parsed_args.group,
        )._info)
        rules = []
        for r in info['rules']:
            formatted_rule = _xform_and_trim_security_group_rule(r)
            rules.append(utils.format_dict(formatted_rule))

        # Format rules into a list of strings
        info.update(
            {'rules': utils.format_list(rules, separator='\n')}
        )
        # Map 'tenant_id' column to 'project_id'
        info.update(
            {'project_id': info.pop('tenant_id')}
        )

        return zip(*sorted(six.iteritems(info)))
