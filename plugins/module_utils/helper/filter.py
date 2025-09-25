class FilterCompileError(Exception):
    def __init__(self, message):            
        super().__init__(message)
        self.path = []

    def push_path(self, path):
        self.path.insert(0, path)
        raise self

    def __str__(self):
        if self.path:
            return f"{super().__str__()} at {'/'.join(self.path)}"
        return super().__str__()
        

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
        case {'value': key, **kw}:
            raise FilterCompileError(f"Could not parse comparison. Expected at most one other param named: eq, gt, lt, startswith or endswith. Got '{str(kw)}'")
        # Combinations
        case {'not': filter_sub_spec, **kw} if not kw:
            try:
                filter = filter_compiler(filter_sub_spec)
                return lambda obj: not filter(obj)
            except FilterCompileError as err:
                err.push_path('not')
        case {'all': list(filter_sub_spec), **kw} if not kw:
            try:
                filters = [filter_compiler(f) for f in filter_sub_spec]
                return lambda obj: all(f(obj) for f in filters)
            except FilterCompileError as err:
                err.push_path('all')
        case {'any': list(filter_sub_spec), **kw} if not kw:
            try:
                filters = [filter_compiler(f) for f in filter_sub_spec]
                return lambda obj: any(f(obj) for f in filters)
            except FilterCompileError as err:
                err.push_path('any')
        case {**kw}:
            raise FilterCompileError(f"Could not parse filter fragment '{str(kw)}'")