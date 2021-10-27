import abc

class Task(object):
    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self):
        self.__parameters = self.get_default_parameters()
        
    # @abc.abstractmethod
    def get_default_parameters(self):
        return {}
        
    def get_ui_types(self):
        return {}
    
    def get_parameters(self):
        return self.__parameters
        
    def set_parameters(self, **parameters):
        for key in self.__parameters:
            self.__parameters[key] = parameters.get(key, self.__parameters.get(key))
        
    @abc.abstractmethod
    def execute(self):
        raise NotImplemented()