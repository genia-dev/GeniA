from collections import deque
import json
import logging
import re

from traitlets import Any
from genia.agents.open_ai import OpenAIToolsEmpoweredAgent
from genia.conversation.llm_conversation import LLMConversation

from genia.llm_function.llm_function import LLMFunction
from genia.llm_function.llm_function_repository import LLMFunctionRepository
from genia.llm_function.llm_skill_function import SkillFunction
from genia.llm_function.open_api_function import OpenApiFunction
from genia.llm_function.python_function import PythonFunction
from genia.llm_function.url_function import URLFunction
from genia.llm_function_lookup_strategy.llm_function_lookup_strategy import LLMFunctionLookupStrategy
from genia.settings_loader import settings
from genia.utils.utils import safe_loads


class AgentSkillFunction(LLMFunction):
    logger = logging.getLogger(__name__)

    _function_repository: LLMFunctionRepository
    _llm_conversation: LLMConversation
    _function_lookup_strategy: LLMFunctionLookupStrategy
    _agent: OpenAIToolsEmpoweredAgent

    def __init__(
        self,
        function_repository: LLMFunctionRepository,
        llm_conversation: LLMConversation,
        function_lookup_strategy: LLMFunctionLookupStrategy,
        agent: OpenAIToolsEmpoweredAgent,
    ):
        self._function_repository = function_repository
        self._llm_conversation = llm_conversation
        self._function_lookup_strategy = function_lookup_strategy
        self._agent = agent

    def evaluate(self, function_config: dict, parameters: dict) -> Any:
        tool_name = function_config["tool_name"]
        # i.e agent: SRE
        agent_name = function_config["agent"]
        self.logger.debug(f"AgentSkillFunction: {agent_name} {tool_name}")
        agents_ctx = []
        tasks_list = deque()

        new_tasks = self.planner_agent(tool_name, agent_name)
        for new_task in new_tasks:
            task_parts = new_task["task"].strip().split(".", 1)
            if len(task_parts) == 2:
                task_id = task_parts[0].strip()
                task_name = task_parts[1].strip()
                tasks_list.append({"task_id": task_id, "task": task_name})

        while len(tasks_list) > 0:
            new_task = tasks_list.popleft()
            # Send to execution function to complete the task based on the context
            agents_ctx.append({"role": "user", "content": new_task["task"]})
            if len(tasks_list) > 0:
                result = self.execution_agent(agents_ctx, agent_name)
            else:
                result = self.execution_agent(agents_ctx, agent_name)
            agents_ctx.append({"role": "assistant", "content": result})

        return result

    def execution_agent(self, agents_ctx, agent_name):
        messages = []
        execution_agent_prompt = settings["execution_agent_prompt"]["system"]
        if settings[agent_name + "_agent_prompt"] is not None:
            messages.append({"role": "system", "content": settings[agent_name + "_agent_prompt"]["system"]})

        messages.append({"role": "system", "content": execution_agent_prompt})
        messages.extend(agents_ctx)

        functions = self._function_lookup_strategy.find_potential_tools(self._llm_conversation)
        return self.call_model(messages, functions, "auto")

    def call_model(self, messages, functions, mode):
        for _ in range(settings["chat"]["max_function_chain_length"]):
            response = self._agent.call_model(messages, functions, "auto")
            message = response["choices"][0]["message"]
            finish_reason = response["choices"][0]["finish_reason"]

            if finish_reason == "stop":
                return message["content"]

            elif finish_reason == "function_call":
                function_name = message["function_call"]["name"]
                function_arguments = safe_loads(message["function_call"]["arguments"])
                self.logger.debug(
                    "the model decided to call the function: %s, with parameters: %s",
                    function_name,
                    function_arguments,
                )
                try:
                    llm_matching_tool = self._function_repository.find_tool_by_name(function_name)
                    if llm_matching_tool is None:
                        raise ValueError("function {} doesn't exist".format(llm_matching_tool))
                    self.logger.debug("found the tool: %s", llm_matching_tool)
                    function_response = self.llm_function_call(
                        messages,
                        function_name,
                        function_arguments,
                        llm_matching_tool,
                    )
                except Exception as e:
                    function_response = str(e)
                    self.logger.exception(
                        "Error executing function=%s, parameters=%s, error=%s",
                        function_name,
                        function_arguments,
                        function_response,
                    )

                self.logger.debug("function response: %s", function_response)
                messages.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": str(function_response),
                    }
                )

    def llm_function_call(self, messages, function_name, function_arguments, llm_matching_tool):
        messages.append(
            {
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": function_name,
                    "arguments": json.dumps(function_arguments),
                },
            }
        )
        llm_function = self.create_function(llm_matching_tool.get("category"))
        return str(llm_function.evaluate(llm_matching_tool, function_arguments))

    def create_function(self, category: str) -> LLMFunction:
        self.logger.debug("create_function with category: %s", category)
        lower_category = category.lower()
        if lower_category == "url":
            fun = URLFunction()
        elif lower_category == "python":
            fun = PythonFunction()
        elif lower_category == "open_api":
            fun = OpenApiFunction()
        elif lower_category == "skill":
            fun = SkillFunction(self._function_repository)
        else:
            raise ValueError("category is not supported:" + category)
        return fun

    def planner_agent(self, tool_name, agent_name):
        skill = self._function_repository.find_skill_by_name(tool_name)
        planner_agent_prompt = settings["planner_agent_prompt"]["system"]
        if settings[agent_name + "_agent_prompt"] is not None:
            special_agent_prompt = settings[agent_name + "_agent_prompt"]["system"]
        else:
            special_agent_prompt = settings["agent_prompt"]["system"]
        messages = [
            {"role": "system", "content": special_agent_prompt},
            {"role": "system", "content": planner_agent_prompt},
        ]

        messages.extend(
            [
                {"role": "user", "content": item["content"]}
                for item in self._llm_conversation.get_messages()
                if item["role"] == "user" and item["content"] != "yes"
            ]
        )
        messages.extend([{"role": "user", "content": skill}])

        functions = self._function_lookup_strategy.find_potential_tools(self._llm_conversation)
        model_response = self._agent.call_model(messages, functions, "none")
        model_response_txt = model_response["choices"][0]["message"]["content"]
        self.logger.debug(model_response_txt)

        tasks = model_response_txt.strip().split("\n")
        # tasks = re.split(r'\n(?=\d+\.)', model_response_txt.strip())

        final_tasks = []
        # Iterate through the lines and append non-numbered lines to the previous line
        for line in tasks:
            line = line.strip()
            if line and not line[0].isdigit():
                if final_tasks:
                    final_tasks[-1] += "\n" + line
            else:
                final_tasks.append(line)

        return [{"task": task} for task in final_tasks if re.match(r"^\d+\.", task)]
