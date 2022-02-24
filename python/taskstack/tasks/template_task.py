# -*- coding: utf-8 -*-
from collections import OrderedDict
import taskstack.core.task as task

class TemplateTask(task.Task):
    '''
    テンプレートタスク
    '''
    
    def get_default_parameters(self):
        return OrderedDict((
            ('Test Text', 'Test'),
            ('Test Bool', True),
            ('Test Number', 0.0),
        ))

    # def get_parameter_types(self):
    #     parameter_types = super(TemplateTask, self).get_parameter_types()
    #     parameter_types['Test Text'] = 'file_in_pj'
    #     return parameter_types

    def execute(self):
        super(TemplateTask, self).execute()
        parameters = self.get_parameters()
        test_text = parameters.get('Test Text')
        test_bool = parameters.get('Test Bool')
        test_number = parameters.get('Test Number')

        print(test_text)
        print(test_bool)
        print(test_number)
