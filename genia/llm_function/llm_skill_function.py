import logging

from traitlets import Any

from genia.llm_function.llm_function import LLMFunction
from genia.llm_function.llm_function_repository import LLMFunctionRepository
from genia.settings_loader import settings


class SkillFunction(LLMFunction):
    logger = logging.getLogger(__name__)

    _function_repository: LLMFunctionRepository

    def __init__(self, function_repository: LLMFunctionRepository):
        self._function_repository = function_repository

    def evaluate(self, function_config: dict, parameters: dict) -> Any:
        skill = self._function_repository.find_skill_by_name(function_config["tool_name"])
        response = settings["skill_template_prompt"]["template"].format(skill=skill)
        return response
