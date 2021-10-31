# -*- coding: utf-8 -*-
import re
from collections import OrderedDict
import maya.cmds as cmds
import taskstack.core.task as task
DECIMAL_PATTERN = re.compile(r'^\d')

class CreateNodesTask(task.Task):
    '''
    指定したタイプのノードを指定数作成するタスク
    '''
    
    def get_default_parameters(self):
        return OrderedDict((
            ('count', 1),
            ('nodeType', 'transform'),
            ('name', 'node'),
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
        name = parameters.get('name')

        if DECIMAL_PATTERN.match(name):
            name = '_{}'.format(name)
        
        for i in range(count):
            item = cmds.createNode(nodeType, name=name)