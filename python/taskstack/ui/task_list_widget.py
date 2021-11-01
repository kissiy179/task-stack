# -*- coding: utf-8 -*-
from pprint import pprint
from functools import partial
from collections import OrderedDict
from mayaqt import maya_base_mixin, maya_dockable_mixin, QtCore, QtWidgets, QtGui
from . import WIDGET_TABLE
import qtawesome as qta
from ..core.task_list import TaskList, TaskListParameters
from .task_widget import TaskWidget
from .task_list_menu import TaskListMenu
import_icon = qta.icon('fa5s.folder-open', color='lightgray')
export_icon = qta.icon('fa5s.save', color='lightgray')
close_icon = qta.icon('fa5s.trash-alt', color='lightgray')
up_icon = qta.icon('fa5s.chevron-up', color='lightgray')
down_icon = qta.icon('fa5s.chevron-down', color='lightgray')
exec_icon = qta.icon('fa5s.play', color='lightgreen')
add_icon = qta.icon('fa5s.plus', color='lightgray')
detail_icon = qta.icon('fa5s.align-left', color='lightgray')
JSON_FILTERS = 'Json (*.json)'
TOOLBAR_POSITION = {
    'top': QtCore.Qt.TopToolBarArea,
    'bottom': QtCore.Qt.BottomToolBarArea,
    'left': QtCore.Qt.LeftToolBarArea,
    'right': QtCore.Qt.RightToolBarArea,
}

class HorizontalLine(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super(HorizontalLine, self).__init__(*args, **kwargs)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Plain)

class InnerTaskListWidget(QtWidgets.QWidget):

    remove_task = QtCore.Signal(int)
    moveup_task = QtCore.Signal(int)
    movedown_task = QtCore.Signal(int)

    def __init__(self, tasks, *args, **kwargs):
        super(InnerTaskListWidget, self).__init__(*args, **kwargs)
        self.__task_widgets = []
        self.__show_details = True
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

            # # Spacer
            # spacer = QtWidgets.QSpacerItem(5,10)
            # vlo.addItem(spacer)

            # # Execute button
            # exec_btn = QtWidgets.QPushButton()
            # exec_btn.setIcon(exec_icon)
            # vlo.addWidget(exec_btn)

            # Stretch
            vlo.addStretch()

            # Task widget
            task_wdiget = TaskWidget(task)
            task_wdiget.init_ui(show_parameters=self.__show_details, label_prefix='[ {} ]  '.format(i))#executable=False)
            hlo.addWidget(task_wdiget)
            self.__task_widgets.append(task_wdiget)

            # Line
            line = HorizontalLine()
            lo.addWidget(line)

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

