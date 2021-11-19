# encoding: UTF-8
import re
from pprint import pprint
from functools import partial
import traceback
from mayaqt import maya_base_mixin, maya_dockable_mixin, QtCore, QtWidgets
import qtawesome as qta
from . import WIDGET_TABLE

exec_icon = qta.icon('fa5s.play', color='lightgreen')
ERROR_PATTERN = re.compile(r'.*(?P<main_err>^[a-zA-Z]*Error: .*$)', re.MULTILINE | re.DOTALL)

class TaskWidget(maya_dockable_mixin, QtWidgets.QWidget):

    updated = QtCore.Signal()

    def __init__(self, task, *args, **kwargs):
        super(TaskWidget, self).__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setStyleSheet('QPushButton {background-color: transparent; border-style: solid; border-width:0px;}')
        self.__widgets = {}
        self.__task = task
        self.__parameter_types = task.get_parameter_types()
        self.__error_message = ''
        self.__warning_message = ''
        self.__label_prefix = ''
        self.__main_layout = None
        self.setWindowTitle(type(self.__task).__name__)
        self.init_ui()
        self.resize(300, 0)
        self.updated.connect(self.apply_parameters)
        # self.updated.connect(self.log_parameters)
        self.__task.get_emitter().warning_raised.connect(self.set_warning_message)
        self.__task.get_emitter().error_raised.connect(self.set_error_message)

    def log_parameters(self):
        print(self.__task.get_active(), self.__task.get_parameters())

    def init_ui(self, executable=True, show_parameters=True, label_prefix=''):
        # uiクリア
        self.clear_ui()

        # Taskオブジェクトから情報取得
        task = self.__task
        doc = task.get_doc()
        param_types = self.__parameter_types
        params = task.get_parameters()

        # Main layout
        self.__main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.__main_layout)

        # Group box
        if label_prefix:
            self.__label_prefix = label_prefix

        label = type(task).__name__
        label = '{}{}'.format(self.__label_prefix, label) if label else label
        self.group_box = QtWidgets.QGroupBox(label)
        self.group_box.setCheckable(True)
        self.group_box.setChecked(task.get_active())
        # self.group_box.setStyle(QtWidgets.QStyleFactory.create("plastique"))
        self.group_box.toggled.connect(self.updated)
        self.__main_layout.addWidget(self.group_box)
        self.group_lo = QtWidgets.QVBoxLayout()
        self.group_lo.setSpacing(2)
        self.group_box.setLayout(self.group_lo)

        # Exec button
        doc_lo = QtWidgets.QHBoxLayout()
        doc_lo.setContentsMargins(0,0,0,0)

        if executable:
            exec_btn = QtWidgets.QPushButton()
            exec_btn.setIcon(exec_icon)
            exec_btn.setIconSize(QtCore.QSize(14, 14))
            exec_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            exec_btn.clicked.connect(self.execute)
            doc_lo.addWidget(exec_btn)

        # Description
        self.group_lo.addLayout(doc_lo)
        self.doc_lbl = QtWidgets.QLabel(doc)
        self.doc_lbl.setStyleSheet('background-color: #555')
        self.doc_lbl.setMargin(5)
        doc_lo.addWidget(self.doc_lbl)

        # Parameters
        if show_parameters:
            self.init_parameters_ui(params, param_types)

        # Error message
        if self.__error_message:
            self.err_lbl = QtWidgets.QLabel(self.__error_message)
            self.err_lbl.setStyleSheet('color: white; background-color: indianred')
            self.err_lbl.setMargin(5)
            self.err_lbl.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            self.group_lo.addWidget(self.err_lbl)

        # Warning message
        if self.__warning_message:
            self.warn_lbl = QtWidgets.QLabel(self.__warning_message)
            self.warn_lbl.setStyleSheet('color: white; background-color: peru')
            self.warn_lbl.setMargin(5)
            self.warn_lbl.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            self.group_lo.addWidget(self.warn_lbl)

    def init_parameters_ui(self, parametrs, parameter_types):
        lo = QtWidgets.QFormLayout()
        lo.setVerticalSpacing(2)
        self.group_lo.addLayout(lo)

        for param_name, param_type in parameter_types.items():
            widget_info = WIDGET_TABLE.get(param_type)

            if not widget_info:
                continue

            widget_class = widget_info.get('class')
            set_method = widget_info.get('set_method')
            update_signal = widget_info.get('update_signal')
            widget = widget_class()
            value = parametrs.get(param_name)

            try:
                getattr(widget, set_method)(value)
                getattr(widget, update_signal).connect(self.updated)

            except:
                pass

            lo.addRow(param_name, widget)
            self.__widgets[param_name] = widget

    def clear_ui(self):
        if self.__main_layout:
            QtWidgets.QWidget().setLayout(self.__main_layout)

    def apply_parameters(self):
        task = self.__task
        params = {}
        param_types = self.__parameter_types
        active = self.group_box.isChecked()
        self.__task.set_active(active)

        for param_name, widget in self.__widgets.items():
            param_type = param_types.get(param_name)
            widget_info = WIDGET_TABLE.get(param_type)
            get_method = widget_info.get('get_method')
            params[param_name] = getattr(widget, get_method)()

        task.set_parameters(**params)

    def set_error_message(self, err=''):
        self.__error_message = err
        self.init_ui()
        
    def set_warning_message(self, err=''):
        self.__warning_message = err
        self.init_ui()
        
    def execute(self):
        # パラメータ適用
        self.apply_parameters()

        # エラーメッセージ初期化
        self.set_error_message()
        self.set_warning_message()

        # activeの場合は実行
        self.__task.execute_if_active()
        return