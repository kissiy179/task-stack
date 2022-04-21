# -*- coding: utf-8 -*-
from collections import OrderedDict
import taskstack.core.task as task
import taskstack.core.task_list as task_list

class CompoundTask(task.Task):
    '''
    複合タスク
    タスク情報ファイルを指定して内部に複数のタスクを持つことができる
    '''
    
    def get_default_parameters(self):
        return OrderedDict((
            ('Task List File', ''),
            ('Child Tasks', '')
        ))

    def get_parameter_types(self):
        parameter_types = super(CompoundTask, self).get_parameter_types()
        parameter_types['Task List File'] = 'file_in_pj'
        parameter_types['Child Tasks'] = 'task_list'
        return parameter_types

    def get_parameters(self, consider_keywords=True):
        # タスク情報ファイルからパラメータを取得
        parameters = super(CompoundTask, self).get_parameters(consider_keywords)
        task_list_file = parameters.get('Task List File')
        task_list_parameters = task_list.TaskListParameters()
        task_list_parameters.load(task_list_file)

        # 子タスクに受け渡し
        parameters['Child Tasks'] = task_list_parameters
        return parameters

    def execute(self):
        super(CompoundTask, self).execute()
        parameters = self.get_parameters()

        # タスク情報ファイルからタスクリストの取得
        child_parameters = parameters.get('Child Tasks')
        task_list_parameters = task_list.TaskListParameters()
        task_list_parameters.loads(child_parameters)
        task_list_ = task_list.TaskList()
        task_list_.set_parameters(task_list_parameters)

        # 無限ループになるのでタスクリストにこのクラスのタスクがあった場合除外
        del_tasks = [task_ for task_ in task_list_ if type(task_) == type(self)]
        
        for del_task in del_tasks:
            idx = task_list_.index(del_task)
            del task_list_[idx]

        # タスクリストの実行
        with task_list_:
            task_list_.execute()

    # def undo(self):
    #     '''
    #     必要な場合Undo処理を書く
    #     '''
    #     super(CompoundTask, self).undo(True)
