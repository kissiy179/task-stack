# -*- coding: utf-8 -*-
import sys
import os
import imp
import abc
import re
import copy
import traceback
from collections import OrderedDict
from qtpy import QtCore
from . import TaskStackError, TaskStackWarning

TASK_DIRS = os.environ.get('TASKSTACK_TASK_DIRS')
TASK_DIRS = TASK_DIRS if TASK_DIRS else ''
PYTHON_EXTENSIONS = ('.py', )
ERROR_PATTERN = re.compile(r'.*(?P<main_err>^[a-zA-Z]*(Error|Warning): .*$)', re.MULTILINE | re.DOTALL)
KEYWORD_PATTERN = re.compile(r'({([\w ]+)})')

class SignalEmitter(QtCore.QObject):
    executed = QtCore.Signal()
    execute_start = QtCore.Signal()
    error_raised = QtCore.Signal(str)
    warning_raised = QtCore.Signal(str)

class Task(object):
    
    __metaclass__ = abc.ABCMeta
    __task_classes = []

    def __init__(self):
        self.__default_parameters = self.get_default_parameters()
        self.__parameters = self.get_default_parameters()
        self.__extraparameters = OrderedDict()
        self.__active = True
        self.__emitter = SignalEmitter()

    def get_emitter(self):
        return self.__emitter

    @abc.abstractmethod
    def get_default_parameters(self):
        '''
        パラメータのデフォルト値をOrderedDictで返す
        get_parameter_typesメソッドをオーバーライドしない限りこのvalueの型がUIウィジェット決定に使用される
        '''
        return OrderedDict()
        
    @abc.abstractmethod
    def execute(self):
        '''
        タスクの実行処理
        このオブジェクトに格納されたパラメータを使用する場合はget_parametersメソッドを使用する
        '''
        print('[TaskStack] {}.execute.'.format(type(self).__name__))

    def undo(self, inherit=False):
        '''
        タスクのUndo処理
        MayaのUndoが効かないコマンド(fileコマンドなど)を戻したい場合に実装する
        親のTaskListでexecuteと逆の順番で実行される想定
        '''
        if inherit:
            print('[TaskStack] {}.undo.'.format(type(self).__name__))

    @classmethod
    def get_task_classes(cls, force=False):
        '''
        環境変数で指定されたフォルダ内のpyファイルをロードしてこのクラスから派生したタスククラスを取得
        タスク生成タイミングなどで呼ぶと使用しているタスクオブジェクトのクラスを書き換えてしまったりするのでtaskstackパッケージ読み込み時に1度だけ行う
        '''
        if not force and cls.__task_classes:
            return cls.__task_classes

        task_classes = OrderedDict()

        for task_dir in TASK_DIRS.split(';'):
            for dirpath, dirnames, filenames in os.walk(task_dir):
                for filename in filenames:
                    basename, ext = os.path.splitext(filename)

                    if not ext in PYTHON_EXTENSIONS:
                        continue

                    filepath = os.path.join(dirpath, filename)
                    module = imp.load_source(basename, filepath)

                    for name, obj in module.__dict__.items():
                        if not isinstance(obj, type):
                            continue

                        if not Task in obj.__mro__ or obj == Task:
                            continue
                        
                        task_classes[obj.__name__] = obj
                        print('Import task. [{}]'.format(obj.__name__))

        cls.__task_classes = task_classes
        return task_classes

    @classmethod
    def is_display_in_list(cls):
        '''
        クラス選択リストに表示するかどうか
        classmethodにする必要がある
        '''
        return True
        
    def get_parameter_types(self):
        '''
        使用するUIウィジェットを決定するための各パラメータの型を返す
        基本的にはget_defalt_parametersの値を使用する
        別のタイプを指定したい場合はこのメソッドをオーバーライドする
        '''
        parameter_types = OrderedDict()

        for name, value in self.__default_parameters.items():
            parameter_types[name] = type(value).__name__

        return parameter_types
    
    def get_parameters(self, consider_keywords=True):
        '''
        このオブジェクトに格納されたパラメータを返す
        consider_keywords=Trueの場合「{}」を含む文字列の場合「{}」は他のパラメータへのリンクとみなし値を置き換える
        ex)
        Name = 'Bob'
        Node Name = 'Node_{Name}'
        RESOLVED: Node Name = 'Node_Bob'
        '''
        parameters = copy.deepcopy(self.__parameters)

        if consider_keywords:
            for name, value in parameters.items():
                if not isinstance(value, basestring):
                    continue

                key_infos = KEYWORD_PATTERN.findall(value)

                for key_info in key_infos:
                    key_string = key_info[0]
                    key = key_info[1]
                    key_value = parameters.get(key)

                    if key_value:
                        value = value.replace(key_string, key_value)
                
                parameters[name] = value

        return parameters
        
    def set_parameters(self, **parameters):
        '''
        このオブジェクトにパラメータを設定する
        '''
        self.__parameters.update(parameters)

    @classmethod
    def get_doc(self, first_line_only=False):
        '''
        タスクを説明する文字列を取得する
        基本このクラスの__doc__アトリビュートを使用する
        別の説明を使用したい場合はこのメソッドをオーバーライドする
        '''
        doc = self.__doc__

        if not doc:
            doc = 'No description...'

        lines = doc.split('\n')
        lines_ = []

        for line in lines:
            line = line.strip(' ')

            if not line:
                continue

            lines_.append(line)

        if first_line_only:
            return lines_[0]

        return '\n'.join(lines_)

    def get_name(self):
        return type(self).__name__

    def get_active(self):
        '''
        このタスクを実行するかどうかを返す
        '''
        return self.__active

    def set_active(self, active):
        '''
        このタスクを実行するかどうかを設定する
        '''
        self.__active = active
        
    def execute_if_active(self):
        '''
        get_activeの戻り値がTrueの場合のみ実行する
        '''
        if not self.__active:
            return 
            
        try:
            self.__emitter.execute_start.emit()
            rtn = self.execute()
            self.__emitter.executed.emit()
            return rtn

        except:
            err_msg = traceback.format_exc().strip('\n')
            type_, value, traceback_ = sys.exc_info()
            match = ERROR_PATTERN.match(err_msg)
            err_msg = match.group('main_err')

            # TaskStackWarningの場合はwarning_raisedシグナルを発信してスルー
            if type_ == TaskStackWarning:
                print(err_msg)
                self.__emitter.warning_raised.emit(err_msg)

            # それ以外(TaskStackError含む)の場合はerror_raisedシグナルを発信して処理を止める
            else:
                self.__emitter.error_raised.emit(err_msg)
                raise


    def undo_if_active(self):
        '''
        get_activeの戻り値がTrueの場合のみUndoする
        '''
        if not self.__active:
            return 

        return self.undo()

    def _raise_error(self, message, exception=TaskStackError):
        message = message.encode('utf-8') # 日本語も扱えるようにutf-8でエンコード

        try:
            raise exception(message)

        except:
            err_msg = traceback.format_exc().strip('\n')
            type_, value, traceback_ = sys.exc_info()
            match = ERROR_PATTERN.match(err_msg)
            err_msg = match.group('main_err')
            return err_msg

    def raise_error(self, message='Error', exception=TaskStackError):
        err_msg = self._raise_error(message, exception)
        self.__emitter.error_raised.emit(err_msg)
        raise TaskStackError(err_msg)

    def raise_warning(self, message='Warning', exception=TaskStackWarning):
        err_msg = self._raise_error(message, exception)
        print('# {}'.format(err_msg))
        self.__emitter.warning_raised.emit(err_msg)

