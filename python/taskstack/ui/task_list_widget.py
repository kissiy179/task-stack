from pprint import pprint
from mayaqt import maya_base_mixin, QtWidgets
from . import WIDGET_TABLE
import qtawesome as qta
from .task_widget import TaskWidget
close_icon = qta.icon('fa5s.trash-alt', color='lightgray')
up_icon = qta.icon('fa5s.chevron-up', color='lightgray')
down_icon = qta.icon('fa5s.chevron-down', color='lightgray')

class InnerTaskListWidget(QtWidgets.QWidget):

    def __init__(self, tasks, *args, **kwargs):
        super(InnerTaskListWidget, self).__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setStyleSheet('QPushButton {background-color: transparent; border-style: solid; border-width:0px;}')
        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0,0,0,0)
        self.setLayout(lo)

        for task in tasks:
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
            vlo.addWidget(remove_btn)

            # Spacer
            spacer = QtWidgets.QSpacerItem(5,10)
            vlo.addItem(spacer)

            # Up/Down button
            up_btn = QtWidgets.QPushButton()
            up_btn.setIcon(up_icon)
            up_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            vlo.addWidget(up_btn)
            down_btn = QtWidgets.QPushButton()
            down_btn.setIcon(down_icon)
            down_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            vlo.addWidget(down_btn)

            # Stretch
            vlo.addStretch()

            # Task widget
            task_wdiget = TaskWidget(task)
            task_wdiget.init_ui(executable=False)
            hlo.addWidget(task_wdiget)


class TaskListWidget(maya_base_mixin, QtWidgets.QWidget):

    def __init__(self, task_list=(), *args, **kwargs):
        super(TaskListWidget, self).__init__(*args, **kwargs)
        self.__task_list = task_list
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_lo = QtWidgets.QVBoxLayout()
        self.setLayout(main_lo)

        # Scroll Aere
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_lo.addWidget(scroll_area)

        # Main Widgets
        tasks = self.__task_list.get_tasks()
        inner_wgt = InnerTaskListWidget(tasks)
        scroll_area.setWidget(inner_wgt)

        # Execute button
        exec_btn = QtWidgets.QPushButton('Execute')
        exec_btn.clicked.connect(self.execute)
        main_lo.addWidget(exec_btn)

        # Resize
        self.resize(500, 600)

    def execute(self):
        self.__task_list.execute()