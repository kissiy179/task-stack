# -*- coding: utf-8 -*-
import os
from pprint import pprint
from functools import partial
from collections import OrderedDict
from re import L
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
code_icon = qta.icon('fa5s.code', color='lightgray')
undo_icon = qta.icon('fa5s.angle-double-left', color='lightgray')
undo_icon = qta.icon('fa5s.backward', color='lightgray')
JSON_FILTERS = 'Json (*.json)'
TOOLBAR_POSITIONS = {
    'top': QtCore.Qt.TopToolBarArea,
    'bottom': QtCore.Qt.BottomToolBarArea,
    'left': QtCore.Qt.LeftToolBarArea,
    'right': QtCore.Qt.RightToolBarArea,
}
PRESET_DIR_PATH = os.path.join(os.environ.get('MAYA_APP_DIR'), 'taskstack')
RECENT_TASKS_FILE_PATH = os.path.join(PRESET_DIR_PATH, 'recent_tasks.json')


class HorizontalLine(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super(HorizontalLine, self).__init__(*args, **kwargs)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Plain)

class InnerTaskListWidget(QtWidgets.QWidget):

    remove_task = QtCore.Signal(int)
    moveup_task = QtCore.Signal(int)
    movedown_task = QtCore.Signal(int)
    updated = QtCore.Signal()
    start_execute = QtCore.Signal()
    execute_task = QtCore.Signal(int)
    executed = QtCore.Signal()
    error_raised = QtCore.Signal(str)
    warning_raised = QtCore.Signal(str)
    increment = QtCore.Signal()

    def __init__(self, taks_list, show_details=True, *args, **kwargs):
        super(InnerTaskListWidget, self).__init__(*args, **kwargs)
        self.__task_list = taks_list
        self.__task_widgets = []
        self.show_details = show_details
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setStyleSheet('QPushButton {background-color: transparent; border-style: solid; border-width:0px;} InnerTaskListWidget{background-color: #3f3f3f}')
        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0,0,0,0)
        lo.setSpacing(0)
        self.setLayout(lo)

        # Connect signals
        task_list_emitter = self.__task_list.get_emitter()
        task_list_emitter.start_execute.connect(self.start_execute)
        task_list_emitter.executed.connect(self.executed)
        task_list_emitter.error_raised.connect(self.error_raised)
        task_list_emitter.warning_raised.connect(self.warning_raised)
        task_list_emitter.increment.connect(self.increment)

        for i, task in enumerate(self.__task_list):
            hlo = QtWidgets.QHBoxLayout()
            hlo.setSpacing(0)
            hlo.setContentsMargins(3,0,0,0)
            lo.addLayout(hlo)
            vlo = QtWidgets.QVBoxLayout()   
            hlo.addLayout(vlo, 1)
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
            task_wdiget.init_ui(show_parameters=self.show_details, label_prefix='[ {} ]  '.format(i))#executable=False)
            task_wdiget.updated.connect(self.updated)
            hlo.addWidget(task_wdiget, 100)
            self.__task_widgets.append(task_wdiget)

            # Line
            line = HorizontalLine()
            lo.addWidget(line)

        lo.addStretch()

    def execute(self):
        with self.__task_list:
            self.__task_list.execute()

    def _remove_task(self, idx):
        self.remove_task.emit(idx)

    def _moveup_task(self, idx):
        self.moveup_task.emit(idx)

    def _movedown_task(self, idx):
        self.movedown_task.emit(idx)

    def apply_parameters(self):
        for task_widget in self.__task_widgets:
            task_widget.apply_parameters()

class CustomProgressBar(QtWidgets.QProgressBar):

    def __init__(self, *args, **kwargs):
        super(CustomProgressBar, self).__init__(*args, **kwargs)

    def increment(self):
        value = self.value()
        self.setValue(value + 1)

