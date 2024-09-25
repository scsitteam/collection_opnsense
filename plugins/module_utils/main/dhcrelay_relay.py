from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ansibleguy.opnsense.plugins.module_utils.base.api import \
    Session
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.main import \
    is_unset
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.base.cls import  BaseModule


class DhcRelayRelay(BaseModule):
    FIELD_ID = 'interface'
    CMDS = {
        'add': 'addRelay',
        'del': 'delRelay',
        'set': 'setRelay',
        'search': 'get',
        'detail': 'getRelay'
    }
    API_KEY_PATH = 'dhcrelay.relays'
    API_KEY_PATH_REQ = 'relay'
    API_MOD = 'dhcrelay'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = ['enabled', 'destination', 'agent_info']
    FIELDS_ALL = [FIELD_ID]
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_VALUE_MAPPING = {}
    FIELDS_TYPING = {
        'select': ['interface'],
        'select_opt_list': ['destination'],
        'bool': ['enabled', 'agent_info']
    }
    EXIST_ATTR = 'relay'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session)
        self.relay = {}


    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['destination']):
                self.m.fail_json("You need to provide a 'destination' to create a dhcrelay_relay!")

        if self.p['state'] == 'present':
            template = self.s.get({
                    **self.call_cnf,
                    'command': self.CMDS['detail'],
            })

            if template['relay']['destination']:
                self.FIELDS_VALUE_MAPPING['destination'] = {
                    v['value']:k
                    for k,v in template['relay']['destination'].items()
                }

        self._base_check()
