# -*- coding: utf-8 -*-
from mayaqt import *
import sys
import cPickle as pickle
import cStringIO
import copy
from mayaqt import maya_base_mixin, QtCore, QtGui, QtWidgets
from taskstack.ui import task_list_widget
from taskstack.core import task, task_list

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

    def data(self, column, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return type(self).__class__.__name__

class TaskItem(BaseItem):

    def __init__(self, task_, parent=None):
        super(TaskItem, self).__init__(parent)
        self._task = task_

    def get_task(self):
        return self._task

    def data(self, column, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self._task.get_name()
        
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
            params = [{'name': task_.get_name(), 'parameters': params}]
            params_obj = task_list.TaskListParameters(params)
            data = params_obj.dumps()
            # print(type(data))
            self.setData(self.MIMETYPE, data)
            self.setText(data)

    def itemInstance(self):
        text = self.text()
        params_obj = task_list.TaskListParameters()
        params_obj.loads(text)
        first_params = params_obj[0]
        task_name = first_params.get('name')
        params = first_params.get('parameters')
        task_class = task.Task.get_task_classes().get(task_name)

        if not task_class:
            return None

        task_ = task_class()
        task_.set_parameters(**params)
        item = TaskItem(task_)
        return item

#====================================================================

class TreeModel(QtCore.QAbstractItemModel):
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
        return item.columnCount()
    
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            item = self.itemFromIndex(index)
            return item.data(index.column(), role)
    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.root.headers[section]
            
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
        return mimedata
    
    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        dropParent = self.itemFromIndex(parentIndex)

        if dropParent != self.root:
            return

        item = mimedata.itemInstance()
        # itemCopy = copy.deepcopy(item)
        dropParent.insertChild(row, item)
        # self.insertRows(len(dropParent)-1, 1, parentIndex)
        self.insertRows(row, 1, parentIndex) # beginInsertRows, endInsertRowsの呼び出しが必要？
        self.dataChanged.emit(parentIndex, parentIndex)
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
        model = TreeModel(root) 
        tree = QtWidgets.QTreeView()
        tree.setModel( model ) 
        tree.setDragEnabled(True)
        tree.setAcceptDrops(True)
        tree.setDragDropMode( QtWidgets.QAbstractItemView.InternalMove )
        tree.show()
        tree.expandAll()
        lo.addWidget(tree)

def main():
    win = TestWindow()
    win.show()

if __name__ == '__main__':
    main()

'''
import taskstack.ui.treeview_test2 as tv; reload(tv)
tv.main()
'''