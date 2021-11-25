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
            ('Attribute Name', 'tx'),
            ('Value', 10.0),
        ))
        
    def execute(self):
        super(SetAttributeTask, self).execute()
        parameters = self.get_parameters()
        attrName = parameters.get('Attribute Name')
        value = parameters.get('Value')
        nodes = pm.ls(sl=True)
        
        for node in nodes:
            node.attr(attrName).set(value)