from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ansibleguy.opnsense.plugins.module_utils.base.api import \
    Session
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.main import \
    validate_int_fields, is_unset
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.base.cls import BaseModule


class Lagg(BaseModule):
    FIELD_ID = 'device'
    CMDS = {
        'add': 'addItem',
        'del': 'delItem',
        'set': 'setItem',
        'search': 'get',
    }
    API_KEY_PATH = 'lagg.lagg'
    API_MOD = 'interfaces'
    API_CONT = 'lagg_settings'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = ['members', 'primary_member', 'proto', 'lacp_fast_timeout', 'use_flowid', 'lagghash', 'lacp_strict', 'mtu', 'description']
    FIELDS_ALL = [FIELD_ID]
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TRANSLATE = {
        'device': 'laggif',
        'description': 'descr',
    }
    FIELDS_TYPING = {
        'bool': ['lacp_fast_timeout'],
        'list': ['members', 'lagghash'],
        'select': ['members', 'primary_member', 'proto', 'use_flowid', 'lagghash', 'lacp_strict'],
    }
    INT_VALIDATIONS = {
        'mtu': {'min': 576, 'max': 65535},
    }
    EXIST_ATTR = 'lagg'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session)
        self.lagg = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['members']):
                self.m.fail_json("You need to provide a list of 'members' to create a lagg!")
            if is_unset(self.p['lagghash']):
                self.m.fail_json("You need to provide a list of 'lagghash' to create a lagg!")

            validate_int_fields(module=self.m, data=self.p, field_minmax=self.INT_VALIDATIONS)

        self._base_check()

    def update(self) -> None:
        self.b.update(enable_switch=False)
