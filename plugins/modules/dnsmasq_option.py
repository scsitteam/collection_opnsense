#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/dnsmasq.html

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.wrapper import \
        module_wrapper, is_multi_module_call, module_multi_wrapper
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.multi import \
        build_multi_mod_args
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_ONLY_MOD_ARG
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.dnsmasq_option import Option

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/dnsmasq.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/dnsmasq.html'

class MultiCallbacks(MultiModuleCallbacks):
    @staticmethod
    def get_existing(meta_entry: Range) -> dict:
        existing = meta_entry.get_existing()
        return {
            'main': existing,
            **{
                key: getattr(meta_entry, key)
                for key in getattr(meta_entry, 'SEARCH_ADDITIONAL', {})
            },
        }

    @staticmethod
    def set_existing(entry: Range, cache: dict):
        entry.existing_entries = cache['main']
        for key in getattr(entry, 'SEARCH_ADDITIONAL', {}):
            setattr(entry, key, cache[key])
        entry.simplify_existing = lambda e: e

def run_module():
    entry_args = dict(
        description=dict(
            type='str', required=True, aliases=['desc'],
            description='DHCP option description.',
        ),
        type=dict(
            type='str', required=False, options=['set', 'match'], default='set',
            description='"Set" to send it to a client in a DHCP offer or '
                        '"Match" to dynamically tag clients that send it in the initial DHCP request.',
        ),
        option=dict(
            type='int', required=False,
            description='DHCPv4 option to offer to the client.',
        ),
        option6=dict(
            type='int', required=False,
            description='DHCPv6 option to offer to the client.',
        ),
        interface=dict(
            type='str', required=False, aliases=['int'],
            description='Interface this options is set for.',
        ),
        tag=dict(
            type='list', elements='str', required=False, default=[], aliases=['t'],
            description='DHCP option is only sent when all the tags do match.',
        ),
        set_tag=dict(
            type='str', required=False,
            description='Tag to set for matching requests.',
        ),
        value=dict(
            type='str', required=False,
            description='Value (or values) to send to the client. '
                        'When using "Match", leave empty to match on the option only.',
        ),
        force=dict(
            type='bool', required=False, default=False,
            description='Always send the option, also when the client does not ask for it.',
        ),
        **STATE_ONLY_MOD_ARG,
    )
    entry_multi_args = build_multi_mod_args(
        mod_args=entry_args,
        aliases=['dnsmasq_options', 'options'],
        not_required=['description'],
    )

    module_args = dict(
        **entry_args,
        **entry_multi_args,
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
            ('description', 'multi'), ('description', 'multi_purge'), ('description', 'multi_control.purge_all'),
        ],
        required_one_of=[
            ('description', 'multi', 'multi_purge', 'multi_control.purge_all'),
        ],
    )

    if is_multi_module_call(module):
        module_multi_wrapper(
            module=module,
            result=result,
            obj=Option,
            kind='dnsmasq_option',
            entry_args=entry_multi_args,
            callbacks=MultiCallbacks,
        )

    else:
        module_wrapper(Option(module=module, result=result))
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
