# -*- coding: utf-8 -*-
from mayaqt import QtWidgets

class CustomSpinBox(QtWidgets.QSpinBox):
    '''最大値を引き上げたSpinBox'''

    def __init__(self, *args, **kwargs):
        super(CustomSpinBox, self).__init__(*args, **kwargs)
        self.setMaximum(100000)

class CustomDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    '''最大値を引き上げたDoubleSpinBox'''

    def __init__(self, *args, **kwargs):
        super(CustomDoubleSpinBox, self).__init__(*args, **kwargs)
        self.setMaximum(100000)


WIDGET_TABLE = {
    'int': {'class': CustomSpinBox, 'get_method': 'value', 'set_method': 'setValue'},
    'float': {'class': CustomDoubleSpinBox, 'get_method': 'value', 'set_method': 'setValue'},
    'str': {'class': QtWidgets.QLineEdit, 'get_method': 'text', 'set_method': 'setText'},
}

import task_widget; reload(task_widget)
import task_list_widget; reload(task_list_widget)