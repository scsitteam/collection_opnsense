from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.main import \
    get_matching
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.defaults.rule import \
     RULE_DEFAULTS


def validate_values(error_func, module: AnsibleModule, cnf: dict) -> None:
    error = "Value '%s' is invalid for the field '%s'!"

    # can't validate as aliases are supported
    # for field in ['source_net', 'destination_net']:
    #     if cnf[field] not in [None, '', 'any']:
    #         try:
    #             ip_network(cnf[field])
    #
    #         except ValueError:
    #             try:
    #                 ip_address(cnf[field])
    #
    #             except ValueError:
    #                 error_func(error % (cnf[field], field))

    if cnf['protocol'] in ['TCP/UDP']:
        error_func(error % (cnf['protocol'], 'protocol'))

    # some recommendations - maybe the user overlooked something
    if 'action' in cnf and cnf['action'] == 'pass' and cnf['protocol'] in ['TCP', 'UDP']:
        if cnf['source_net'] == 'any' and cnf['destination_net'] == 'any':
            module.warn(
                "Configuring allow-rules with 'any' source and "
                "'any' destination is bad practice!"
            )

        elif cnf['destination_net'] == 'any' and cnf['destination_port'] == 'any':
            module.warn(
                "Configuring allow-rules to 'any' destination "
                "using 'all' ports is bad practice!"
            )


def check_purge_configured(module: AnsibleModule, existing_rule: dict) -> bool:
    configured_rules = []

    for rule_key, rule_config in module.params['rules'].items():
        if rule_config is None:
            rule_config = {}

        rule_config = {
            **RULE_DEFAULTS,
            **rule_config,
        }

        rule_config[module.params['key_field']] = rule_key
        configured_rules.append(rule_config)

    return get_matching(
        module=module, existing_items=configured_rules,
        compare_item=existing_rule, match_fields=module.params['match_fields'],
    ) is None
