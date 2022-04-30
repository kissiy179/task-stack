# -*- coding: utf-8 -*-
import os
from collections import OrderedDict
from pprint import pprint
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
            ('Child Tasks', []),
        ))

    def get_parameter_types(self):
        parameter_types = super(CompoundTask, self).get_parameter_types()
        parameter_types['Task List File'] = 'file_in_pj'
        parameter_types['Child Tasks'] = 'task_list'
        return parameter_types

    # def get_parameters(self, consider_keywords=True):
    #     # タスク情報ファイルからパラメータを取得
    #     parameters = super(CompoundTask, self).get_parameters(consider_keywords)
    #     task_list_file = parameters.get('Task List File')
    #     task_list_parameters = task_list.TaskListParameters()
    #     task_list_parameters.load(task_list_file)

    #     # 子タスクに受け渡し
    #     parameters['Child Tasks'] = task_list_parameters
    #     return parameters

    def get_signal_connection_infos(self):
        conn_infos = super(CompoundTask, self).get_signal_connection_infos()
        conn_infos['Task List File'] = {'Child Tasks': 'import_parameters'}
        return conn_infos

    def set_parameters(self, **parameters):
        '''
        このオブジェクトにパラメータを設定する
        子タスクで設定済みのパラメータはなるべく再現する

        ＊＊＊注意＊＊＊
        設定済みパラメータを再現するため既存子タスクと新規設定子タスクのマッチングは単純な名前で行う
        そのため同じタスクが複数ある場合実行順が遅い子タスクの値がすべてのタスクに引き継がれる
        '''
        # 通常通りタスク情報を上書き
        crr_params = super(CompoundTask, self).set_parameters(**parameters)

        # タスクファイルからタスク情報を取得
        task_list_file = crr_params.get('Task List File')
        task_list_params = task_list.TaskListParameters()
        task_list_params.load(task_list_file)

        # 読み込んだタスク情報を現在の子タスク情報で上書き
        crr_child_task_params = crr_params.get('Child Tasks')

        for i, task_info in enumerate(task_list_params):
            task_name = task_info.get('name')

            for crr_task_info in crr_child_task_params:
                crr_task_name = crr_task_info.get('name')

                if crr_task_name == task_name:
                    for key in task_info:
                        if key in crr_task_info:
                            value = crr_task_info[key]
                            # print(task_name, key, value)
                            task_info[key] = value
                            task_list_params[i] = task_info
        
        crr_params['Child Tasks'] = task_list_params
        return super(CompoundTask, self).set_parameters(**crr_params)

    def execute(self):
        super(CompoundTask, self).execute()
        parameters = self.get_parameters()

        # タスク情報ファイルからタスクリストの取得
        child_parameters = parameters.get('Child Tasks')
        task_list_ = task_list.TaskList()
        task_list_.set_parameters(child_parameters)

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
