# -*- coding: utf-8 -*-
import sys
import json
import cPickle as pickle
import cStringIO
import copy
import random
from mayaqt import maya_base_mixin, QtCore, QtGui, QtWidgets
import qtawesome as qta
from taskstack.ui import task_list_widget
from taskstack.core import task, task_list
from pyside_components.widgets.tag_item_button import string_to_color

task_icon = qta.icon('mdi.cube', color='cyan')
param_icon = qta.icon('fa5s.dice-d6', color='lightgreen')
param_icon = qta.icon('fa5s.eye', color='lightgreen')
param_icon = qta.icon('fa5s.feather', color='lightgreen')
param_icon = qta.icon('fa5s.list', color='lightgreen')
param_icon = qta.icon('mdi.cards-diamond', color='lightgreen')
param_icon = qta.icon('fa.dot-circle-o', color='lightgreen')
param_icon = qta.icon('fa5s.genderless', color='lightgreen')
param_icon = qta.icon('fa5s.ghost', color='lightgreen')
param_icon = qta.icon('mdi.bullseye', color='lightgreen')
param_icon = qta.icon('mdi.checkbox-multiple-blank-circle', color='lightgreen')
param_icon = qta.icon('mdi.disc', color='lightgreen')
param_icon = qta.icon('mdi.gamepad-circle-outline', color='lightgreen')
param_icon = qta.icon('mdi.hexagon', color='lightgreen')
param_icon = qta.icon('mdi.hexagon-multiple', color='lightgreen')
param_icon = qta.icon('mdi.hexagon-slice-6', color='lightgreen')
param_icon = qta.icon('mdi.music-note-whole', color='lightgreen')
param_icon = qta.icon('mdi.nut', color='lightgreen')
param_icon = qta.icon('mdi.puzzle', color='lightgreen')
param_icon = qta.icon('mdi.record-circle-outline', color='lightgreen')
param_icon = qta.icon('mdi.source-commit', color='lightgreen')
param_icon = qta.icon('mdi.circle-medium', color='lightgreen')
param_icon = qta.icon('fa5s.bullseye', color='lightgreen')
param_icon = qta.icon('fa5.dot-circle', color='lightgreen')
param_icon = qta.icon('fa5s.neuter', color='lightgreen')
param_icon = qta.icon('mdi.adjust', color='lightgreen')

class TaskItem(QtGui.QStandardItem):

    def __init__(self, task_=None, *args, **kwargs):
        super(TaskItem, self).__init__(*args, **kwargs) 
        self.task = task_
        params = self.task.get_parameters()

        for name, value in params.items():
            param_item = ParameterItem(name, value)
            self.appendRow(param_item)

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled

    def data(self, role):
        if role == QtCore.Qt.DisplayRole:
            return self.task.get_name()

        elif role == QtCore.Qt.DecorationRole:
            return task_icon

    def mimeTypes(self):
        return ['text/plain']

    def mimeData(self):
        info = self.task.get_info()
        data = QtCore.QMimeData()
        info_text = json.dumps(info)
        data.setText(info_text)
        return data

    def dropMimeData(self, model, data, action, row, column):
        parent_item = self.parent()

        if not parent_item:
            parent_item = model
            
        # mimeDataからアイテムを復元
        info_text = data.text()
        info = json.loads(info_text)
        task_ = task.Task.get_task_by_info(info)
        task_item = TaskItem(task_, task_.get_name())

        # アイテムを挿入
        row = self.row() + 1
        parent_item.insertRow(row, task_item)
        model.itemChanged.emit(task_item)
        return True

class ParameterItem(QtGui.QStandardItem):

    def __init__(self, name, value, *args, **kwargs):
        super(ParameterItem, self).__init__(name) 
        self.name = name
        self.value = value

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDropEnabled #| QtCore.Qt.ItemIsDragEnabled

    def data(self, role):
        if role == QtCore.Qt.DisplayRole:
            return '{} = {}'.format(self.name, self.value)

        elif role == QtCore.Qt.DecorationRole:
            return param_icon
        
        else:
            return super(ParameterItem, self).data(role)

    def dropMimeData(self, model, data, action, row, column):
        parent_task_item = self.parent()
        return parent_task_item.dropMimeData(model, data, action, row, column)

