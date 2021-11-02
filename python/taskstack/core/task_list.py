from collections import OrderedDict
# import abc
import json
from .task import Task

class TaskList(object):
    
    # __metaclass__ = abc.ABCMeta

    def __init__(self):
        # self.__parameters = {}
        self.__tasks = []

    def get_parameters(self):
        params = []

        for task in self.__tasks:
            task_active = task.get_active()
            task_params = task.get_parameters()
            params.append({'name': type(task).__name__, 'active': task_active, 'parameters': task_params})

        return params

    def set_parameters(self, parameters):
        self.clear_tasks()
        
        for task_info in parameters:
            task_name = task_info.get('name')
            task_active = task_info.get('active', True)
            task_params = task_info.get('parameters')
            self.add_task(name=task_name, active=task_active, parameters=task_params)

    def get_tasks(self):
        return self.__tasks

    def add_task(self, task=None, name='', active=True, parameters={}):
        if not task:
            task_classes = Task.get_task_classes()
            task_class = task_classes.get(name)

            if not task_class:
                print('[TaskStackError] Task "{}" does not exist.'.format(name))
                return

            task = task_class()

        task.set_active(active)

        if not isinstance(parameters, dict):
            print('[TaskStackError] Parameters must be dictionary.'.format(name))
            return

        task.set_parameters(**parameters)
        self.__tasks.append(task)

    def remove_task(self, idx):
        del self.__tasks[idx]

    def moveup_task(self, idx):
        tasks = self.__tasks
        src_task = tasks[idx]
        tgt_task = tasks[idx -1]
        tasks[idx] = tgt_task
        tasks[idx -1] = src_task

    def movedown_task(self, idx):
        tasks = self.__tasks
        src_task = tasks[idx]
        tgt_task = tasks[idx +1]
        tasks[idx] = tgt_task
        tasks[idx +1] = src_task

    def clear_tasks(self):
        del self.__tasks[:]

    def execute(self):
        print('[TaskStack] {0} {1}.execute. {0}'.format('-'*20, type(self).__name__))
        for task in self.__tasks:
            task.execute_if_active()

class TaskListParameters(list):

    def __init__(self, *args, **kwargs):
        # self.__source_parameters
        # self.__parameters
        super(TaskListParameters, self).__init__(*args, **kwargs)

    def load(self, path):
        with open(path, 'r') as f:
            params = json.load(f)#, object_pairs_hook=OrderedDict)

        self.__init__(params)

    def dump(self, path):
        with open(path, 'w') as f:
            json.dump(self, f, indent=4)

    def loads(self, s):
        params = json.loads(s)#, object_pairs_hook=OrderedDict)
        self.__init__(params)

    def dumps(self):
        s = json.dumps(self, indent=4)
        return s