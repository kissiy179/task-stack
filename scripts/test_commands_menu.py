#encoding: utf-8

import maya.cmds as cmds
import maya.cmds as cmds
import reloadable_menu

def show_message(message):
    print(message)
    cmds.inViewMessage(assistMessage=message,
                        position='midCenter',
                        fade=True,
                        # fadeStayTime=3000,
                        )

def open_tasklist(*args):
    import taskstack; reload(taskstack)
    import taskstack.ui; reload(taskstack.ui)
    import taskstack.ui.task_list_widget as task_list_widget

    wgt = task_list_widget.TaskListWidget()
    wgt.show()

@reloadable_menu.reloadable_menu('Test Commands')
def create_menu():
    # cmds.setParent('MayaWindow')
    # cmds.menu(label='Test Commands', tearOff=True)
    cmds.menuItem(label='TaskStack', command=open_tasklist)

