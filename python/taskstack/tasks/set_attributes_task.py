# -*- coding: utf-8 -*-
import re
from collections import OrderedDict
import maya.cmds as cmds
import pymel.core as pm
from taskstack.core.task import Task

class SetAttributeTask(Task):
    '''
    指定したノードタイプのオブジェクトにアトリビュートを設定するタスク
    '''
    
    def get_default_parameters(self):
        return OrderedDict((
            ('Node Type', 'transform'),
            ('Node Name', '*'),
            ('Attribute Name', 'tx'),
            ('Value', 10.0),
        ))
        
    def execute(self):
        super(SetAttributeTask, self).execute()
        parameters = self.get_parameters()
        nodeType = parameters.get('Node Type')
        nodeName = parameters.get('Node Name')
        attrName = parameters.get('Attribute Name')
        value = parameters.get('Value')

        if nodeType:
            nodes = pm.ls(nodeName, type=nodeType)

        else:
            nodes = pm.ls(nodeName)
        
        for node in nodes:
            node.attr(attrName).set(value)