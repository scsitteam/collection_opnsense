from typing import Callable
from ipaddress import ip_address, ip_network, IPv4Address, IPv6Address, IPv6Network, AddressValueError, \
    NetmaskValueError
from re import match as regex_match

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.base.handler import \
    exit_bug, exit_cnf
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.validate import \
    is_valid_domain


def diff_remove_empty(diff: dict) -> dict:
    d = diff.copy()
    for k in diff:
        if len(diff[k]) == 0:
            d.pop(k)

    return d


def ensure_list(data: (int, str, list, None)) -> list:
    # if user supplied a string instead of a list => convert it to match our expectations
    if isinstance(data, list):
        return data

    if data is None:
        return []

    return [data]


def is_ip(host: str, ignore_empty: bool = False, strip_enclosure: bool = True) -> bool:
    if ignore_empty and is_unset(host):
        return True

    if strip_enclosure and host.startswith('['):
        host = host[1:-1]

    try:
        ip_address(host)
        return True

    except ValueError:
        return False


def is_ip4(host: str, ignore_empty: bool = False) -> bool:
    if ignore_empty and is_unset(host):
        return True

    try:
        IPv4Address(host)
        return True

    except (AddressValueError, NetmaskValueError):
        return False


def is_ip6(host: str, ignore_empty: bool = False, strip_enclosure: bool = True) -> bool:
    if ignore_empty and is_unset(host):
        return True

    if strip_enclosure and host.startswith('['):
        host = host[1:-1]

    try:
        IPv6Address(host)
        return True

    except (AddressValueError, NetmaskValueError):
        return False


def is_ip_or_network(entry: str, strict: bool = False) -> bool:
    valid = is_ip(entry)

    if not valid:
        try:
            ip_network(entry, strict=strict)
            valid = True

        except ValueError:
            valid = False

    return valid


def is_ip6_network(entry: str, strict: bool = False) -> bool:
    try:
        valid = isinstance(ip_network(entry, strict=strict), IPv6Network)

    except ValueError:
        valid = False

    return valid


def valid_hostname(name: str) -> bool:
    _valid_domain = is_valid_domain(name)
    # see: https://en.wikipedia.org/wiki/Hostname#Restrictions_on_valid_host_names
    expr_hostname = r'^[a-zA-Z0-9-\.]{1,253}$'
    _valid_hostname = regex_match(expr_hostname, name) is not None
    return all([_valid_domain, _valid_hostname])


def get_matching(
        module: AnsibleModule, existing_items: (dict, list), compare_item: dict,
        match_fields: list, simplify_func: Callable = None,
) -> (dict, None):
    matching = None

    if len(existing_items) > 0:
        if isinstance(existing_items, dict):
            _existing_items_list = []
            for uuid, existing in existing_items.items():
                existing['uuid'] = uuid
                _existing_items_list.append(existing)

            existing_items = _existing_items_list

        for existing in existing_items:
            _matching = []

            if simplify_func is not None:
                existing = simplify_func(existing)

            try:
                for field in match_fields:
                    _matching.append(str(existing[field]) == str(compare_item[field]))

                    if module.params['debug']:
                        if existing[field] != compare_item[field]:
                            module.warn(
                                f"NOT MATCHING: "
                                f"'{existing[field]}' != '{compare_item[field]}'"
                            )

            except KeyError as error:
                exit_bug(
                    "Failed to match existing entry with provided one: "
                    f"{existing} <=> {sanitize_module_args(compare_item)}; "
                    f"Error while comparing: {error}"
                )

            if all(_matching):
                matching = existing
                break

    return matching


def get_multiple_matching(
        module: AnsibleModule, existing_items: (dict, list), compare_item: dict,
        match_fields: list, simplify_func: Callable = None,
) -> list:
    matching = []

    if len(existing_items) > 0:
        if isinstance(existing_items, dict):
            _existing_items_list = []
            for uuid, existing in existing_items.items():
                existing['uuid'] = uuid
                _existing_items_list.append(existing)

            existing_items = _existing_items_list

        for existing in existing_items:
            _simple = get_matching(
                module=module,
                existing_items=[existing],
                compare_item=compare_item,
                match_fields=match_fields,
                simplify_func=simplify_func,
            )
            if _simple is not None:
                matching.append(_simple)

    return matching


