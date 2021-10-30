import abc
from collections import OrderedDict

class Task(object):
    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self):
        self.__default_parameters = self.get_default_parameters()
        self.__parameters = self.get_default_parameters()
        self.__active = True
        
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

    @classmethod
    def get_doc(self, first_line_only=False):
        doc = self.__doc__

        if not doc:
            doc = 'No description...'

        lines = doc.split('\n')
        lines_ = []

        for line in lines:
            line = line.strip(' ')

            if not line:
                continue

            lines_.append(line)

        if first_line_only:
            return lines_[0]

        return '\n'.join(lines_)

    def get_active(self):
        return self.__active

    def set_active(self, active):
        self.__active = active
        
    @abc.abstractmethod
    def execute(self):
        raise NotImplemented()

    def execute_if_active(self):
        if not self.__active:
            return 

        self.execute()

