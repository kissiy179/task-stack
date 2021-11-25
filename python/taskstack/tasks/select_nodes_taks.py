# -*- coding: utf-8 -*-
import re
from collections import OrderedDict
import maya.cmds as cmds
import forcesLib as flib; 
import taskstack.core.task as task
DECIMAL_PATTERN = re.compile(r'^\d')

class SelectNodesTask(task.Task):
    '''
    指定したタイプ、名前のノードを選択するタスク
    Use RegExをTrueにすることでNameに正規表現を使用可能
    '''
    
    def get_default_parameters(self):
        return OrderedDict((
            ('Node Type', 'transform'),
            ('Name', 'node'),
            ('Use RegEx', False),
        ))
        
    def execute(self):
        super(SelectNodesTask, self).execute()
        parameters = self.get_parameters()
        node_type = parameters.get('Node Type')
        name = parameters.get('Name')
        use_regex = parameters.get('Use RegEx')

        # 正規表現パターンを生成
        regex_name = name if use_regex else '^{}$'.format(name)
        p = re.compile(regex_name)

        # 指定ノードタイプのノードをリストアップ/正規表現でフィルタリング
        item_names = cmds.ls(type=node_type)
        item_names = [item_name for item_name in item_names if p.match(item_name)]

        # 選択
        # if item_names:
        cmds.select(item_names)