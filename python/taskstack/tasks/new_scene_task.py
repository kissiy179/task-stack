# encoding: UTF-8
from collections import OrderedDict
import maya.cmds as cmds
from taskstack.core.task import Task

class NewSceneTask(Task):
    '''
    新しいシーンを開くタスク
    '''

    def get_default_parameters(self):
        return OrderedDict()
       
    def execute(self):
        super(NewSceneTask, self).execute()
        cmds.file(new=True,force=True)