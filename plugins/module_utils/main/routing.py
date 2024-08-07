from ipaddress import ip_address

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.main import \
    validate_int_fields
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.base.api import \
    Session
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.base.cls import BaseModule


class Routing(BaseModule):
    FIELD_ID = 'name'
    CMDS = {
        'add': 'addGateway',
        'del': 'delGateway',
        'set': 'setGateway',
        'search': 'get',
        'toggle': 'toggleGateway',
    }
    API_KEY_PATH = 'gateways.gateway_item'
    API_MOD = 'routing'
    API_CONT = 'settings'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = ['name', 'interface', 'gateway', 'defaultgw', 'fargw', 'monitor_disable', 'monitor_noroute', 'monitor', 'force_down', 'priority', 'weight', 'latencylow', 'latencyhigh', 'losslow', 'losshigh', 'interval', 'time_period', 'loss_interval', 'data_length', 'description']
    FIELDS_ALL = ['enabled']
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_BOOL_INVERT = ['enabled']
    FIELDS_TRANSLATE = {
        'description': 'descr',
        'enabled': 'disabled',
    }
    FIELDS_TYPING = {
        'bool': ['enabled', 'defaultgw', 'fargw', 'monitor_disable', 'monitor_noroute', 'force_down'],
        'int': ['priority', 'weight', 'latencylow', 'latencyhigh', 'losslow', 'losshigh', 'interval', 'time_period', 'loss_interval', 'data_length'],
        'list': [],
        'select': [],
    }
    INT_VALIDATIONS = {
        'priority': {'min': 0, 'max': 255},
        'weight': {'min': 1, 'max': 5},
        'latencylow': {'min': 1, 'max': 9999},
        'latencyhigh': {'min': 1, 'max': 9999},
        'losslow': {'min': 1, 'max': 99},
        'losshigh': {'min': 1, 'max': 99},
        'interval': {'min': 1, 'max': 9999},
        'time_period': {'min': 1, 'max': 9999},
        'data_length': {'min': 0, 'max': 9999},
    }
    EXIST_ATTR = 'routing'
    ipprotocol = 'inet'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session)
        self.routing = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            validate_int_fields(module=self.m, data=self.p, field_minmax=self.INT_VALIDATIONS)
            try:
                ip_address(self.p['gateway'])
                # set ipprotocol based on gateway address type
                if self.p['gateway'].find(':') != -1:
                    self.p['ipprotocol'] = 'inet6'
                else:
                    self.p['ipprotocol'] = 'inet'

            except ValueError:
                self.m.fail_json(f"Value '{self.p['gateway']}' is not a valid gateway!")
            if self.p['monitor']:
                try:
                    ip_address(self.p['monitor'])
                except ValueError:
                    self.m.fail_json(f"Value '{self.p['monitor']}' is not a valid monitor address!")
            if not self.p['interface']:
                self.m.fail_json('You need to provide a value for the interface!')
            if not self.p['gateway']:
                self.m.fail_json('You need to provide a value for the gateway!')
        self._base_check()
