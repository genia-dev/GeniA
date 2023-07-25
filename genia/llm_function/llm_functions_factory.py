import logging

from genia.llm_function.llm_function import LLMFunction
from genia.llm_function.llm_function_repository import LLMFunctionRepository
from genia.llm_function.llm_skill_function import SkillFunction
from genia.llm_function.open_api_function import OpenApiFunction
from genia.llm_function.python_function import PythonFunction
from genia.llm_function.url_function import URLFunction


class LLMFunctionFactory:
    logger = logging.getLogger(__name__)

    def create_function(self, category: str, function_repository: LLMFunctionRepository) -> LLMFunction:
        self.logger.debug("create_function with category: %s", category)
        if category.lower() == "url":
            fun = URLFunction()
        elif category.lower() == "python":
            fun = PythonFunction()
        elif category.lower() == "open_api":
            fun = OpenApiFunction()
        elif category.lower() == "skill":
            fun = SkillFunction(function_repository)
        else:
            raise ValueError("category is not supported:" + category)
        return fun
