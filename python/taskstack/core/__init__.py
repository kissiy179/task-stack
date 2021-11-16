class TaskStackError(Exception):
    def __init__(self, message):
        super(TaskStackError, self).__init__(message)

class TaskStackWarning(Exception):
    def __init__(self, message):
        super(TaskStackWarning, self).__init__(message)

import task; reload(task)
import task_list; reload(task_list)