import logging

from traitlets import Any
from genia.agents.open_ai import OpenAIAgent

from genia.llm_function.llm_function import LLMFunction
from genia.llm_function.llm_function_repository import LLMFunctionRepository
from genia.settings_loader import settings


class AgentSkillFunction(LLMFunction):
    logger = logging.getLogger(__name__)

    _function_repository: LLMFunctionRepository

    def __init__(self, function_repository: LLMFunctionRepository):
        self._function_repository = function_repository
        self._model = OpenAIAgent()

    def evaluate(self, function_config: dict, parameters: dict) -> Any:
        tool_name = function_config["tool_name"]
        skill = self._function_repository.find_skill_by_name(tool_name)
        # i.e agent: SRE
        agent_name = function_config["agent"]
        self.logger.debug(f"AgentSkillFunction: {agent_name} {tool_name}")
        special_agent_prompt = ""
        if settings[agent_name + "_agent_prompt"] is not None:
            special_agent_prompt = settings[agent_name + "_agent_prompt"]["system"]
        else:
            special_agent_prompt = settings["agent_prompt"]["system"]

        # planner_agent_prompt = settings["planner_agent_prompt"]["system"]
        messages = [
            {"role": "system", "content": special_agent_prompt},
            # {"role": "system", "content": planner_agent_prompt},
            {"role": "user", "content": skill},
        ]
        llm_conversation = parameters["llm_conversation"]
        function_lookup_strategy = parameters["function_lookup_strategy"]
        functions = function_lookup_strategy.find_potential_tools(llm_conversation)
        return self._model.call_model(messages, functions, "none")
