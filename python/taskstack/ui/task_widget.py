from pprint import pprint
from mayaqt import *
from . import WIDGET_TABLE

class TaskWidget(maya_base_mixin, QtWidgets.QWidget):

    def __init__(self, task, *args, **kwargs):
        super(TaskWidget, self).__init__(*args, **kwargs)
        self.__widgets = {}
        self.__task = task
        self.__parameter_types = task.get_parameter_types()
        self.main_layout = None
        self.init_ui()

    def init_ui(self, executable=True):
        self.clear_ui()
        task = self.__task
        param_types = self.__parameter_types
        params = task.get_parameters()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.group = QtWidgets.QGroupBox(type(task).__name__)
        self.group.setCheckable(True)
        self.main_layout.addWidget(self.group)
        group_lo = QtWidgets.QFormLayout()
        self.group.setLayout(group_lo)

        for param_name, param_type in param_types.items():
            widget_info = WIDGET_TABLE.get(param_type)

            if not widget_info:
                continue

            widget_class = widget_info.get('class')
            set_method = widget_info.get('set_method')
            widget = widget_class()
            value = params.get(param_name)
            getattr(widget, set_method)(value)
            group_lo.addRow(param_name, widget)
            self.__widgets[param_name] = widget

        if not len(param_types):
            lbl = QtWidgets.QLabel('No parameters.')
            group_lo.addRow('', lbl)

        if executable:
            print('exec')
            exec_btn = QtWidgets.QPushButton('Execute')
            exec_btn.clicked.connect(self.execute)
            self.main_layout.addWidget(exec_btn)

        self.resize(400, 0)

    def clear_ui(self):
        if self.main_layout:
            QtWidgets.QWidget().setLayout(self.main_layout)

    def execute(self):
        if not self.group.isChecked():
            return 

        params = {}
        param_types = self.__parameter_types
        task = self.__task

        for param_name, widget in self.__widgets.items():
            param_type = param_types.get(param_name)
            widget_info = WIDGET_TABLE.get(param_type)
            get_method = widget_info.get('get_method')
            params[param_name] = getattr(widget, get_method)()

        task.set_parameters(**params)
        task.execute()