from bert2tf import Model, Executor
from tests import Bert2TFTestCase


class MyTestCase(Bert2TFTestCase):

    def test_create_base_executor(self):
        executor = Executor.load_config('yaml/base_executor.yml')
        self.assertEqual(isinstance(executor, Executor), True)

        executor = Executor.load_config('BaseExecutor')
        self.assertEqual(isinstance(executor, Executor), True)

    def test_create_base_model(self):
        model = Executor.load_config('yaml/base_model.yml')
        self.assertEqual(isinstance(model, Model), True)

        model = Executor.load_config('BaseModel')
        self.assertEqual(isinstance(model, Model), True)

    def test_py_modules_executor(self):
        executor = Executor.load_config(use='MyExecutor', metas={'py_modules': 'myexecutor.py'})
        self.assertEqual(isinstance(executor, Executor), True)
