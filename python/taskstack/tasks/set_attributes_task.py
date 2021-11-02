# -*- coding: utf-8 -*-
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
            ('nodeType', 'transform'),
            ('attrName', 'tx'),
            ('value', 10.0),
        ))
        
    def execute(self):
        super(SetAttributeTask, self).execute()
        parameters = self.get_parameters()
        nodeType = parameters.get('nodeType')
        attrName = parameters.get('attrName')
        value = parameters.get('value')
        nodes = pm.ls(type=nodeType)
        
        for node in nodes:
            node.attr(attrName).set(value)