class TaskListWidget(maya_dockable_mixin, QtWidgets.QMainWindow):

    def __init__(self, task_list=None, *args, **kwargs):
        super(TaskListWidget, self).__init__(*args, **kwargs)
        self.setWindowTitle('Task List')
        self.setMinimumHeight(400)
        self.__task_list = task_list if task_list else TaskList()
        self.__menu_bar = None
        self.__tool_bar = None
        self.__status_bar = None
        self.__main_layout = None
        self.__actions = self.get_actions()
        self.__task_list_menu = TaskListMenu()
        self.__task_list_menu.triggered.connect(self.add_task_class)
        self.init_ui()
        self.resize(500, 600)

    def init_ui(self, executable=True, tool_bar_position='top'):
        # Clear ui
        self.clear_ui()

        # Main widget
        main_wgt = QtWidgets.QWidget()
        self.setCentralWidget(main_wgt)

        # Main layout
        self.__main_layout = QtWidgets.QVBoxLayout()
        self.__main_layout.setContentsMargins(0,0,0,0)
        main_wgt.setLayout(self.__main_layout)

        # Scroll Aere
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet('QScrollArea {background-color: #2b2b2b;}')
        self.__main_layout.addWidget(self.scroll_area)

        # Parameters Widgets
        tasks = self.__task_list.get_tasks()
        self.inner_wgt = InnerTaskListWidget(tasks)
        self.inner_wgt.remove_task.connect(self.remove_task)
        self.inner_wgt.moveup_task.connect(self.moveup_task)
        self.inner_wgt.movedown_task.connect(self.movedown_task)
        self.scroll_area.setWidget(self.inner_wgt)

        # Buttons
        buttons_lo = QtWidgets.QHBoxLayout()
        self.__main_layout.addLayout(buttons_lo)
        buttons_lo.setContentsMargins(0,0,0,0)

        if executable:
            # self.init_menu_bar()
            self.init_tool_bar(position=tool_bar_position)
            self.init_status_bar()

    def init_menu_bar(self):
        if self.__menu_bar:
            return

        self.__menu_bar = self.menuBar()
        menu = self.__menu_bar.addMenu('&File')

        for action in self.__actions.get('io_actions'):
            menu.addAction(action)

    def init_tool_bar(self, position='top'):
        if self.__tool_bar:
            self.addToolBar(TOOLBAR_POSITION.get(position), self.__tool_bar)
            return 

        toolbar = QtWidgets.QToolBar('Commands')
        self.addToolBar(TOOLBAR_POSITION.get(position), toolbar)
        toolbar.setIconSize(QtCore.QSize(16, 16))

        for action in self.__actions.get('exec_actions'):
            toolbar.addAction(action)

        toolbar.addSeparator() #-----

        for action in self.__actions.get('task_list_actions'):
            toolbar.addAction(action)

        toolbar.addSeparator() #-----

        for action in self.__actions.get('io_actions'):
            toolbar.addAction(action)

        self.__tool_bar = toolbar

    def init_status_bar(self):
        if not self.__status_bar:
            self.__status_bar = QtWidgets.QStatusBar()
            self.setStatusBar(self.__status_bar)

        task_count = len(self.__task_list.get_tasks())
        self.__status_bar.showMessage('{} tasks.'.format(task_count))
        
    def clear_ui(self):
        if self.__main_layout:
            QtWidgets.QWidget().setLayout(self.__main_layout)

    def get_actions(self):
        actions = OrderedDict()

        # I/O actions ------
        io_actions = []
        actions['io_actions'] = io_actions

        # Import tasks
        import_task_list_parameters_action = QtWidgets.QAction(import_icon, '&Import Tasks', self)
        import_task_list_parameters_action.triggered.connect(self.import_task_list_parameters)
        io_actions.append(import_task_list_parameters_action)

        # Export tasks
        export_task_list_parameters_action = QtWidgets.QAction(export_icon, '&Emport Tasks', self)
        export_task_list_parameters_action.triggered.connect(self.export_task_list_parameters)
        io_actions.append(export_task_list_parameters_action)

        # Execute actions -------
        exec_actions = []
        actions['exec_actions'] = exec_actions

        # Execute
        exec_action = QtWidgets.QAction(exec_icon, 'Execute', self)
        exec_action.triggered.connect(self.execute)
        exec_actions.append(exec_action)

        # Tasks actions -------
        task_list_actions = []
        actions['task_list_actions'] = task_list_actions

        # Add Task
        add_task_action = QtWidgets.QAction(add_icon, 'Add Task', self)
        add_task_action.triggered.connect(self.select_task_class)
        task_list_actions.append(add_task_action)

        # Toggle deetails
        # toggle_task_details_action = QtWidgets.QAction(detail_icon, 'Toggle Task Details', self)
        # task_list_actions.append(toggle_task_details_action)

        # Clear Tasks
        clear_tasks_action = QtWidgets.QAction(close_icon, 'Clear Tasks', self)
        clear_tasks_action.triggered.connect(self.clear_tasks)
        task_list_actions.append(clear_tasks_action)

        return actions
        
    def select_task_class(self):
        self.__task_list_menu.move(QtGui.QCursor.pos())
        self.__task_list_menu.show()

    def add_task_class(self, task_class):
        task = task_class()
        self.add_task(task)

    def add_task(self, task=None, name='NewSceneTask', parameters={}):
        self.__task_list.add_task(task=task, name=name, parameters=parameters)
        self.init_ui()
        varticalBar = self.scroll_area.verticalScrollBar()
        varticalBar.setSliderPosition(varticalBar.maximum())

    def remove_task(self, idx):
        varticalBar = self.scroll_area.verticalScrollBar()
        crr_position = varticalBar.sliderPosition()
        self.__task_list.remove_task(idx)
        self.init_ui()
        varticalBar = self.scroll_area.verticalScrollBar()
        varticalBar.setSliderPosition(crr_position)

    def moveup_task(self, idx):
        varticalBar = self.scroll_area.verticalScrollBar()
        crr_position = varticalBar.sliderPosition()
        self.__task_list.moveup_task(idx)
        self.init_ui()
        varticalBar = self.scroll_area.verticalScrollBar()
        varticalBar.setSliderPosition(crr_position)

    def movedown_task(self, idx):
        varticalBar = self.scroll_area.verticalScrollBar()
        crr_position = varticalBar.sliderPosition()
        self.__task_list.movedown_task(idx)
        self.init_ui()
        varticalBar = self.scroll_area.verticalScrollBar()
        varticalBar.setSliderPosition(crr_position)

    def clear_tasks(self):
        self.__task_list.clear_tasks()
        self.init_ui()

    def import_task_list_parameters(self):
        file_info = QtWidgets.QFileDialog().getOpenFileName(self, 'Import TaskList Parameters', filter=JSON_FILTERS)
        file_path = file_info[0]

        if not file_path:
            return

        params = TaskListParameters()
        params.load(file_path)
        self.__task_list.set_parameters(params)
        self.init_ui()

    def export_task_list_parameters(self):
        file_info = QtWidgets.QFileDialog().getSaveFileName(self, 'Export TaskList Parameters', filter=JSON_FILTERS)
        file_path = file_info[0]

        if not file_path:
            return

        self.inner_wgt.apply_parameters()
        params = TaskListParameters(self.__task_list.get_parameters())
        params.dump(file_path)

    def execute(self):
        self.inner_wgt.apply_parameters()
        self.__task_list.execute()
