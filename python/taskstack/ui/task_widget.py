from mayaqt import *

class TaskWidget(maya_base_mixin, QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(TaskWidget, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        lo = QtWidgets.QFormLayout()
        self.setLayout(lo)
        btn = QtWidgets.QPushButton('task')
        lo.addRow('task button', btn)