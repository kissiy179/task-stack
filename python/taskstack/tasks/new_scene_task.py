from collections import OrderedDict
import maya.cmds as cmds
import taskstack.core.task as task

class NewSceneTask(task.Task):

    def get_default_parameters(self):
        return OrderedDict()
       
    def execute(self):
        cmds.file(new=True,force=True)