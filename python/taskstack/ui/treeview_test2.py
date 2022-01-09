from mayaqt import *
import sys
import cPickle as pickle
import cStringIO
import copy
from mayaqt import maya_base_mixin, QtCore, QtGui, QtWidgets


class Item(object):
    def __init__(self, name, parent=None):
        self.name = name
        self.children = []
        self.parent = parent
        
        if parent is not None:
            self.parent.addChild( self )
        
    def addChild(self, child):
        self.children.append(child)
        child.parent = self
    
    def removeChild(self, row):
        self.children.pop(row)
    
    def child(self, row):
        # return self.children[row]
        if len(self.children) > row:
            return self.children[row]

        return None
    
    def __len__(self):
        return len(self.children)
    
    def row(self):
        if self.parent is not None:
            return self.parent.children.index(self)
        
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
    
#====================================================================

class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, root, parent=None):
        super(TreeModel, self).__init__(parent)
        self.root = root
        
    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsSelectable
    
    def supportedDropActions(self):
        return QtCore.Qt.MoveAction | QtCore.Qt.CopyAction
    
    def itemFromIndex(self, index):
        if index.isValid():
            # print(index)
            return index.internalPointer()

        return self.root
    
    def rowCount(self, index):
        item = self.itemFromIndex(index)
        return len(item)
    
    def columnCount(self, index):
        return 1
    
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            item = self.itemFromIndex(index)
            return item.name
    
    def index(self, row, column, parentIndex):
        parentItem = self.itemFromIndex(parentIndex)
        item = parentItem.child(row)
        # print(parentItem)

        # if not item:
        #     return None
            
        return self.createIndex(row, column, item)

        # if item:
        #     index_ = self.createIndex(row, column, item)

        # else:
        #     index_ = self.createIndex(row, column, parentItem)

        # return index_
    
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
        try:
            # print count
            # print 'start removeRows'
            # print parentIndex, row, row + count-1
            self.beginRemoveRows(parentIndex, row, row + count-1)
            # print 'beginRemoveRows'
            parent = self.itemFromIndex(parentIndex)
            parent.removeChild(row)
            self.endRemoveRows()
            # print 'end removeRows'
            return True

        except: pass
    
    def mimeTypes(self):
        types = []
        types.append('application/x-pyobj')
        return types
    
    def mimeData(self, index):
        item = self.itemFromIndex(index[0])
        mimedata = PyObjMime(item)
        return mimedata
    
    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        item = mimedata.itemInstance()
        dropParent = self.itemFromIndex(parentIndex)
        itemCopy = copy.deepcopy(item)
        dropParent.addChild(itemCopy)
        self.insertRows(len(dropParent)-1, 1, parentIndex)
        self.dataChanged.emit(parentIndex, parentIndex)
        return True

class TestWindow(maya_base_mixin, QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(TestWindow, self).__init__(parent)
        root = Item( 'root' )
        itemA = Item( 'ItemA', root )
        itemB = Item( 'ItemB', root )
        itemC = Item( 'ItemC', root )
        itemG = Item( 'ItemG', root )
        itemD = Item( 'ItemD', itemA )
        itemE = Item( 'ItemE', itemB )
        itemF = Item( 'ItemF', itemC )
        itemH = Item( 'ItemH', itemG)

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