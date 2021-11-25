# -*- coding: utf-8 -*-
import re
from collections import OrderedDict
import maya.cmds as cmds
from taskstack.core.task import Task
DECIMAL_PATTERN = re.compile(r'^\d')

class CreateNodesTask(Task):
    '''
    指定したタイプのノードを指定数作成するタスク
    '''
    
    def get_default_parameters(self):
        return OrderedDict((
            ('Count', 1),
            ('Node Type', 'transform'),
            ('Node Name', '{Node Type}'),
        ))
        
    # def get_parameter_types(self):
    #     return OrderedDict((
    #         ('count', int),
    #         ('nodeType', str),
    #         ('key', str),
    #     ))
         
    def execute(self):
        super(CreateNodesTask, self).execute()
        parameters = self.get_parameters()
        count = parameters.get('Count')
        nodeType = parameters.get('Node Type')
        nodeName = parameters.get('Node Name')

        if DECIMAL_PATTERN.match(nodeName):
            nodeName = '_{}'.format(nodeName)
        
        for i in range(count):
            item = cmds.createNode(nodeType, name=nodeName)
            