class TaskListWidget(maya_dockable_mixin, QtWidgets.QMainWindow):

    updated = QtCore.Signal()
    show_raw_text = False

    def __init__(self, task_list=None, use_recent_tasks=False, *args, **kwargs):
        super(TaskListWidget, self).__init__(*args, **kwargs)
        self.setWindowTitle('Task List')
        self.setMinimumHeight(400)

        if task_list:
            self.__task_list = task_list
            use_recent_tasks = False # taks_listの指定がある場合RECENT_TASKS_FILE_PATHは使用しない

        else:
            self.__task_list = TaskList()

        self.__menu_bar = None
        self.__tool_bar = None
        self.__tool_bar_position = None
        self.__status_bar = None
        self.__main_layout = None
        self.__actions = self.get_actions()
        self.__task_list_menu = TaskListMenu()
        self.__task_list_menu.triggered.connect(self.add_task_class)
        # self.__task_list_menu.start_reload.connect(self.)
        self.__task_list_menu.start_reload.connect(self.store_task_list_parameters)
        self.__task_list_menu.end_reload.connect(self.restore_task_list_parameters)
        self.__task_list_parameters = ''
        self.__ignored_actions = []
        self.show_details = True
        self.init_ui()
        self.resize(500, 600)
        # self.updated.connect(self.log)

        if use_recent_tasks:
            self.import_task_list_parameters(RECENT_TASKS_FILE_PATH)
            self.updated.connect(partial(self.export_task_list_parameters, RECENT_TASKS_FILE_PATH))

    def log(self):
        print(self.__task_list.get_parameters())

    def init_ui(self, executable=True, show_details=None, tool_bar_position=''):
        # Result show details
        show_details = show_details if show_details else self.show_details

        # Clear ui
        self.clear_ui()

        # Main widget
        main_wgt = QtWidgets.QWidget()
        self.setCentralWidget(main_wgt)

        # Main layout
        self.__main_layout = QtWidgets.QVBoxLayout()
        # self.__main_layout.setContentsMargins(0,0,0,0)
        main_wgt.setLayout(self.__main_layout)

        # Scroll aere
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet('QScrollArea {background-color: #2b2b2b;}')
        self.__main_layout.addWidget(self.scroll_area)

        # Tasks widgets
        self.inner_wgt = InnerTaskListWidget(self.__task_list, show_details=show_details)
        self.raw_text = QtWidgets.QTextEdit()

        if not self.show_raw_text:
            self.inner_wgt.remove_task.connect(self.remove_task)
            self.inner_wgt.moveup_task.connect(self.moveup_task)
            self.inner_wgt.movedown_task.connect(self.movedown_task)
            self.inner_wgt.updated.connect(self.updated)
            self.inner_wgt.start_execute.connect(self.preprocess)
            self.scroll_area.setWidget(self.inner_wgt)

        # Row Text
        else:
            params = TaskListParameters(self.__task_list.get_parameters())
            self.raw_text.setText(params.dumps())
            self.raw_text.setReadOnly(True)
            self.scroll_area.setWidget(self.raw_text)

        # Buttons
        buttons_lo = QtWidgets.QHBoxLayout()
        self.__main_layout.addLayout(buttons_lo)
        buttons_lo.setContentsMargins(0,0,0,0)

        if executable:
            # self.init_menu_bar()
            self.init_tool_bar(position=tool_bar_position)
            self.init_status_bar()

            # プログレスバーのインクリメントはinner_wgtのシグナル経由で行う
            self.inner_wgt.increment.connect(self.__progress_bar.increment)


        # Emit Signal
        self.updated.emit()

    def init_menu_bar(self):
        if self.__menu_bar:
            return

        self.__menu_bar = self.menuBar()
        menu = self.__menu_bar.addMenu('&File')

        for action in self.__actions.get('io_actions'):
            menu.addAction(action)

    def init_tool_bar(self, position=''):
        TOOLBAR_POSITION = TOOLBAR_POSITIONS.get(position)
        
        if self.__tool_bar:
            self.addToolBar(TOOLBAR_POSITION, self.__tool_bar) if TOOLBAR_POSITION else None
            return 

        toolbar = QtWidgets.QToolBar('Commands')
        self.addToolBar(TOOLBAR_POSITION, toolbar) if TOOLBAR_POSITION else self.addToolBar(toolbar)
        toolbar.setIconSize(QtCore.QSize(16, 16))

        for action in self.__actions.get('exec_actions'):
            if not action.text() in self.__ignored_actions:
                toolbar.addAction(action)

        toolbar.addSeparator() #-----

        for action in self.__actions.get('task_list_actions'):
            if not action.text() in self.__ignored_actions:
                toolbar.addAction(action)

        toolbar.addSeparator() #-----

        for action in self.__actions.get('io_actions'):
            if not action.text() in self.__ignored_actions:
                toolbar.addAction(action)

        toolbar.addSeparator() #-----

        for action in self.__actions.get('flow_actions'):
            if not action.text() in self.__ignored_actions:
                toolbar.addAction(action)

        self.__tool_bar = toolbar

    def init_status_bar(self):
        if not self.__status_bar:
            self.__status_bar = QtWidgets.QStatusBar()
            self.setStatusBar(self.__status_bar)
            self.__progress_bar = CustomProgressBar()
            self.__progress_bar.setValue(0)
            self.__status_bar.addPermanentWidget(self.__progress_bar)
            # self.__progress_bar.setMaximumWidth(100)
            self.__progress_bar.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

        task_count = len(self.__task_list)
        self.__status_bar.showMessage('{} tasks.'.format(task_count))
        self.__status_bar.setSizeGripEnabled(False)
        self.__progress_bar.setVisible(False)

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

        # Add task
        add_task_action = QtWidgets.QAction(add_icon, 'Add task', self)
        add_task_action.triggered.connect(self.select_task_class)
        task_list_actions.append(add_task_action)

        # Toggle details
        toggle_details_action = QtWidgets.QAction(detail_icon, 'Toggle show ditails', checkable=True, parent=self)
        toggle_details_action.triggered.connect(self.toggle_show_details)
        task_list_actions.append(toggle_details_action)

        # Toggle row string
        toggle_raw_action = QtWidgets.QAction(code_icon, 'Toggle raw strings', checkable=True, parent=self)
        toggle_raw_action.triggered.connect(self.toggle_raw_strings)
        task_list_actions.append(toggle_raw_action)

        # Toggle deetails
        # toggle_task_details_action = QtWidgets.QAction(detail_icon, 'Toggle Task Details', self)
        # task_list_actions.append(toggle_task_details_action)

        # Clear Tasks
        clear_tasks_action = QtWidgets.QAction(close_icon, 'Clear tasks', self)
        clear_tasks_action.triggered.connect(self.clear_tasks)
        task_list_actions.append(clear_tasks_action)

        # Flow actions -------
        flow_actions = []
        actions['flow_actions'] = flow_actions

        # Toggle ukndo enabled
        self.toggle_undo_action = QtWidgets.QAction(undo_icon, 'Toggle undo enabled', checkable=True, parent=self)
        self.toggle_undo_action.triggered.connect(self.toggle_undo_enabled)
        flow_actions.append(self.toggle_undo_action)
        return actions

    def get_task_list(self):
        return self.__task_list

    def set_task_list(self, task_list):
        self.__task_list = task_list
        self.init_ui()
        
    def select_task_class(self):
        # self.__task_list_menu.move(QtGui.QCursor.pos())
        # self.__task_list_menu.show()
        self.__task_list_menu.exec_(QtGui.QCursor.pos())

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

    def store_task_list_parameters(self):
        self.inner_wgt.apply_parameters()
        params = TaskListParameters(self.__task_list.get_parameters())
        text = params.dumps()
        self.__task_list_parameters = text

    def restore_task_list_parameters(self):
        params = TaskListParameters()
        text = self.__task_list_parameters
        params.loads(text)
        self.__task_list.set_parameters(params)
        self.init_ui()

    def import_task_list_parameters(self, file_path=''):
        if not file_path:
            file_info = QtWidgets.QFileDialog().getOpenFileName(self, 'Import TaskList Parameters', filter=JSON_FILTERS)
            file_path = file_info[0]

        if not file_path or not os.path.exists(file_path):
            return

        params = TaskListParameters()
        params.load(file_path)
        self.__task_list.set_parameters(params)
        self.init_ui()

    def export_task_list_parameters(self, file_path=''):
        if not file_path:
            file_info = QtWidgets.QFileDialog().getSaveFileName(self, 'Export TaskList Parameters', filter=JSON_FILTERS)
            file_path = file_info[0]

        if not file_path:
            return

        dir_path = os.path.dirname(file_path)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        self.inner_wgt.apply_parameters()
        params = TaskListParameters(self.__task_list.get_parameters())
        params.dump(file_path)

    def preprocess(self):
        self.__progress_bar.setVisible(True)
        tasks = self.__task_list
        self.__progress_bar.setMaximum(len([task for task in tasks if task.get_active()]))
        self.__progress_bar.setValue(0)

    def execute(self):
        self.inner_wgt.execute()

    def toggle_show_details(self):
        self.show_details = not self.show_details
        self.init_ui(show_details=self.show_details)

    def toggle_raw_strings(self):
        self.show_raw_text = not self.show_raw_text
        self.init_ui()

    def toggle_undo_enabled(self):
        checked = self.toggle_undo_action.isChecked()
        self.__task_list.set_undo_enabled(checked)

    def set_ignore_actions(self, action_names=()):
        self.__ignored_actions = action_names