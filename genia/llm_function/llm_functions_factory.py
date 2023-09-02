import logging
from genia.agents.agent import Agent
from genia.conversation.llm_conversation import LLMConversation
from genia.llm_function.agent_skill_function import AgentSkillFunction

from genia.llm_function.llm_function import LLMFunction
from genia.llm_function.llm_function_repository import LLMFunctionRepository
from genia.llm_function.llm_skill_function import SkillFunction
from genia.llm_function.open_api_function import OpenApiFunction
from genia.llm_function.python_function import PythonFunction
from genia.llm_function.url_function import URLFunction
from genia.llm_function_lookup_strategy.llm_function_lookup_strategy import LLMFunctionLookupStrategy


class LLMFunctionFactory:
    logger = logging.getLogger(__name__)

    _agent: Agent

    def __init__(
        self,
        agent: Agent = None,
    ):
        self._agent = agent

    def create_function(
        self,
        category: str,
        function_repository: LLMFunctionRepository,
        llm_conversation: LLMConversation = None,
        function_lookup_strategy: LLMFunctionLookupStrategy = None,
    ) -> LLMFunction:
        self.logger.debug("create_function with category: %s", category)
        lower_category = category.lower()
        if lower_category == "url":
            fun = URLFunction()
        elif lower_category == "python":
            fun = PythonFunction()
        elif lower_category == "open_api":
            fun = OpenApiFunction()
        elif lower_category == "skill":
            fun = SkillFunction(function_repository)
        elif lower_category == "agent_skill":
            fun = AgentSkillFunction(
                function_repository, llm_conversation, function_lookup_strategy, self._agent
            )
        else:
            raise ValueError("category is not supported:" + category)
        return fun
