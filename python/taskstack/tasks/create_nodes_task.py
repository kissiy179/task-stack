from collections import OrderedDict
import maya.cmds as cmds
import taskstack.core.task as task

class CreateNodesTask(task.Task):
    
    def get_default_parameters(self):
        return {
            'count': 1,
            'nodeType': 'transform',
            'key': 'test',
        }
        
    def get_ui_types(self):
        return OrderedDict(
            ('count', int),
            ('nodeType', str),
            ('key', str),
        )
         
    def execute(self):
        parameters = self.get_parameters()
        count = parameters.get('count')
        nodeType = parameters.get('nodeType')
        key = parameters.get('key')
        
        for i in range(count):
            item = cmds.createNode(nodeType, name='node_{}'.format(key))