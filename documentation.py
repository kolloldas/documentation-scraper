class Parameters(dict):
    def add(self, name, param_type, description):
        self[name] = {'type': param_type, 'description': description}

class Returns(dict):
    def set_returns(self, return_type, description):
        self['type'] = return_type
        self['description'] = description

class Documentation(object):
    """
    Encapsulates documentation for a single file
    """
    def __init__(self):
        self._name = None
        self._obj_type = None
        self._api_level = '1'
        self._summary = []
        self._parent_class = 'Object'
        self._interfaces = []
        self._nested_classes = []
        self._constants = []
        self._fields = []
        self._constructors = []
        self._public_methods = []
        self._protected_methods = []

    def set_name(self, name):
        self._name = name

    def set_api_level(self, api_level):
        self._api_level = api_level

    def append_summary(self, summary):
        self._summary.append(summary)
    
    def set_object_type(self, obj_type):
        self._obj_type = obj_type

    def set_parent_class(self, parent_class):
        self._parent_class = parent_class

    def set_interfaces(self, interfaces):
        self._interfaces = interfaces

    def add_nested_class(self, name, obj_type, description):
        self._nested_classes.append({'name': name, 
                                     'type': obj_type, 
                                     'description': description})

    def add_constant(self, name, const_type, const_value, description, api_level):
        self._constants.append({'name': name, 
                                'type': const_type, 
                                'value': const_value, 
                                'description': description,
                                'api_level': api_level})

    def add_field(self, name, field_type, description, api_level):
        self._fields.append({'name': name, 
                                'type': field_type, 
                                'description': description,
                                'api_level': api_level})

    def add_constructor(self, name, description, api_level):
        params = Parameters()
        returns = Returns() #dummy
        self._constructors.append({'name': name, 
                                    'params': params, 
                                    'description': description, 
                                    'api_level': api_level})
        return params, returns

    def add_public_method(self, name, description, api_level):
        params = Parameters()
        returns = Returns()
        self._public_methods.append({'name': name, 
                                    'params': params, 
                                    'returns': returns, 
                                    'description': description,
                                    'api_level': api_level})
        return params, returns

    def add_protected_method(self, name, description, api_level):
        params = Parameters()
        returns = Returns()
        self._protected_methods.append({'name': name, 
                                        'params': params, 
                                        'returns': returns, 
                                        'description': description,
                                        'api_level': api_level})
        return params, returns

    @property
    def name(self):
        return self._name

    @property
    def object_type(self):
        return self._obj_type

    @property
    def api_level(self):
        return self._api_level

    @property
    def summary(self):
        return self._summary if len(self._summary) > 0 else None

    @property
    def parent_class(self):
        return self._parent_class

    @property
    def interfaces(self):
        return self._interfaces if len(self._interfaces) > 0 else None

    @property
    def nested_classes(self):
        return self._nested_classes if len(self._nested_classes) > 0 else None

    @property
    def constants(self):
        return self._constants if len(self._constants) > 0 else None

    @property
    def fields(self):
        return self._fields if len(self._fields) > 0 else None

    @property
    def constructors(self):
        return self._constructors if len(self._constructors) > 0 else None

    @property
    def public_methods(self):
        return self._public_methods if len(self._public_methods) > 0 else None

    @property
    def protected_methods(self):
        return self._protected_methods if len(self._protected_methods) > 0 else None