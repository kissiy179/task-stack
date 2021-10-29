# -*- coding: utf-8 -*-
from collections import OrderedDict
import maya.cmds as cmds
import taskstack.core.task as task

class CreateNodesTask(task.Task):
    '''
    指定したタイプのノードを指定数作成するタスク
    '''
    
    def get_default_parameters(self):
        return OrderedDict((
            ('count', 1),
            ('nodeType', 'transform'),
            ('key', 'test'),
        ))
        
    # def get_parameter_types(self):
    #     return OrderedDict((
    #         ('count', int),
    #         ('nodeType', str),
    #         ('key', str),
    #     ))
         
    def execute(self):
        parameters = self.get_parameters()
        count = parameters.get('count')
        nodeType = parameters.get('nodeType')
        key = parameters.get('key')
        
        for i in range(count):
            item = cmds.createNode(nodeType, name='node_{}'.format(key))