def validate_port(module: AnsibleModule, port: (int, str), error_func: Callable = None) -> bool:
    if error_func is None:
        error_func = module.fail_json

    if port == 'any' or is_unset(port):
        return True

    try:
        if int(port) < 1 or int(port) > 65535:
            error_func(f"Value '{port}' is an invalid port!")
            return False

    except (ValueError, TypeError):
        error_func(f"Value '{port}' is an invalid port!")
        return False

    return True


def validate_int_fields(
        module: AnsibleModule, data: dict, field_minmax: dict,
        error_func: Callable = None
):
    if error_func is None:
        error_func = module.fail_json

    for field, valid in field_minmax.items():
        try:
            if ('min' in valid and int(data[field]) < valid['min']) or \
               ('max' in valid and int(data[field]) > valid['max']):
                error_func(
                    f"Value of field '{field}' is not valid - "
                    f"Must be between {valid['min']} and {valid['max']}!"
                )

        except (TypeError, ValueError):
            pass


def is_true(data: (str, int, bool)) -> bool:
    return data in [1, '1', True]


def get_selected(data: dict) -> (str, None):
    if isinstance(data, dict):
        for key, values in data.items():
            if is_true(values['selected']):
                return key

        return ''  # none selected

    # if function is re-applied
    return data


def get_selected_value(data: dict) -> (str, None):
    if isinstance(data, dict):
        for values in data.values():
            if is_true(values['selected']) and 'value' in values:
                return values['value']

        return ''  # none selected

    if isinstance(data, list):
        for values in data:
            if is_true(values['selected']) and 'value' in values:
                return values['value']

        return ''  # none selected

    # if function is re-applied
    return data


def get_selected_opt_list(data: (dict, list)) -> (str, None):
    if isinstance(data, dict):
        return get_selected(data)

    return get_selected_value(data)


def get_selected_opt_list_idx(data: list) -> int:
    idx = 0
    for values in data:
        if is_true(values['selected']):
            return idx

        idx += 1

    return 0

def get_selected_list(data: dict, remove_empty: bool = False) -> list:
    if isinstance(data, list):
        # if function is re-applied
        return data

    if isinstance(data, str):
        if data.strip() == '':
            return []

        return data.split(',')

    selected = []
    if len(data) > 0:
        try:
            for key, values in data.items():
                if remove_empty and key in [None, '', ' ']:
                    continue

                if is_true(values['selected']):
                    selected.append(key)

        except AttributeError:
            exit_bug(f"Got data entry that is not a dictionary => '{data}'")

    selected.sort()
    return selected


def get_key_by_value_from_selection(selection: dict, value: str) -> (str, None):
    if isinstance(selection, dict):
        for key, values in selection.items():
            if 'value' in values and values['value'] == value:
                return key

    return None


def get_key_by_value_end_from_selection(selection: dict, value: str) -> (str, None):
    if isinstance(selection, dict):
        for key, values in selection.items():
            if 'value' in values and values['value'].endswith(value):
                return key

    return None


def get_key_by_value_beg_from_selection(selection: dict, value: str) -> (str, None):
    if isinstance(selection, dict):
        for key, values in selection.items():
            if 'value' in values and values['value'].startswith(value):
                return key

    return None


def to_digit(data: bool) -> int:
    return 1 if data else 0


def get_simple_existing(
        entries: (dict, list), add_filter: Callable = None,
        simplify_func: Callable = None
) -> list:
    simple_entries = []

    if isinstance(entries, dict):
        _entries = []
        for uuid, entry in entries.items():
            if not isinstance(entry, dict):
                exit_bug(f"The provided entry is not a dictionary => '{entry}'")

            entry['uuid'] = uuid
            _entries.append(entry)

        entries = _entries

    for entry in entries:
        if simplify_func is not None and add_filter is not None:
            simple_entries.append(add_filter(simplify_func(entry)))

        elif simplify_func is not None:
            simple_entries.append(simplify_func(entry))

        else:
            simple_entries.append(entries)

    return simple_entries


