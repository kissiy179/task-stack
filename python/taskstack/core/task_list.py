# -*- coding: utf-8 -*-
import os
from collections import OrderedDict
# import abc
import json
from qtpy import QtCore
from .task import Task
import maya.cmds as cmds

class SignalEmitter(QtCore.QObject):
    start_execute = QtCore.Signal()
    executed = QtCore.Signal()
    error_raised = QtCore.Signal(str)
    warning_raised = QtCore.Signal(str)
    increment = QtCore.Signal()

class TaskList(list):
    
    # __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.__emitter = SignalEmitter()
        self.__executed = False
        self.__undo_enabled = False

    def get_emitter(self):
        return self.__emitter

    def __enter__(self):
        # self.execute()
        cmds.undoInfo(openChunk=True)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        cmds.undoInfo(closeChunk=True)
        self.undo_if_executed()
        self.__executed = False

    def get_parameters(self, consider_keywords=False):
        params = []

        for task in self:
            params.append(task.get_info(consider_keywords))

        return params

    def set_parameters(self, parameters):
        self.clear_tasks()
        
        try:
            print(parameters)
            for task_info in parameters:
                self.add_task(info=task_info)

        except Exception as e:
            print(e)

    def add_task(self, task=None, info={}):
        if not task:
            task = Task.get_task_by_info(info)

        if not task:
            return

        # Connect signals
        task_emitter = task.get_emitter()
        task_emitter.error_raised.connect(self.__emitter.error_raised)
        task_emitter.warning_raised.connect(self.__emitter.warning_raised)
        task_emitter.executed.connect(self.__emitter.increment)
        self.append(task)

    def remove_task(self, idx):
        del self[idx]

    def move_task(self, idx, move=1):
        src_task = self[idx]
        tgt_idx = (idx + move) % len(self)
        del self[idx]
        self.insert(tgt_idx, src_task)

    def moveup_task(self, idx):
        self.move_task(idx, -1)

    def movedown_task(self, idx):
        self.move_task(idx, 1)

    def clear_tasks(self):
        del self[:]

    def execute(self):
        print('[TaskStack] {0} {1}.execute. {0}'.format('-'*20, type(self).__name__))

        self.__emitter.start_execute.emit()
        self.__executed = True

        for task in self:
            task.execute_if_active()

        self.__emitter.executed.emit()

    def get_undo_enabled(self):
        return self.__undo_enabled

    def set_undo_enabled(self, undo_enabled):
        self.__undo_enabled = undo_enabled

    def undo(self):
        '''
        各タスクのundo処理を実行
        executeされた後のみ実行される
        '''
        print('[TaskStack] {0} {1}.undo. {0}'.format('-'*20, type(self).__name__))
        cmds.undo()

        for task in self[::-1]:
            task.undo_if_active()

    def undo_if_executed(self):
        '''
        実行済みの場合のみUndo処理を行う
        '''
        if not self.__executed or not self.__undo_enabled:
            return

        self.undo()

class TaskListParameters(list):

    def __init__(self, *args, **kwargs):
        # self.__source_parameters
        # self.__parameters
        super(TaskListParameters, self).__init__(*args, **kwargs)

    def load(self, path):
        if not os.path.exists(path):
            return

        with open(path, 'r') as f:
            params = json.load(f)#, object_pairs_hook=OrderedDict)

        self.__init__(params)

    def dump(self, path):
        dirpath = os.path.dirname(path)

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            
        with open(path, 'w') as f:
            json.dump(self, f, indent=4)

    def loads(self, s):
        params = json.loads(s)#, object_pairs_hook=OrderedDict)
        self.__init__(params)

    def dumps(self):
        s = json.dumps(self, indent=4)
        return s

    def load_task(self, task):
        task_list = TaskList()
        task_list.add_task(task)
        self.load_task_list(task_list)

    def load_task_list(self, task_list):
        params = task_list.get_parameters(consider_keywords=False)
        self.__init__(params)

    def create_task_list(self):
        task_list = TaskList()
        task_list.set_parameters(self)
        return task_list
