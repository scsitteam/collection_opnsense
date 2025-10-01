#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

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
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.interface_gre import Gre

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/interface.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/interface.html'


def run_module():
    entry_args = dict(
        description=dict(
            type='str', required=True, aliases=['desc'],
            description='The unique description used to match the configured entries to the existing ones.',
        ),
        local=dict(
            type='str', required=False, aliases=['l', 'local_addr'],
            description='The local address or interface to use.',
        ),
        remote=dict(
            type='str', required=False, aliases=['r', 'remote_addr'],
            description='Peer address where encapsulated gre packets will be sent.',
        ),
        tunnel_local=dict(
            type='str', required=False, aliases=['tl', 'tunnel_local_addr'],
            description='Local gre tunnel endpoint.',
        ),
        tunnel_remote=dict(
            type='str', required=False, aliases=['tr', 'tunnel_remote_addr'],
            description='Remote gre tunnel endpoint.',
        ),
        tunnel_remote_net=dict(
            type='int', required=False, default=32,
            description="Netmask 'ipv4' or prefix 'ipv6' to use for this tunnel",
        ),
        **STATE_ONLY_MOD_ARG,
    )
    entry_multi_args = build_multi_mod_args(
        mod_args=entry_args,
        aliases=['interface_gres', 'gres'],
        not_required=['description'],
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
            ('description', 'multi'), ('description', 'multi_purge'), ('description', 'multi_control.purge_all')
        ],
        required_one_of=[
            ('description', 'multi', 'multi_purge', 'multi_control.purge_all'),
        ],
    )

    if is_multi_module_call(module):
        module_multi_wrapper(
            module=module,
            result=result,
            obj=Gre,
            kind='interface_gre',
            entry_args=entry_multi_args,
        )

    else:
        module_wrapper(Gre(module=module, result=result))
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
