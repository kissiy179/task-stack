# encoding: UTF-8
from pprint import pprint
from mayaqt import maya_base_mixin, QtWidgets
# import qtawesome as qta
from . import WIDGET_TABLE
# task_icon = qta.icon('fa5s.cog', color='calendar')

class TaskWidget(maya_base_mixin, QtWidgets.QWidget):

    def __init__(self, task, *args, **kwargs):
        super(TaskWidget, self).__init__(*args, **kwargs)
        self.__widgets = {}
        self.__task = task
        self.__parameter_types = task.get_parameter_types()
        self.__main_layout = None
        self.init_ui()

    def init_ui(self, executable=True):
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
        self.group_box = QtWidgets.QGroupBox(type(task).__name__)
        self.group_box.setCheckable(True)
        self.group_box.setChecked(task.get_active())
        self.group_box.toggled.connect(self.toggle_active)
        self.__main_layout.addWidget(self.group_box)
        group_lo = QtWidgets.QVBoxLayout()
        self.group_box.setLayout(group_lo)

        # Description
        if doc:
            doc_lbl = QtWidgets.QLabel(doc)
            group_lo.addWidget(doc_lbl)

        # Parameters
        group_form_lo = QtWidgets.QFormLayout()
        group_lo.addLayout(group_form_lo)

        for param_name, param_type in param_types.items():
            widget_info = WIDGET_TABLE.get(param_type)

            if not widget_info:
                continue

            widget_class = widget_info.get('class')
            set_method = widget_info.get('set_method')
            widget = widget_class()
            value = params.get(param_name)
            getattr(widget, set_method)(value)
            group_form_lo.addRow(param_name, widget)
            self.__widgets[param_name] = widget

        # Execute button
        if executable:
            exec_btn = QtWidgets.QPushButton('Execute')
            exec_btn.clicked.connect(self.execute)
            self.__main_layout.addWidget(exec_btn)

        # Resize
        self.resize(400, 0)

    def clear_ui(self):
        if self.__main_layout:
            QtWidgets.QWidget().setLayout(self.__main_layout)

    def toggle_active(self):
        active = self.group_box.isChecked()
        self.__task.set_active(active)

    def execute(self):
        task = self.__task
        active = task.get_active()

        if not active:
            return 

        params = {}
        param_types = self.__parameter_types

        for param_name, widget in self.__widgets.items():
            param_type = param_types.get(param_name)
            widget_info = WIDGET_TABLE.get(param_type)
            get_method = widget_info.get('get_method')
            params[param_name] = getattr(widget, get_method)()

        task.set_parameters(**params)
        task.execute()