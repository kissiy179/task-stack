# -*- coding: utf-8 -*-
import sys
import cPickle as pickle
import cStringIO
import copy
import random
from mayaqt import maya_base_mixin, QtCore, QtGui, QtWidgets
import qtawesome as qta
from taskstack.ui import task_list_widget
from taskstack.core import task, task_list
from pyside_components.widgets.tag_item_button import string_to_color

import_icon = qta.icon('fa5s.folder-open', color='lightgray')

class TaskItem(QtGui.QStandardItem):

    def __init__(self, task_=None, *args, **kwargs):
        super(TaskItem, self).__init__(*args, **kwargs) 
        self.task = task_
        params = self.task.get_parameters()

        for param_name in params.keys():
            param_item = ParameterItem(param_name)
            self.appendRow(param_item)

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled #| QtCore.Qt.ItemIsDropEnabled

    def data(self, role):
        if role == QtCore.Qt.DisplayRole:
            return self.task.get_name()

class ParameterItem(QtGui.QStandardItem):

    def __init__(self, *args, **kwargs):
        super(ParameterItem, self).__init__(*args, **kwargs) 

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable #| QtCore.Qt.ItemIsDragEnabled #| QtCore.Qt.ItemIsDropEnabled

class TreeModel(QtGui.QStandardItemModel):
    '''
    ドラッグ&ドロップ可能にしてあるがドロップ後はすべてStandardItemになってしまう
    mimedataの処理が必要
    '''

    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent) 

    def flags(self, index):
        item = self.itemFromIndex(index)

        if not item:
            return QtCore.Qt.ItemIsDropEnabled
        
        return item.flags()

    def data(self, index, role):
        item = self.itemFromIndex(index)

        if role == QtCore.Qt.DisplayRole:
            return '{}  ( {} )'.format(item.data(role), type(item).__name__)

class TreeView(QtWidgets.QTreeView):

    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

    def mousePressEvent(self, event):
        super(TreeView, self).mousePressEvent(event)
        index = self.indexAt(event.pos())
        row = index.row()
        
        if row == -1:
            self.clearSelection()

class TestWindow(maya_base_mixin, QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(TestWindow, self).__init__(parent)
        file_path = task_list_widget.RECENT_TASKS_FILE_PATH
        params = task_list.TaskListParameters()
        params.load(file_path)
        task_list_ = params.create_task_list()

        lo = QtWidgets.QVBoxLayout()
        self.setLayout(lo)
        self.model = TreeModel()
        
        # build model
        for task_ in task_list_:
            task_item = TaskItem(task_, task_.get_name())
            self.model.appendRow(task_item)

        self.tree = TreeView()
        self.tree.setModel(self.model)
        self.model.itemChanged.connect(self.log)
        lo.addWidget(self.tree)

    def log(self, item):
        print(item.data(role=QtCore.Qt.DisplayRole))


def show():
    win = TestWindow()
    win.show()

if __name__ == '__main__':
    show()

'''
import taskstack.ui.draggable_treeview_with_standard as tv; reload(tv)
tv.show()
'''