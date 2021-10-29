import abc
from collections import OrderedDict

class Task(object):
    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self):
        self.__default_parameters = self.get_default_parameters()
        self.__parameters = self.get_default_parameters()
        
    @abc.abstractmethod
    def get_default_parameters(self):
        return OrderedDict()
        
    def get_parameter_types(self):
        parameter_types = OrderedDict()

        for name, value in self.__default_parameters.items():
            parameter_types[name] = type(value).__name__

        return parameter_types
    
    def get_parameters(self):
        return self.__parameters
        
    def set_parameters(self, **parameters):
        for key in self.__parameters:
            self.__parameters[key] = parameters.get(key, self.__parameters.get(key))

    def get_doc(self):
        return self.__doc__
        
    @abc.abstractmethod
    def execute(self):
        raise NotImplemented()

