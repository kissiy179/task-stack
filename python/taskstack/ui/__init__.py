# -*- coding: utf-8 -*-
import os
import inspect
from functools import partial
import maya.cmds as cmds
from mayaqt import QtWidgets, QtCore
import qtawesome as qta
from pyside_components.widgets import path_edit
from maya_pyside_components.widgets import path_in_project_edit, node_name_edit

class CustomSpinBox(QtWidgets.QSpinBox):
    '''最大最小値を引き上げたSpinBox'''

    def __init__(self, *args, **kwargs):
        super(CustomSpinBox, self).__init__(*args, **kwargs)
        self.setMinimum(-100000)
        self.setMaximum(100000)

class CustomDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    '''最大最小値を引き上げたDoubleSpinBox'''

    def __init__(self, *args, **kwargs):
        super(CustomDoubleSpinBox, self).__init__(*args, **kwargs)
        self.setMinimum(-100000)
        self.setMaximum(100000)
        self.setDecimals(3)

class CustomLineEdit(QtWidgets.QLineEdit):

    def __init__(self, *args, **kwargs):
        super(CustomLineEdit, self).__init__(*args, **kwargs)
        self.setClearButtonEnabled(True)

class CustomTextEdit(QtWidgets.QTextEdit):

    def __init__(self, *args, **kwargs):
        super(CustomTextEdit, self).__init__(*args, **kwargs)
        self.setFixedHeight(80)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

# TaskWidgetで各パラメータに使用するウィジェットを洗濯するための情報を登録

# Mayaのすべてのノードタイプ用のウィジェット情報を登録
WIDGET_TABLE = {}

for node_type in cmds.allNodeTypes(includeAbstract=True):
    if node_type.endswith(' (abstract)'):
        node_type = node_type[:-11]

    non_exact_node_type = '{}+'.format(node_type)

    for node_type_ in [node_type, non_exact_node_type]:
        wgt_info = {
            'class': partial(node_name_edit.NodeNameEdit, node_type_), 
            'get_method': 'text', 
            'set_method': 'setText', 
            'update_signal': 'textChanged'
            }
        WIDGET_TABLE[node_type_] = wgt_info

# その他のウィジェット情報を登録
WIDGET_TABLE.update({
    'bool': {
        'class': QtWidgets.QCheckBox, 
        'get_method': 'isChecked', 
        'set_method': 'setChecked', 
        'update_signal': 'stateChanged',
        },
    'int': {
        'class': CustomSpinBox, 
        'get_method': 'value', 
        'set_method': 'setValue', 
        'update_signal': 'valueChanged',
        },
    'float': {
        'class': CustomDoubleSpinBox, 
        'get_method': 'value', 
        'set_method': 'setValue', 
        'update_signal': 'valueChanged'
        },
    'str': {
        'class': CustomLineEdit, 
        'get_method': 'text', 
        'set_method': 'setText', 
        'update_signal': 'textChanged'
        },
    'file': {
        'class': path_edit.FilePathEdit, 
        'get_method': 'text', 
        'set_method': 'setText', 
        'update_signal': 'textChanged'
        },
    'dir': {
        'class': path_edit.DirectoryPathEdit, 
        'get_method': 'text', 
        'set_method': 'setText', 
        'update_signal': 'textChanged'
        },
    'file_in_pj': {
        'class': path_in_project_edit.FilePathInProjectEdit, 
        'get_method': 'text', 
        'set_method': 'setText', 
        'update_signal': 'textChanged'
        },
    'dir_in_pj': {
        'class': path_in_project_edit.DirectoryPathInProjectEdit, 
        'get_method': 'text', 
        'set_method': 'setText', 
        'update_signal': 'textChanged'
        },
    'scn': {
        'class': path_in_project_edit.MayaSceneEdit, 
        'get_method': 'text', 
        'set_method': 'setText', 
        'update_signal': 'textChanged'
        },
    'multi_line_str': {
        'class': CustomTextEdit, 
        'get_method': 'toPlainText', 
        'set_method': 'setText', 
        'update_signal': 'textChanged'
        },
})

# 各種タスク用ウィジェットを読み込み
import task_list_menu; reload(task_list_menu)
import task_widget; reload(task_widget)
import task_list_widget; reload(task_list_widget)
