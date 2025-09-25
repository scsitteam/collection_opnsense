def filter_compiler(filter_spec: dict) -> callable:
    match filter_spec:
        # Comparisons
        case {'value': key, **kw} if not kw:
            return lambda obj: bool(obj[key])
        case {'value': key, 'eq': value,  **kw} if not kw:
            return lambda obj: obj[key] == value
        case {'value': key, 'gt': value,  **kw} if not kw:
            return lambda obj: obj[key] > value
        case {'value': key, 'lt': value,  **kw} if not kw:
            return lambda obj: obj[key] < value
        case {'value': key, 'startswith': value,  **kw} if not kw:
            return lambda obj: obj[key].startswith(value)
        case {'value': key, 'endswith': value,  **kw} if not kw:
            return lambda obj: obj[key].endswith(value)
        # Combinations
        case {'not': filter_sub_spec, **kw} if not kw:
            return lambda obj: not filter_compiler(filter_sub_spec)(obj)
        case {'all': list(filter_sub_spec), **kw} if not kw:
            filters = [filter_compiler(f) for f in filter_sub_spec]
            return lambda obj: all(f(obj) for f in filters)
        case {'any': list(filter_sub_spec), **kw} if not kw:
            filters = [filter_compiler(f) for f in filter_sub_spec]
            return lambda obj: any(f(obj) for f in filters)