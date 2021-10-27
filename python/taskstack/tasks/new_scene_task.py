from collections import OrderedDict
import maya.cmds as cmds
import taskstack.core.task as task

class NewSceneTask(task.Task):
       
    def execute(self):
        cmds.file(new=True,force=True)