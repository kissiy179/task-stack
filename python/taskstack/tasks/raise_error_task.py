# encoding: UTF-8
from collections import OrderedDict
import maya.cmds as cmds
from taskstack.core.task import Task

class RaiseErrorTask(Task):
    '''
    エラーを発生させるテストタスク
    '''

    def get_default_parameters(self):
        return OrderedDict((
            ('Raise Error', True),
        ))
       
    def execute(self):
        super(RaiseErrorTask, self).execute()
        parameters = self.get_parameters()
        raise_error = parameters.get('Raise Error')

        if raise_error:
            raise