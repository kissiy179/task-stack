from pprint import pprint
from functools import partial
from mayaqt import maya_base_mixin, QtCore, QtWidgets
from . import WIDGET_TABLE
import qtawesome as qta
from .task_widget import TaskWidget
close_icon = qta.icon('fa5s.trash-alt', color='lightgray')
up_icon = qta.icon('fa5s.chevron-up', color='lightgray')
down_icon = qta.icon('fa5s.chevron-down', color='lightgray')

class InnerTaskListWidget(QtWidgets.QWidget):

    remove_task = QtCore.Signal(int)
    moveup_task = QtCore.Signal(int)
    movedown_task = QtCore.Signal(int)

    def __init__(self, tasks, *args, **kwargs):
        super(InnerTaskListWidget, self).__init__(*args, **kwargs)
        self.__task_widgets = []
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setStyleSheet('QPushButton {background-color: transparent; border-style: solid; border-width:0px;} InnerTaskListWidget{background-color: #3f3f3f}')
        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0,0,0,0)
        lo.setSpacing(0)
        self.setLayout(lo)

        for i, task in enumerate(tasks):
            hlo = QtWidgets.QHBoxLayout()
            hlo.setSpacing(0)
            hlo.setContentsMargins(3,0,0,0)
            lo.addLayout(hlo)
            vlo = QtWidgets.QVBoxLayout()
            hlo.addLayout(vlo)
            vlo.setSpacing(0)

            # Stretch
            vlo.addStretch()

            # Remove button
            remove_btn = QtWidgets.QPushButton()
            remove_btn.setIcon(close_icon)
            remove_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            remove_btn.clicked.connect(partial(self._remove_task, i))
            vlo.addWidget(remove_btn)

            # Spacer
            spacer = QtWidgets.QSpacerItem(5,10)
            vlo.addItem(spacer)

            # Up/Down button
            up_btn = QtWidgets.QPushButton()
            up_btn.setIcon(up_icon)
            up_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            up_btn.clicked.connect(partial(self._moveup_task, i))
            vlo.addWidget(up_btn)
            down_btn = QtWidgets.QPushButton()
            down_btn.setIcon(down_icon)
            down_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            down_btn.clicked.connect(partial(self._movedown_task, i))
            vlo.addWidget(down_btn)

            # Stretch
            vlo.addStretch()

            # Task widget
            task_wdiget = TaskWidget(task)
            task_wdiget.init_ui(executable=False)
            hlo.addWidget(task_wdiget)
            self.__task_widgets.append(task_wdiget)

        lo.addStretch()

    def _remove_task(self, idx):
        self.remove_task.emit(idx)

    def _moveup_task(self, idx):
        self.moveup_task.emit(idx)

    def _movedown_task(self, idx):
        self.movedown_task.emit(idx)

    def apply_parameters(self):
        for task_widget in self.__task_widgets:
            task_widget.apply_parameters()

class TaskListWidget(maya_base_mixin, QtWidgets.QWidget):

    def __init__(self, task_list=(), *args, **kwargs):
        super(TaskListWidget, self).__init__(*args, **kwargs)
        self.__task_list = task_list
        self.__main_layout = None
        self.init_ui()
        self.resize(500, 600)

    def init_ui(self):
        # Clear ui
        self.clear_ui()

        # Main layout
        self.__main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.__main_layout)

        # Scroll Aere
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.__main_layout.addWidget(scroll_area)

        # Parameters Widgets
        tasks = self.__task_list.get_tasks()
        self.inner_wgt = InnerTaskListWidget(tasks)
        self.inner_wgt.remove_task.connect(self.remove_task)
        self.inner_wgt.moveup_task.connect(self.moveup_task)
        self.inner_wgt.movedown_task.connect(self.movedown_task)
        scroll_area.setWidget(self.inner_wgt)

        # Execute button
        exec_btn = QtWidgets.QPushButton('Execute')
        exec_btn.clicked.connect(self.execute)
        self.__main_layout.addWidget(exec_btn)

    def clear_ui(self):
        if self.__main_layout:
            QtWidgets.QWidget().setLayout(self.__main_layout)

    def remove_task(self, idx):
        self.__task_list.remove_task(idx)
        self.init_ui()

    def moveup_task(self, idx):
        self.__task_list.moveup_task(idx)
        self.init_ui()

    def movedown_task(self, idx):
        self.__task_list.movedown_task(idx)
        self.init_ui()

    def execute(self):
        self.inner_wgt.apply_parameters()
        self.__task_list.execute()