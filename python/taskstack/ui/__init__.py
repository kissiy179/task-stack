from mayaqt import *

WIDGET_TABLE = {
    'int': QtWidgets.QSpinBox,
    'float': QtWidgets.QDoubleSpinBox,
    'string': QtWidgets.QLineEdit,
}

import task_widget; reload(task_widget)