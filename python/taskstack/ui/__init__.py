from mayaqt import *

WIDGET_TABLE = {
    'int': {'class': QtWidgets.QSpinBox, 'get_method': 'value', 'set_method': 'setValue'},
    'float': {'class': QtWidgets.QDoubleSpinBox, 'get_method': 'value', 'set_method': 'setValue'},
    'str': {'class': QtWidgets.QLineEdit, 'get_method': 'text', 'set_method': 'setText'},
}

import task_widget; reload(task_widget)
import task_list_widget; reload(task_list_widget)