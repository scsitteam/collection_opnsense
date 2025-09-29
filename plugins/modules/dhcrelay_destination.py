#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/dhcrelay.html

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.wrapper import \
        module_wrapper, is_multi_module_call, module_multi_wrapper
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.multi import \
        build_multi_mod_args
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_ONLY_MOD_ARG, RELOAD_MOD_ARG
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.dhcrelay_destination import \
        DhcRelayDestination

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/dhcrelay_destination.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/dhcrelay_destination.html'


def run_module():
    entry_args = dict(
        name=dict(
            type='str', required=True,
            description='A unique name for this relay destination.',
        ),
        server=dict(
            type='list', elements='str', required=False,
            description='A list of server IP addresses to relay DHCP requests to.'
        ),
        **STATE_ONLY_MOD_ARG,
    )
    entry_multi_args = build_multi_mod_args(
        mod_args=entry_args,
        aliases=['dhcrelay_destinations', 'destinations'],
        not_required=['name'],
    )

    module_args = dict(
        **entry_args,
        **entry_multi_args,
        **OPN_MOD_ARGS,
        **RELOAD_MOD_ARG,
    )

    result = dict(
        changed=False,
        diff={
            'before': {},
            'after': {},
        }
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[
            ('name', 'multi'), ('name', 'multi_purge'), ('name', 'multi_control.purge_all')
        ],
        required_one_of=[
            ('name', 'multi', 'multi_purge', 'multi_control.purge_all'),
        ],
    )

    if is_multi_module_call(module):
        module_multi_wrapper(
            module=module,
            result=result,
            obj=DhcRelayDestination,
            kind='dhcrelay_destination',
            entry_args=entry_multi_args,
        )

    else:
        module_wrapper(DhcRelayDestination(module=module, result=result))

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
