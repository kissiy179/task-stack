import copy
from mayaqt import maya_base_mixin, QtCore, QtGui, QtWidgets
import taskstack; #reload(taskstack)
from taskstack.ui import task_list_widget
from taskstack.core import task, task_list

class BaseItem(object):
    
    def __init__(self, parent=None):
        self._headers = ('name', 'value')
        self.parentItem = parent
        self.childItems = []

    def addChild(self, child):
        self.childItems.append(child)

    def removeChild(self, row):
        self.childItems.pop(row)
    
    def clear(self):
        self.childItems = []

    def columnCount(self):
        return len(self._headers)

    def __len__(self):
        return len(self.childItems)

    def child(self, row):
        print(row, self.children)
        if len(self.childItems) > row:
            return self.childItems[row]

        else:
            return None

    def parent(self):
        return self.parentItem

    def data(self, column):
        return self.header(column)

    def header(self, column):
        return self._headers[column]

class ParameterItem(BaseItem):

    def __init__(self, name='dummy parameter', value=-1, parent=None):
        super(ParameterItem, self).__init__(parent=parent)
        self.__name = name
        self.__value = value

    def data(self, column):
        if column == 0:
            return self.__name

        elif column == 1:
            return self.__value

class TaskItem(BaseItem):
    
    def __init__(self, task_=None, parent=None):
        super(TaskItem, self).__init__(parent=parent)
        self.__task = task_
        # self._headers = ('name', 'description')
        # self._headers = ('name',)
        self.setupParameters()

    def setupParameters(self):
        if not self.__task:
            return

        paramItem = ParameterItem('', self.__task.get_doc(), self)
        self.addChild(paramItem)

        for name, value in self.__task.get_parameters().items():
            paramItem = ParameterItem(name, value, self)
            self.addChild(paramItem)

    def data(self, column):
        if self.__task is None:
            return ""

        if column == 0:
            return self.__task.get_name()

        elif column == 1:
            return self.__task.get_doc()

    def get_task(self):
        return self.__task

class TaskModel(QtCore.QAbstractItemModel):

    def __init__(self, task_list_=None, parent=None):
        super(TaskModel, self).__init__(parent)
        self.__task_list = task_list_
        self.rootItem = TaskItem()
        self.setupModelData()

    def setupModelData(self, task_list_=None):
        task_list_ = task_list_ if task_list_ else self.__task_list
        self.rootItem.clear()
        self.beginResetModel()
        tasks = task_list_
        
        for task_ in tasks:
            item = TaskItem(task_, self.rootItem)
            self.rootItem.addChild(item)

        self.endResetModel()

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsSelectable
 
    def supportedDropActions(self):
        return QtCore.Qt.MoveAction | QtCore.Qt.CopyAction
    
    def itemFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()

        return self.rootItem

    def rowCount(self, parent):
        # if parent.column() > 0:
        #     return 0

        parentItem = self.itemFromIndex(parent)
        return len(parentItem)

    def columnCount(self, parent):
        parentItem = self.itemFromIndex(parent)
        return parentItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        item = self.itemFromIndex(index)

        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())

    def index(self, row, column, parentIndex):
        print row, column, parentIndex
        parentItem = self.itemFromIndex(parentIndex)
        # print(parentItem)
        childItem = parentItem.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)

        return self.createIndex(row, 0, parentItem)

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        item = index.internalPointer()
        parentItem = item.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(index.row(), 0, parentItem)

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.header(section)
            
        return None

    def insertRows(self, row, count, parentIndex):
        self.beginInsertRows(parentIndex, row, row+count-1)
        self.endInsertRows()
        return True
    
    def removeRows(self, row, count, parentIndex):
        self.beginRemoveRows(parentIndex, row, row+count-1)
        parent = self.itemFromIndex(parentIndex)
        parent.removeChild(row)
        self.endRemoveRows()
        return True
    
    def mimeTypes(self):
        types = []
        types.append('application/json')
        return types
    
    def mimeData(self, index):
        item = self.itemFromIndex(index[0])
        mimedata = TaskMime(item)
        return mimedata
    
    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        item = mimedata.itemInstance()
        dropParent = self.itemFromIndex(parentIndex)
        # itemCopy = copy.deepcopy(item)
        dropParent.addChild(item)
        self.insertRows(len(dropParent)-1, 1, parentIndex)
        self.dataChanged.emit(parentIndex, parentIndex)
        return True

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
    
class TestWindow(maya_base_mixin, QtWidgets.QWidget):

    def __init__(self, task_list_, *args):
        super(TestWindow, self).__init__(*args)
        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0,0,0,0)
        self.setLayout(lo)
        tree = QtWidgets.QTreeView()
        tree.setDragEnabled(True)
        tree.setAcceptDrops(True)
        tree.setDragDropMode( QtWidgets.QAbstractItemView.InternalMove )
        # tree.header().hide()
        model = TaskModel(task_list_)
        tree.setModel(model)
        lo.addWidget(tree)

def main():
    file_path = task_list_widget.RECENT_TASKS_FILE_PATH
    params = task_list.TaskListParameters()
    params.load(file_path)
    print(params)
    task_list_ = task_list.TaskList()
    task_list_.set_parameters(params)

    # show window
    win = TestWindow(task_list_)
    win.show()

if __name__ == '__main__':
    main()

'''
import taskstack.ui.treeview_test as tv; reload(tv)
tv.main()
'''