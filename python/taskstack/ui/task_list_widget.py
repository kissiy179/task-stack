from pprint import pprint
from mayaqt import maya_base_mixin, QtWidgets
from . import WIDGET_TABLE
from .task_widget import TaskWidget

class InnerTaskListWidget(QtWidgets.QWidget):

    def __init__(self, tasks, *args, **kwargs):
        super(InnerTaskListWidget, self).__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0,0,0,0)
        self.setLayout(lo)

        for task in tasks:
            task_wdiget = TaskWidget(task)
            task_wdiget.init_ui(executable=False)
            lo.addWidget(task_wdiget)


class TaskListWidget(maya_base_mixin, QtWidgets.QWidget):

    def __init__(self, task_list=(), *args, **kwargs):
        super(TaskListWidget, self).__init__(*args, **kwargs)
        self.__task_list = task_list
        self.init_ui()

    def init_ui(self):
        main_lo = QtWidgets.QVBoxLayout()
        # main_lo.setContentsMargins(0,0,0,0)
        self.setLayout(main_lo)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_lo.addWidget(scroll_area)
        tasks = self.__task_list.get_tasks()
        inner_wgt = InnerTaskListWidget(tasks)
        scroll_area.setWidget(inner_wgt)
        exec_btn = QtWidgets.QPushButton('Execute')
        main_lo.addWidget(exec_btn)