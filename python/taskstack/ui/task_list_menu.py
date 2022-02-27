# -*- coding: utf-8 -*-
from pprint import pprint
from functools import partial
from mayaqt import maya_base_mixin, QtCore, QtWidgets
from . import WIDGET_TABLE
import qtawesome as qta
from ..core.task import Task
close_icon = qta.icon('fa5s.clipboard-list', color='lightgray')
reload_icon = qta.icon('fa5s.sync-alt', color='lightgray')

class TaskListMenu(QtWidgets.QMenu):

    triggered = QtCore.Signal(Task)
    reloaded = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(TaskListMenu, self).__init__(*args, **kwargs)
        self.setTearOffEnabled(True)
        self.setTitle('Tasks')
        self.reload_task_classes()
        # self.init_ui() # reload_taks_classesに含まれる

    def init_ui(self):
        task_class_names = [cls.__name__ for cls in self.__task_classes.values()]
        max_task_class_name_lens = [len(task_class_name) for task_class_name in task_class_names]
        max_task_class_name_len = max(max_task_class_name_lens) if max_task_class_name_lens else 0
        lbls = ['{}: {}'.format(task_class_names[i].ljust(max_task_class_name_len), task_class.get_doc(first_line_only=True)) for i, task_class in enumerate(self.__task_classes.values())]
        self.clear()

        for i, lbl in enumerate(lbls):
            action = QtWidgets.QAction(close_icon, lbl, self)
            task_class = self.__task_classes.values()[i]
            
            if not task_class.is_display_in_list():
                continue

            action.triggered.connect(partial(self.trigger, task_class.__name__))
            self.addAction(action)

        if not lbls:
            action = QtWidgets.QAction('No Tasks...', self)
            self.addAction(action)

        # Update action
        self.addSeparator()
        action = QtWidgets.QAction(reload_icon, 'Reload Tasks', self)
        action.triggered.connect(self.reload_task_classes)
        self.addAction(action)
        # action.setEnabled(False)

    def trigger(self, task_name):
        task_class = self.__task_classes.get(task_name)
        self.triggered.emit(task_class)

    def reload_task_classes(self):
        self.__task_classes = Task.get_task_classes(force=True)
        self.init_ui()
        self.reloaded.emit()
