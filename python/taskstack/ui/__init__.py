# -*- coding: utf-8 -*-
import os
import inspect
from mayaqt import QtWidgets, QtCore
import qtawesome as qta
import maya.cmds as cmds
from .. import util

dir_icon = qta.icon('fa5s.folder', color='lightgray')

def getOpenFileName(parent, dir='', filter=''):
    '''
    QtWidgets.QFileDialog.getOpenFileName が inspect.argspec に通らないので関数でラップ
    '''
    file_obj = QtWidgets.QFileDialog.getOpenFileName(parent, dir=dir, filter=filter)

    if file_obj:
        return file_obj[0]

    return ''

def getExistingDirectory(parent, dir=''):
    '''
    QtWidgets.QFileDialog.getExistingDirectory が inspect.argspec に通らないので関数でラップ
    '''
    dir = QtWidgets.QFileDialog.getExistingDirectory(parent, dir=dir)
    return dir

class FilePathEdit(QtWidgets.QWidget):
    '''
    ファイルパス用ウィジェット
    '''

    filter = 'All files (*)'
    open_method = getOpenFileName
    textChanged = QtCore.Signal()
    
    def __init__(self, *args, **kwargs):
        super(FilePathEdit, self).__init__(*args, **kwargs)
        hlo = QtWidgets.QHBoxLayout()
        hlo.setContentsMargins(0,0,0,0)
        hlo.setSpacing(0)
        self.setLayout(hlo)

        # LineEdit
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.textChanged.connect(self.textChanged)
        hlo.addWidget(self.line_edit)

        # Dialog Button
        self.dialog_btn = QtWidgets.QPushButton()
        self.dialog_btn.setIcon(dir_icon)
        self.dialog_btn.clicked.connect(self.open_dialog)
        hlo.addWidget(self.dialog_btn)

    def open_dialog(self):
        crr_path = self.text()
        crr_dir = os.path.dirname(crr_path) if os.path.isfile(crr_path) else crr_path
        kwargs = {
                'dir': crr_dir,
                'filter': self.filter,
                }
        argspec = inspect.getargspec(self.open_method)
        kwargs = {key: value for key, value in kwargs.items() if key in argspec.args}
        result = self.open_method(**kwargs)

        if result:
            self.setText(result)

        return result

    def text(self):
        return self.line_edit.text()

    def setText(self, text):
        self.line_edit.setText(text)

class DirectoryPathEdit(FilePathEdit):
    '''
    ディレクトリパス用ウィジェット
    '''
    open_method = getExistingDirectory

class FilePathInMayaProjectEdit(FilePathEdit):
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
    open_method = getExistingDirectory

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
    'file': {'class': FilePathEdit, 'get_method': 'text', 'set_method': 'setText', 'update_signal': 'textChanged'},
    'dir': {'class': DirectoryPathEdit, 'get_method': 'text', 'set_method': 'setText', 'update_signal': 'textChanged'},
    'file_in_pj': {'class': FilePathInMayaProjectEdit, 'get_method': 'text', 'set_method': 'setText', 'update_signal': 'textChanged'},
    'dir_in_pj': {'class': DirectoryPathInMayaProjectEdit, 'get_method': 'text', 'set_method': 'setText', 'update_signal': 'textChanged'},
    'scn': {'class': MayaSceneEdit, 'get_method': 'text', 'set_method': 'setText', 'update_signal': 'textChanged'},
    'multi_line_str': {'class': CustomTextEdit, 'get_method': 'toPlainText', 'set_method': 'setText', 'update_signal': 'textChanged'},
}

import task_list_menu; reload(task_list_menu)
import task_widget; reload(task_widget)
import task_list_widget; reload(task_list_widget)