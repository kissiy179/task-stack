# encoding: UTF-8
import re
from pprint import pprint
from functools import partial
import traceback
from mayaqt import maya_base_mixin, maya_dockable_mixin, QtCore, QtWidgets
import qtawesome as qta
from pyside_components.util.color import color_to_hextriplet
from . import WIDGET_TABLE

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
        color = self.__task.get_color()
        color = [int(num * 1.3) for num in color]
        self.__exec_icon = qta.icon('fa5s.play', color=color_to_hextriplet(color))
        self.setWindowTitle(type(self.__task).__name__)
        self.init_ui()
        self.resize(300, 0)

    def log_parameters(self):
        print(self.__task.get_active(), self.__task.get_parameters(consider_keywords=False))

    def init_ui(self, executable=True, show_parameters=True, label_prefix=''):
        # uiクリア
        self.clear_ui()

        # Taskオブジェクトから情報取得
        task = self.__task
        doc = task.get_doc()
        param_types = self.__parameter_types
        params = task.get_parameters(consider_keywords=False)
        # print(params)

        # Main layout
        self.__main_layout = QtWidgets.QVBoxLayout()
        # self.__main_layout.setSpacing(3)
        self.__main_layout.setContentsMargins(0,4,6,6)
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
        self.__main_layout.addWidget(self.group_box)
        self.group_lo = QtWidgets.QVBoxLayout()
        self.group_lo.setSpacing(2)
        self.group_box.setLayout(self.group_lo)

        # Exec button
        doc_lo = QtWidgets.QHBoxLayout()
        doc_lo.setContentsMargins(0,0,0,0)

        if executable:
            exec_btn = QtWidgets.QPushButton()
            exec_btn.setIcon(self.__exec_icon)
            exec_btn.setIconSize(QtCore.QSize(14, 14))
            exec_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            exec_btn.clicked.connect(self.execute)
            doc_lo.addWidget(exec_btn)

        # Description
        if not show_parameters:
            doc = doc.split('\n')[0]
            
        self.group_lo.addLayout(doc_lo)
        self.doc_lbl = QtWidgets.QLabel(doc)
        self.doc_lbl.setStyleSheet('background-color: #585858;')# border: 0px solid gray; border-radius: 3px;')
        self.doc_lbl.setMargin(5)
        doc_lo.addWidget(self.doc_lbl)

        # Parameters
        self.init_parameters_ui(params, param_types, show_parameters)

        # Connect signals
        self.connect_signals()

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

    def init_parameters_ui(self, parametrs, parameter_types, show_parameters=True):
        if not parametrs:
            return

        wgt = QtWidgets.QWidget()
        lo = QtWidgets.QFormLayout()
        lo.setContentsMargins(0,0,0,0)
        wgt.setLayout(lo)
        lo.setVerticalSpacing(2)
        self.group_lo.addWidget(wgt)
        wgt.setVisible(show_parameters)

        for param_name, param_type in parameter_types.items():
            widget_info = WIDGET_TABLE.get(param_type)

            if not widget_info:
                continue

            widget_class = widget_info.get('class')
            widget = widget_class()
            set_method_name = widget_info.get('set_method', '')
            update_ui_method_name = widget_info.get('update_ui_method', '')
            value = parametrs.get(param_name)

            if hasattr(widget, set_method_name):
                getattr(widget, set_method_name)(value)

            if hasattr(widget, update_ui_method_name):
                getattr(widget, update_ui_method_name)()

            lo.addRow(param_name, widget)
            self.__widgets[param_name] = widget


    def clear_ui(self):
        if self.__main_layout:
            QtWidgets.QWidget().setLayout(self.__main_layout)

    def connect_signals(self):
        # 基本シグナル設定
        self.updated.connect(self.apply_parameters)
        self.group_box.toggled.connect(self.updated)
        task_emitter = self.__task.get_emitter(new=True)
        task_emitter.execute_start.connect(self.preprocess)
        task_emitter.executed.connect(self.postprocess)
        task_emitter.warning_raised.connect(self.set_warning_message)
        task_emitter.error_raised.connect(self.set_error_message)

        # パラメータウィジェット毎のシグナル設定
        param_types = self.__task.get_parameter_types()

        for param_name, param_type in param_types.items():
            widget = self.__widgets.get(param_name)
            widget_info = WIDGET_TABLE.get(param_type)

            if not widget_info:
                continue

            signal_name = widget_info.get('update_signal', '')
            signal = getattr(widget, signal_name)

            if hasattr(widget, signal_name):
                signal.connect(self.updated)

        # get_signal_connection_infosから取得できる情報からシグナル設定
        signal_connection_infos = self.__task.get_signal_connection_infos()
        
        for signal_param_name, slot_param_infos in signal_connection_infos.items():
            signal_widget = self.__widgets.get(signal_param_name)
            signal_param_type = param_types.get(signal_param_name)
            signal_widget_info = WIDGET_TABLE.get(signal_param_type)
            signal_name = signal_widget_info.get('update_signal', '')
            signal = getattr(signal_widget, signal_name)

            for slot_param_name, slot_name in slot_param_infos.items():
                signal_param_type = param_types.get(slot_param_name)
                slot_widget = self.__widgets.get(slot_param_name)

                if not hasattr(slot_widget, slot_name):
                    continue

                slot = getattr(slot_widget, slot_name)
                signal.connect(slot)
                # print(signal_widget, signal_name, slot)

    def apply_parameters(self):
        task = self.__task
        params = {}
        param_types = self.__parameter_types
        active = self.group_box.isChecked()
        task.set_active(active)

        for param_name, widget in self.__widgets.items():
            param_type = param_types.get(param_name)
            widget_info = WIDGET_TABLE.get(param_type)
            get_method = widget_info.get('get_method')

            if not get_method or not hasattr(widget, get_method):
                continue

            value = getattr(widget, get_method)()
            params[param_name] = value

        task.set_parameters(**params)

    def set_error_message(self, err=''):
        self.__error_message = err
        self.init_ui()
        
    def set_warning_message(self, err=''):
        self.__warning_message = err
        # self.init_ui()

    def preprocess(self):
        # エラーメッセージ初期化
        self.set_error_message()
        self.set_warning_message()

    def postprocess(self):
        self.init_ui()
        
    def execute(self):
        # activeの場合は実行
        self.__task.execute_if_active()
        return