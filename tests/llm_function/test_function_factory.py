import unittest
from unittest.mock import Mock
from genia.llm_function import url_function
from genia.llm_function.llm_function_repository import LLMFunctionRepository
from genia.llm_function.llm_functions_factory import LLMFunctionFactory
from genia.llm_function.llm_skill_function import SkillFunction
from genia.llm_function.python_function import PythonFunction
from genia.llm_function.url_function import URLFunction


class TestLLMFunctionFactory(unittest.TestCase):
    factory: LLMFunctionFactory

    def setUp(self):
        self.factory = LLMFunctionFactory()
        # Create a mock instance of MyClass
        self.function_repository = Mock(spec=LLMFunctionRepository)

    def test_none(self):
        with self.assertRaises(ValueError):
            self.factory.create_function("", self.function_repository)

    def test_url(self):
        self.assertIsInstance(self.factory.create_function("url", self.function_repository), URLFunction)

    def test_url_as_default(self):
        with self.assertRaises(ValueError):
            self.factory.create_function("*", self.function_repository)

    def test_url_upper(self):
        self.assertIsInstance(self.factory.create_function("URL", self.function_repository), URLFunction)

    def test_python(self):
        self.assertIsInstance(
            self.factory.create_function("python", self.function_repository),
            PythonFunction,
        )

    def test_python_camel(self):
        self.assertIsInstance(
            self.factory.create_function("Python", self.function_repository),
            PythonFunction,
        )

    def test_skill(self):
        self.assertIsInstance(
            self.factory.create_function("skill", self.function_repository),
            SkillFunction,
        )

    def test_skill_loader(self):
        # Specify the return value for the mocked method
        self.function_repository.find_skill_by_name.return_value = "Mocked implementation"
        fun = self.factory.create_function("skill", self.function_repository)
        res = fun.evaluate({"tool_name": "test"}, {})
        self.assertIsNotNone(res)


if __name__ == "__main__":
    unittest.main()

    # Replace the original class with the mock
    # with patch('__main__.MyClass', return_value=mock_obj):
    #     result = my_function()
