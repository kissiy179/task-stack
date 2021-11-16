# encoding: UTF-8
from collections import OrderedDict
import maya.cmds as cmds
from taskstack.core.task import Task
from taskstack.core import TaskStackError, TaskStackWarning

class RaiseErrorTask(Task):
    '''
    エラーを発生させるテストタスク
    '''

    def get_default_parameters(self):
        return OrderedDict((
            ('Raise Error', True),
            ('Raise Warning', True),
        ))
       
    def execute(self):
        super(RaiseErrorTask, self).execute()
        parameters = self.get_parameters()
        raise_warning = parameters.get('Raise Warning')
        raise_error = parameters.get('Raise Error')

        if raise_warning:
            self.raise_warning('Warning')

        if raise_error:
            self.raise_error('Err')


