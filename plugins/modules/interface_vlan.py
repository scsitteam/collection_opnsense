#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/interfaces.html

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
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.interface_vlan import Vlan

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/interface.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/interface.html'


def run_module():
    entry_args = dict(
        device=dict(
            type='str', required=False, aliases=['vlanif'],
            description="Optional 'device' of the entry. Needs to start with 'vlan0'",
        ),
        interface=dict(
            type='str', required=False, aliases=['parent', 'port', 'int', 'if'],
            description='Existing VLAN capable interface - you must provide the network '
                        "port as shown in 'Interfaces - Assignments - Network port'"
        ),
        vlan=dict(
            type='int', required=False, aliases=['tag', 'id'],
            description='802.1Q VLAN tag (between 1 and 4094)'
        ),
        priority=dict(
            type='int', required=False, default=0, aliases=['prio', 'pcp'],
            description='802.1Q VLAN PCP (priority code point)'
        ),
        protocol=dict(
            type='str', required=False, options=['802.1q', '802.1ad'], aliases=['proto'],
            description='Enforce protocol selection. 802.1Q is the default for VLAN interfaces, '
                        'but 802.1ad is used when the parent is a VLAN',
        ),
        description=dict(type='str', required=True, aliases=['desc', 'name']),
        **STATE_ONLY_MOD_ARG,
    )
    entry_multi_args = build_multi_mod_args(
        mod_args=entry_args,
        aliases=['interface_vlans', 'vlans'],
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
            obj=Vlan,
            kind='interface_vlan',
            entry_args=entry_multi_args,
        )

    else:
        module_wrapper(Vlan(module=module, result=result))
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
