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

import_icon = qta.icon('fa5s.folder-open', color='lightgray')

class BaseItem(object):
    def __init__(self, parent=None):
        self.children = []
        self.parent = parent
        self.headers = ['Name']
        
        if parent is not None:
            self.parent.addChild(self)
        
    def addChild(self, child):
        self.children.append(child)
        child.parent = self

    def insertChild(self, row, child):
        self.children.insert(row, child)
        child.parent = self
    
    def removeChild(self, row):
        self.children.pop(row)
    
    def child(self, row):
        if len(self.children) > row:
            return self.children[row]

        return None
    
    def rowCount(self):
        return len(self.children)

    def columnCount(self):
        return max(1, len(self.headers))
    
    def row(self):
        if self.parent is not None:
            return self.parent.children.index(self)

    def data(self, column=0, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return type(self).__name__

class TaskItem(BaseItem):

    def __init__(self, task_, parent=None):
        super(TaskItem, self).__init__(parent)
        self._task = task_

    def get_task(self):
        return self._task

    def data(self, column=0, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self._task.get_name()
        
        elif role == QtCore.Qt.DecorationRole:
            return import_icon

        elif role == QtCore.Qt.CheckStateRole:
            return self._task.get_active()

        elif role == QtCore.Qt.BackgroundRole:
            return QtGui.QColor(65,65,65)

#====================================================================

class PyObjMime(QtCore.QMimeData):
    MIMETYPE = 'application/x-pyobj'

    def __init__(self, data=None): 
        super(PyObjMime, self).__init__() 
 
        self.data = data 
        if data is not None: 
            # Try to pickle data
            try: 
                pdata = pickle.dumps(data) 
            except: 
                return 

            self.setData(self.MIMETYPE, pickle.dumps(data.__class__) + pdata) 

    def itemInstance(self): 
        if self.data is not None: 
            return self.data

        io = cStringIO.StringIO(str(self.data(self.MIMETYPE))) 

        try: 
            # Skip the type. 
            pickle.load(io) 

            # Recreate the data. 
            return pickle.load(io) 
        except: 
            pass 

        return None

class TaskMime(QtCore.QMimeData):
    MIMETYPE = 'application/json'

    def __init__(self, item=None): 
        super(TaskMime, self).__init__()
        
        if item:
            task_ = item.get_task()
            params = task_.get_parameters(consider_keywords=False)
            params = [{'name': task_.get_name(), 'active': task_.get_active(), 'parameters': params}]
            params_obj = task_list.TaskListParameters(params)
            data = params_obj.dumps()
            # print(type(data))
            self.setData(self.MIMETYPE, data)
            self.setText(data)
            self.setUrls([r'https://srinikom.github.io/pyside-docs/PySide/QtCore/QMimeData.html'])

    def itemInstance(self):
        text = str(self.data(self.MIMETYPE))
        text = self.text()
        params_obj = task_list.TaskListParameters()
        params_obj.loads(text)
        first_params = params_obj[0]
        task_name = first_params.get('name')
        task_active = first_params.get('active')
        params = first_params.get('parameters')
        task_class = task.Task.get_task_classes().get(task_name)

        if not task_class:
            return None

        task_ = task_class()
        task_.set_active(task_active)
        task_.set_parameters(**params)
        item = TaskItem(task_)
        return item

#====================================================================

class TreeModel(QtCore.QAbstractItemModel):

    showIndex = False

    def __init__(self, root, parent=None):
        super(TreeModel, self).__init__(parent)
        self.root = root
        
    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled

        # return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsSelectable
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsSelectable
    
    def supportedDropActions(self):
        return QtCore.Qt.MoveAction | QtCore.Qt.CopyAction
    
    def itemFromIndex(self, index):
        if index.isValid():
            # print(index)
            return index.internalPointer()

        return self.root
    
    def rowCount(self, index):
        item = self.itemFromIndex(index)
        return item.rowCount()
    
    def columnCount(self, index):
        item = self.itemFromIndex(index)
        columnCount = item.columnCount()

        if self.showIndex:
            columnCount += 1

        return columnCount
    
    def data(self, index, role):
        # インデックス表示ON、0列目の場合行番号を返す
        if self.showIndex and index.column() == 0:
            if role == QtCore.Qt.DisplayRole:
                return str(index.row())

            else:
                return None
            
        # それ以外はアイテムに任せる
        item = self.itemFromIndex(index)
        data = item.data(index.column(), role)
        return data
    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            headers = copy.deepcopy(self.root.headers)

            if self.showIndex:
                headers.insert(0, 'Index')  

            return headers[section]
            
        return None
        
    def index(self, row, column, parentIndex):
        parentItem = self.itemFromIndex(parentIndex)
        item = parentItem.child(row)           
        return self.createIndex(row, column, item)
    
    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
            
        item = index.internalPointer()

        try:
            parentItem = item.parent

            if parentItem == self.root:
                return QtCore.QModelIndex()

            else:
                return self.createIndex(parentItem.row(), 0, parentItem)
                
        except: pass

    def insertRows(self, row, count, parentIndex):
        self.beginInsertRows(parentIndex, row, row+count-1)
        self.endInsertRows()
        # print 'insertRows'
        return True
    
    def removeRows(self, row, count, parentIndex):
        try: # エラーが出るタイミングがあるのでエラー処理
            self.beginRemoveRows(parentIndex, row, row + count-1)
            parent = self.itemFromIndex(parentIndex)
            parent.removeChild(row)
            self.endRemoveRows()
            return True

        except: pass
    
    def mimeTypes(self):
        types = []
        # types.append('application/x-pyobj')
        types.append('application/json')
        return types
    
    def mimeData(self, index):
        item = self.itemFromIndex(index[0])
        # mimedata = PyObjMime(item)
        mimedata = TaskMime(item)
        self.dragging_index = index[0]
        return mimedata
    
    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        dropParent = self.itemFromIndex(parentIndex)

        if dropParent != self.root:
            return

        item = mimedata.itemInstance()
        self.beginInsertRows(parentIndex, row, row)
        dropParent.insertChild(row, item)
        self.endInsertRows()
        return True

class TestWindow(maya_base_mixin, QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(TestWindow, self).__init__(parent)
        file_path = task_list_widget.RECENT_TASKS_FILE_PATH
        params = task_list.TaskListParameters()
        params.load(file_path)
        task_list_ = params.create_task_list()

        root = BaseItem()

        for task_ in task_list_:
            TaskItem(task_, root)
        
        # itemA = TaskItem( 'ItemA', root )
        # itemB = TaskItem( 'ItemB', root )
        # itemC = TaskItem( 'ItemC', root )
        # itemG = TaskItem( 'ItemG', root )
        # itemD = TaskItem( 'ItemD', itemA )
        # itemE = TaskItem( 'ItemE', itemB )
        # itemF = TaskItem( 'ItemF', itemC )
        # itemH = TaskItem( 'ItemH', itemG)

        lo = QtWidgets.QVBoxLayout()
        self.setLayout(lo)
        self.model = TreeModel(root)
        self.model.rowsInserted.connect(self.selectItem, QtCore.Qt.QueuedConnection) # すべて終わってから処理するのでQueuedConnectionが必要
        # self.sel_model = QtCore.QItemSelectionModel()
        # model.showIndex = True
        self.tree = QtWidgets.QTreeView()
        self.tree.setModel(self.model)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.tree.expandAll()
        lo.addWidget(self.tree)

        self.tree2 = QtWidgets.QTreeView()
        self.tree2.setModel(self.model)
        self.tree2.setSelectionModel(self.tree.selectionModel())
        lo.addWidget(self.tree2)

        self.sel_model = self.tree.selectionModel()

        tglBtn = QtWidgets.QPushButton('Show Index')
        tglBtn.clicked.connect(self.toggle)
        lo.addWidget(tglBtn)

    def log(self, selection, command):
        print('test')
        print(selection, command)

    def toggle(self):
        showIndex = not self.model.showIndex
        self.model = TreeModel(self.model.root) 
        self.model.showIndex = showIndex
        self.tree.setModel(self.model)

    def selectItem(self, parent=QtCore.QModelIndex(), first=0, last=0):
        try:
            dragging_row = self.model.dragging_index.row()

            if first > dragging_row:
                first -= 1
            
        except: pass

        item = self.model.itemFromIndex(parent)
        child_item = item.children[first]
        child = self.model.createIndex(first, 0, child_item)
        # print self.model.itemFromIndex(child)

        # セレクションモデルはすでに削除されているのでItemViewから再取得
        sel_model = self.tree.selectionModel()
        sel_model.select(child, QtCore.QItemSelectionModel.Rows|QtCore.QItemSelectionModel.ClearAndSelect)

def main():
    win = TestWindow()
    win.show()

if __name__ == '__main__':
    main()

'''
import taskstack.ui.treeview_test2 as tv; reload(tv)
tv.main()
'''