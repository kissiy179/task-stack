# -*- coding: utf-8 -*-
from mayaqt import QtWidgets, QtCore
import qtawesome as qta
import maya.cmds as cmds

dir_icon = qta.icon('fa5s.folder', color='lightgray')

class FilePathEdit(QtWidgets.QWidget):
    '''
    ファイルパス用ウィジェット
    '''

    textChanged = QtCore.Signal()
    
    def __init__(self, *args, **kwargs):
        super(FilePathEdit, self).__init__(*args, **kwargs)
        hlo = QtWidgets.QHBoxLayout()
        hlo.setContentsMargins(0,0,0,0)
        hlo.setSpacing(0)
        self.setLayout(hlo)

        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.textChanged.connect(self.textChanged)
        hlo.addWidget(self.line_edit)

        self.dialog_btn = QtWidgets.QPushButton()
        self.dialog_btn.setIcon(dir_icon)
        self.dialog_btn.clicked.connect(self.open_dialog)
        hlo.addWidget(self.dialog_btn)

    def open_dialog(self):
        file_obj = QtWidgets.QFileDialog.getOpenFileName()
        file_path = file_obj[0]

        if file_path:
            self.setText(file_path)

    def text(self):
        return self.line_edit.text()

    def setText(self, text):
        self.line_edit.setText(text)

class DirectoryPathEdit(FilePathEdit):
    '''
    ディレクトリパス用ウィジェット
    '''

    def open_dialog(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self)

        if dir_path:
            self.setText(dir_path)

class MayaSceneEdit(FilePathEdit):
    '''
    Mayaシーンパス用ウィジェット
    .ma, .mb, .fbxが有効
    '''

    def open_dialog(self):
        pj_path = cmds.workspace(query=True, rootDirectory=True)
        file_obj = QtWidgets.QFileDialog.getOpenFileName(dir=pj_path, filter='Maya scene files (*.ma *.mb);;FBX files (*.fbx)')
        file_path = file_obj[0]

        if file_path:
            file_path = file_path.replace(pj_path, '{}/'.format(pj_path)) # 相対パスに変換
            self.setText(file_path)

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
    'scn': {'class': MayaSceneEdit, 'get_method': 'text', 'set_method': 'setText', 'update_signal': 'textChanged'},
    'multi_line_str': {'class': CustomTextEdit, 'get_method': 'toPlainText', 'set_method': 'setText', 'update_signal': 'textChanged'},
}

import task_list_menu; reload(task_list_menu)
import task_widget; reload(task_widget)
import task_list_widget; reload(task_list_widget)