class TreeModel(QtGui.QStandardItemModel):
    '''
    ドラッグ&ドロップ可能にしてあるがドロップ後はすべてStandardItemになってしまう
    mimedataの処理が必要
    '''

    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)

    def flags(self, index):
        item = self.itemFromIndex(index)
        
        if hasattr(item, 'flags'):
            return item.flags()

        return super(TreeModel, self).flags(index)

    def data(self, index, role):
        item = self.itemFromIndex(index)

        if hasattr(item, 'data'):
            return item.data(role)

        return super(TreeModel, self).data(index, role)

    def mimeTypes(self):
        child = self.invisibleRootItem().child(0)

        if hasattr(child, 'mimeTypes'):
            return child.mimeTypes()

        return super(TreeModel, self).mimeTypes()

    def mimeData(self, indexes):
        index = indexes[0]
        item = self.itemFromIndex(index)

        if hasattr(item, 'mimeData'):
            return item.mimeData()

        return super(TreeModel, self).mimeData(indexes)

    def dropMimeData(self, data, action, row, column, parent):
        parent_item = self.itemFromIndex(parent)

        if hasattr(parent_item, 'dropMimeData'):
            return parent_item.dropMimeData(self, data, action, row, column)

        # ここから↓↓↓は継承先クラスでの実装もしくはアイテムに移譲したい
        # mimeDataからアイテムを復元
        info_text = data.text()
        info = json.loads(info_text)
        task_ = task.Task.get_task_by_info(info)
        task_item = TaskItem(task_, task_.get_name())

        # アイテムを挿入
        if row < 0:
            row = self.rowCount()

        parent_item = self.invisibleRootItem()
        self.insertRow(row, task_item)
        self.itemChanged.emit(task_item)
        return True

class DraggableTreeView(QtWidgets.QTreeView):
    '''
    ドラッグ&ドロップ機能を有効にしたTreeView
    ModelにはQStandardItemModelを継承したものを渡す想定
    '''

    def __init__(self, parent=None):
        super(DraggableTreeView, self).__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.current_is_expanded = False

    def setModel(self, model):
        '''
        setModelをオーバーライド
        '''
        # モデル登録
        super(DraggableTreeView, self).setModel(model)

        # シグナル接続
        model.itemChanged.connect(self.post_drop_item_process, QtCore.Qt.QueuedConnection) # 変更処理が終わってから実行したいのでQueuedConnection(キューに入れらた接続)を指定

    def mousePressEvent(self, event):
        '''
        マウス押下時の処理
        '''
        # 押下位置がアイテム外だったら選択をクリア
        super(DraggableTreeView, self).mousePressEvent(event)
        index = self.indexAt(event.pos())
        row = index.row()
        
        if row == -1:
            self.clearSelection()

        # 押下アイテムの展開状態を保持
        self.current_is_expanded = self.isExpanded(index)

    def select_item(self, item):
        '''
        アイテムを選択する
        '''
        sel_model = self.selectionModel()
        index = item.index()
        sel_model.select(index, QtCore.QItemSelectionModel.Rows | QtCore.QItemSelectionModel.ClearAndSelect)

    def post_drop_item_process(self, item):
        '''
        アイテムドロップ後の処理
        '''
        index = item.index()
        self.select_item(item)
        self.setExpanded(index, self.current_is_expanded)

class TestWindow(maya_base_mixin, QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(TestWindow, self).__init__(parent)
        file_path = task_list_widget.RECENT_TASKS_FILE_PATH
        params = task_list.TaskListParameters()
        params.load(file_path)
        task_list_ = params.create_task_list()

        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0,0,0,0)
        self.setLayout(lo)
        self.model = TreeModel()
        
        # build model
        for task_ in task_list_:
            task_item = TaskItem(task_, task_.get_name())
            # task_item = QtGui.QStandardItem(task_.get_name())
            self.model.appendRow(task_item)

            # for i in range(3):
            #     child_task_item = TaskItem(task_, task_.get_name())
            #     task_item.appendRow(child_task_item)

        self.tree = DraggableTreeView()
        self.tree.setModel(self.model)
        # self.tree.expandAll()
        self.tree.setHeaderHidden(True)
        lo.addWidget(self.tree)

def show():
    win = TestWindow()
    win.show()

if __name__ == '__main__':
    show()

'''
import taskstack.ui.draggable_treeview_with_standard as tv; reload(tv)
tv.show()
'''