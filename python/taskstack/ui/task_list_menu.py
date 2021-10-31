from pprint import pprint
from functools import partial
from mayaqt import maya_base_mixin, QtCore, QtWidgets
from . import WIDGET_TABLE
import qtawesome as qta
from ..core import task_list
from ..core import task
close_icon = qta.icon('fa5s.clipboard-list', color='lightgray')

class TaskListMenu(QtWidgets.QMenu):

    triggered = QtCore.Signal(task.Task)

    def __init__(self, *args, **kwargs):
        super(TaskListMenu, self).__init__(*args, **kwargs)
        self.setTearOffEnabled(True)
        self.setWindowTitle('Tasks')
        task_classes = task_list.get_task_classes()
        max_task_class_name_len = max([len(cls.__name__) for cls in task_classes.values()])
        lbls = ['{}: {}'.format(task_class.__name__.ljust(max_task_class_name_len), task_class.get_doc(first_line_only=True)) for task_class in task_classes.values()]

        for i, lbl in enumerate(lbls):
            action = QtWidgets.QAction(close_icon, lbl, self)
            task_class = task_classes.values()[i]
            action.triggered.connect(partial(self.trigger, task_class))
            self.addAction(action)

    def trigger(self, task_name):
        self.triggered.emit(task_name)
