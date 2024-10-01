from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ansibleguy.opnsense.plugins.module_utils.base.handler import \
    ModuleSoftError
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.base.api import \
    Session
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.main import \
    validate_int_fields, is_unset
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.base.cls import BaseModule


class Category(BaseModule):
    FIELD_ID = 'name'
    CMDS = {
        'add': 'addItem',
        'del': 'delItem',
        'set': 'setItem',
        'search': 'get',
    }
    API_KEY_PATH = 'category.categories.category'
    API_MOD = 'firewall'
    API_CONT = 'category'
    FIELDS_CHANGE = ['color', 'auto']
    FIELDS_ALL = [FIELD_ID]
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TYPING = {
        'bool': ['auto'],
    }
    EXIST_ATTR = 'category'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session)
        self.category = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if len(self.p['color']) != 6 or any(c not in '0123456789abcdef' for c in self.p['color']):
                self.m.fail_json('Color needs to be six hex digits!')
                
        self._base_check()

        if 'color' in self.category:
            self.category['color'] = f"{self.category['color']:06}"
