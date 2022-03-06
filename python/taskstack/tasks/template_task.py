# -*- coding: utf-8 -*-
from collections import OrderedDict
import taskstack.core.task as task

class TemplateTask(task.Task):
    '''
    テンプレートタスク
    '''
    
    def get_default_parameters(self):
        '''
        UIに表示したいパラメータを定義する
        OrderedDictにすることで順番が保持される（保持が必要ない場合dictでも良い)
        以下のフォーマットをのように書く

        OrderedDict((
            (パラメータ名, デフォルト値),
            ...
        }

        UIはデフォルト値から勝手に判断して作成されるが、get_parameter_typesメソッドを実装することで個別に指定できる
        '''
        return OrderedDict((
            ('Test File', 'Test'),
            ('Test Bool', True),
            ('Test Number', 0.0),
        ))

    def get_parameter_types(self):
        '''
        パラメータごとにUIタイプを指定したい場合にしよするメソッド
        書かなければデフォルト値から判断されたUIが使われる
        使用できるタイプはtaskstack.ui.__init__.pyのWIDGET_TABLEを参照
        '''
        parameter_types = super(TemplateTask, self).get_parameter_types()
        parameter_types['Test File'] = 'file'
        return parameter_types

    def execute(self):
        '''
        このタスクが実行したい処理を書く
        UIで指定したパラメータの値はget_parametersメソッドでdict(OrderedDict)で取得できる
        '''
        super(TemplateTask, self).execute()
        parameters = self.get_parameters()
        test_file = parameters.get('Test File')
        test_bool = parameters.get('Test Bool')
        test_number = parameters.get('Test Number')

        print(test_file)
        print(test_bool)
        print(test_number)

    def undo(self):
        '''
        必要な場合Undo処理を書く
        '''
        super(TemplateTask, self).undo(True)
