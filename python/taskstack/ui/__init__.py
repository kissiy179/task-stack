# -*- coding: utf-8 -*-
import os
import inspect
from mayaqt import QtWidgets, QtCore
import qtawesome as qta
import maya.cmds as cmds
from .. import util
from pyside_components.widgets import path_edit

class FilePathInMayaProjectEdit(path_edit.FilePathEdit):
    '''
    Mayaプロジェクト内の場合相対パスとして記憶するファイルパス用ウィジェット
    '''

    def text(self):
        text = self.line_edit.text()
        text = util.get_absolute_path_in_maya_project(text)
        return text

    def row_text(self):
        return super(FilePathInMayaProjectEdit, self).text()

    def setText(self, text):
        text = util.get_relatvie_path_in_maya_project(text)
        super(FilePathInMayaProjectEdit, self).setText(text)


class DirectoryPathInMayaProjectEdit(FilePathInMayaProjectEdit):
    '''
    Mayaプロジェクト内の場合相対パスとして記憶するファイルパス用ディレクトリパス用ウィジェット
    '''
    open_method = path_edit.getExistingDirectory

class MayaSceneEdit(FilePathInMayaProjectEdit):
    '''
    Mayaシーンパス用ウィジェット
    .ma, .mb, .fbxが有効
    '''
    filter = 'Maya scene files (*.ma *.mb);;FBX files (*.fbx)'

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

class CustomTextEdit(QtWidgets.QTextEdit):

    def __init__(self, *args, **kwargs):
        super(CustomTextEdit, self).__init__(*args, **kwargs)
        self.setFixedHeight(80)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))


WIDGET_TABLE = {
    'bool': {'class': QtWidgets.QCheckBox, 'get_method': 'isChecked', 'set_method': 'setChecked', 'update_signal': 'stateChanged'},
    'int': {'class': CustomSpinBox, 'get_method': 'value', 'set_method': 'setValue', 'update_signal': 'valueChanged'},
    'float': {'class': CustomDoubleSpinBox, 'get_method': 'value', 'set_method': 'setValue', 'update_signal': 'valueChanged'},
    'str': {'class': QtWidgets.QLineEdit, 'get_method': 'text', 'set_method': 'setText', 'update_signal': 'textChanged'},
    'file': {'class': path_edit.FilePathEdit, 'get_method': 'text', 'set_method': 'setText', 'update_signal': 'textChanged'},
    'dir': {'class': path_edit.DirectoryPathEdit, 'get_method': 'text', 'set_method': 'setText', 'update_signal': 'textChanged'},
    'file_in_pj': {'class': FilePathInMayaProjectEdit, 'get_method': 'text', 'set_method': 'setText', 'update_signal': 'textChanged'},
    'dir_in_pj': {'class': DirectoryPathInMayaProjectEdit, 'get_method': 'text', 'set_method': 'setText', 'update_signal': 'textChanged'},
    'scn': {'class': MayaSceneEdit, 'get_method': 'text', 'set_method': 'setText', 'update_signal': 'textChanged'},
    'multi_line_str': {'class': CustomTextEdit, 'get_method': 'toPlainText', 'set_method': 'setText', 'update_signal': 'textChanged'},
}

import task_list_menu; reload(task_list_menu)
import task_widget; reload(task_widget)
import task_list_widget; reload(task_list_widget)