def validate_str_fields(
        module: AnsibleModule, data: dict, field_regex: dict = None,
        field_minmax_length: dict = None, allow_empty: bool = False,
) -> None:
    if field_minmax_length is not None:
        for field, min_max_length in field_minmax_length.items():
            if not unset_check_error(params=data, field=field, fail=not allow_empty):
                continue

            if 'min' not in min_max_length or 'max' not in min_max_length:
                exit_bug("Values of 'STR_LEN_VALIDATIONS' must have a 'min' and 'max' attribute!")

            if min_max_length['min'] < len(data[field]) > min_max_length['max']:
                module.fail_json(
                    f"Value of field '{field}' is not valid - "
                    f"Invalid length must be between {min_max_length['min']} and {min_max_length['max']}!"
                )

    if field_regex is not None:
        for field, regex in field_regex.items():
            if not unset_check_error(params=data, field=field, fail=not allow_empty):
                continue

            if regex_match(regex, data[field]) is None:
                module.fail_json(
                    f"Value of field '{field}' is not valid - "
                    f"Must match regex '{regex}'!"
                )


def format_int(data: (int, str)) -> (int, str):
    if isinstance(data, int):
        return data

    if data.isnumeric():
        return int(data)

    return data


def sort_param_lists(params: dict) -> None:
    for k in params:
        if isinstance(params[k], list):
            params[k].sort()


# pylint: disable=R0914,R0915
def simplify_translate(
        existing: dict, translate: dict = None, typing: dict = None,
        bool_invert: list = None, ignore: list = None, value_map: dict = None,
) -> dict:
    # pylint: disable=R0912
    simple = {}
    if translate is None:
        translate = {}

    if typing is None:
        typing = {}

    if bool_invert is None:
        bool_invert = []

    if ignore is None:
        ignore = []

    if value_map is None:
        value_map = {}

    try:
        # translate api-fields to ansible-fields
        for k, v in translate.items():
            if v in existing:
                simple[k] = existing[v]

        translate_fields = translate.values()
        for k in existing:
            if k not in translate_fields and k not in ignore:
                simple[k] = existing[k]

        # correct value types to match (for diff-checks)
        for t, fields in typing.items():
            for f in fields:
                if t == 'bool':
                    simple[f] = is_true(simple[f])

                elif t == 'int':
                    simple[f] = format_int(simple[f])

                elif t == 'list':
                    simple[f] = get_selected_list(data=simple[f], remove_empty=True)

                elif t == 'select':
                    simple[f] = get_selected(simple[f])

                elif t == 'select_opt_list':
                    simple[f] = get_selected_opt_list(simple[f])

                elif t == 'select_opt_list_idx':
                    simple[f] = get_selected_opt_list_idx(simple[f])

        for f, vmap in value_map.items():
            try:
                for pretty_value, opn_value in vmap.items():
                    if simple[f] == opn_value:
                        simple[f] = pretty_value
                        break

            except KeyError:
                pass

        for k, v in simple.items():
            if isinstance(v, str) and v.isnumeric():
                simple[k] = int(simple[k])

            elif isinstance(v, bool) and k in bool_invert:
                simple[k] = not simple[k]

    except KeyError as err:
        exit_bug(
            f"Failed to translate API entry to Ansible entry! Maybe the API changed lately? "
            f"Failed field: {err} | "
            f"API entry: '{existing}' '{simple}'"
        )

    return simple


def is_unset(value: (str, None, list, dict)) -> bool:
    if isinstance(value, (list, dict)):
        return len(value) == 0

    if isinstance(value, str):
        value = value.strip()

    return value in ['', None]


def unset_check_error(params: dict, field: str, fail: bool) -> bool:
    if is_unset(params[field]):
        if fail:
            exit_cnf(f"Field '{field}' must be set!")

        return False

    return True

def sanitize_module_args(args: dict) -> dict:
    args.pop('api_key', None)
    args.pop('api_secret', None)
    return args
