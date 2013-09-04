class AUser(object):
    """A simple object to provide an interface into whatever your system User object is.
    It allows us to use property names within the Odummo framework without having
    to know what your User object uses."""
    
    def __init__(self, request_object):
        super(AUser, self).__init__()
        
        if type(request_object) == dict:
            return self.__from_dict(request_object)
        
        user_object = config['get_user_func'](request_object)
        self.id   = getattr(user_object, config['user.id_property'])
        self.name = getattr(user_object, config['user.name_property'])
    
    def __from_dict(self, dict_oject):
        self.id   = dict_oject['id']
        self.name = dict_oject['name']

config = {
    "layout": "../templates/default_layout.pt",
    "DBSession": None,
    "User": None,
    "use_achievements": False,
    
    "get_user_func": lambda r: KeyError("No function exists to get the user"),
    "get_user": AUser,
}

# This is a copy of how I'm setting up my Odummo configuration
#     from .games import odummo
#     config.include(odummo, route_prefix="odummo")
#     odummo.config.config['layout'] = '../../../templates/layouts/viewer.pt'
#     odummo.config.config['DBSession'] = DBSession
#     odummo.config.config['User'] = models.User
    
#     odummo.config.config['get_user_func']      = lambda r: r.user
#     odummo.config.config['user.id_property']   = "id"
#     odummo.config.config['user.name_property'] = "name"
