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
        build_multi_mod_args, MultiModuleCallbacks
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_ONLY_MOD_ARG, RELOAD_MOD_ARG
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.dhcrelay_relay import DhcRelayRelay

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/dhcrelay_relay.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/dhcrelay_relay.html'


class MultiCallbacks(MultiModuleCallbacks):
    @staticmethod
    def get_existing(meta_entry: DhcRelayRelay) -> dict:
        existing = meta_entry.get_existing()
        return {
            'main': existing,
            'destinations': meta_entry.existing_destinations,
        }

    @staticmethod
    def set_existing(entry: DhcRelayRelay, cache: dict):
        entry.existing_entries = cache['main']
        entry.existing_destinations = cache['destinations']

def run_module():
    entry_args = dict(
        enabled=dict(
            type='bool', default=False,
            description='Enable or disable this relay.',
        ),
        interface=dict(
            type='str', required=True, aliases=['i', 'int'],
            description='The interface to relay DHCP requests from. '
        ),
        destination=dict(
            type='str', required=False, aliases=['dest'],
            description='The uuid of the destination server group to relay DHCP requests to.'
        ),
        agent_info=dict(
            type='bool', default=False,
            description='Add the relay agent information option.',
        ),
        **STATE_ONLY_MOD_ARG,
    )
    entry_multi_args = build_multi_mod_args(
        mod_args=entry_args,
        aliases=['dhcrelay_relays', 'relays'],
        not_required=['interface'],
    )

    module_args = dict(
        **entry_args,
        **entry_multi_args,
        **RELOAD_MOD_ARG,
        **OPN_MOD_ARGS,
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
            ('interface', 'multi'), ('interface', 'multi_purge'), ('interface', 'multi_control.purge_all')
        ],
        required_one_of=[
            ('interface', 'multi', 'multi_purge', 'multi_control.purge_all'),
        ],
    )

    if is_multi_module_call(module):
        module_multi_wrapper(
            module=module,
            result=result,
            obj=DhcRelayRelay,
            kind='dhcrelay_relay',
            entry_args=entry_multi_args,
            callbacks=MultiCallbacks,
        )

    else:
        module_wrapper(DhcRelayRelay(module=module, result=result))

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
