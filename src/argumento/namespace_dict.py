class NamespaceDict(dict):
    def __init__(self, *args, **kwargs):
        super(NamespaceDict, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __getitem__(self, item):
        idx_dot = item.find('.')
        if idx_dot >= 0:
            curr_attr = item[:idx_dot]
            nested_attr = item[idx_dot + 1:]
            nested_map = self.get(curr_attr)
            return nested_map.get(nested_attr)
        else:
            return self.get(item)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = NamespaceDict(value)
        idx_dot = key.find('.')
        if idx_dot >= 0:
            attr = key[:idx_dot]
            nested_key = key[idx_dot+1:]
            nested_map = self.get(attr)
            if nested_map is None:
                nested_map = NamespaceDict()
            nested_map.__setitem__(nested_key, value)
            super(NamespaceDict, self).__setitem__(attr, nested_map)
            self.__dict__.update({attr: nested_map})
        else:
            super(NamespaceDict, self).__setitem__(key, value)
            self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(NamespaceDict, self).__delitem__(key)
        del self.__dict__[key]

