import pytest

MOCK_OBJECT = {
    'yes': True, 'no': False,
    'name': 'bob',
    'number': 42,
}


@pytest.mark.parametrize('filter_spec, result', [
    ({'value': 'yes'}, True),
    ({'value': 'no'}, False),
])
def test_filter_compiler_bool(filter_spec, result):
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.filter import filter_compiler

    assert filter_compiler(filter_spec)(MOCK_OBJECT) == result


@pytest.mark.parametrize('filter_spec, result', [
    ({'value': 'name', 'eq': 'alice'}, False),
    ({'value': 'name', 'eq': 'bob'} , True),
    ({'value': 'number', 'eq': 42}, True),
    ({'value': 'number', 'eq': 23} , False),
])
def test_filter_compiler_eq(filter_spec, result):
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.filter import filter_compiler

    assert filter_compiler(filter_spec)(MOCK_OBJECT) == result


@pytest.mark.parametrize('filter_spec, result', [
    ({'value': 'name', 'gt': 'alice'}, True),
    ({'value': 'name', 'gt': 'bob'} , False),
    ({'value': 'name', 'gt': 'carol'} , False),
    ({'value': 'number', 'gt': 41}, True),
    ({'value': 'number', 'gt': 42} , False),
    ({'value': 'number', 'gt': 43} , False),
])
def test_filter_compiler_gt(filter_spec, result):
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.filter import filter_compiler

    assert filter_compiler(filter_spec)(MOCK_OBJECT) == result


@pytest.mark.parametrize('filter_spec, result', [
    ({'value': 'name', 'lt': 'alice'}, False),
    ({'value': 'name', 'lt': 'bob'} , False),
    ({'value': 'name', 'lt': 'carol'} , True),
    ({'value': 'number', 'lt': 41}, False),
    ({'value': 'number', 'lt': 42} , False),
    ({'value': 'number', 'lt': 43} , True),
])
def test_filter_compiler_lt(filter_spec, result):
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.filter import filter_compiler

    assert filter_compiler(filter_spec)(MOCK_OBJECT) == result


@pytest.mark.parametrize('filter_spec, result', [
    ({'value': 'name', 'startswith': 'alice'}, False),
    ({'value': 'name', 'startswith': 'bob'} , True),
    ({'value': 'name', 'startswith': 'bo'} , True),
])
def test_filter_compiler_startswith(filter_spec, result):
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.filter import filter_compiler

    assert filter_compiler(filter_spec)(MOCK_OBJECT) == result


@pytest.mark.parametrize('filter_spec, result', [
    ({'value': 'name', 'endswith': 'alice'}, False),
    ({'value': 'name', 'endswith': 'bob'} , True),
    ({'value': 'name', 'endswith': 'ob'} , True),
])
def test_filter_compiler_endswith(filter_spec, result):
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.filter import filter_compiler

    assert filter_compiler(filter_spec)(MOCK_OBJECT) == result


@pytest.mark.parametrize('filter_spec, result', [
    ({'not': {'value': 'yes'}}, False),
    ({'not': {'value': 'no'}}, True),
])
def test_filter_compiler_not(filter_spec, result):
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.filter import filter_compiler

    assert filter_compiler(filter_spec)(MOCK_OBJECT) == result


@pytest.mark.parametrize('filter_spec, result', [
    ({'all': [{'value': 'yes'}]}, True),
    ({'all': [{'value': 'no'}]}, False),
    ({'all': [{'value': 'yes'}, {'value': 'yes'}]}, True),
    ({'all': [{'value': 'yes'}, {'value': 'no'}]}, False),
    ({'all': [{'value': 'no'}, {'value': 'yes'}]}, False),
    ({'all': [{'value': 'no'}, {'value': 'no'}]}, False),
])
def test_filter_compiler_all(filter_spec, result):
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.filter import filter_compiler

    assert filter_compiler(filter_spec)(MOCK_OBJECT) == result


@pytest.mark.parametrize('filter_spec, result', [
    ({'any': [{'value': 'yes'}]}, True),
    ({'any': [{'value': 'no'}]}, False),
    ({'any': [{'value': 'yes'}, {'value': 'yes'}]}, True),
    ({'any': [{'value': 'yes'}, {'value': 'no'}]}, True),
    ({'any': [{'value': 'no'}, {'value': 'yes'}]}, True),
    ({'any': [{'value': 'no'}, {'value': 'no'}]}, False),
])
def test_filter_compiler_any(filter_spec, result):
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.filter import filter_compiler

    assert filter_compiler(filter_spec)(MOCK_OBJECT) == result


@pytest.mark.parametrize('filter_spec, error_path', [
    ({}, []),
    ({'value': 'unknown', 'unknown': 'unknown'}, []),
    ({'unknown': 'unknown'}, []),
    ({'not': {'unknown': 'unknown'}}, ['not']),
    ({'all': [{'value': 'yes'}, {'unknown': 'unknown'}]}, ['all']),
    ({'any': [{'value': 'yes'}, {'unknown': 'unknown'}]}, ['any']),
    ({'not': {'all': [{'any': [{'unknown': 'unknown'}]}]}}, ['not', 'all', 'any']),
])
def test_filter_compiler_compile_error(filter_spec, error_path):
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.filter import filter_compiler, FilterCompileError

    with pytest.raises(FilterCompileError) as excinfo:
        filter_compiler(filter_spec)
    assert excinfo.value.path == error_path

