import logging
from typing import Dict

from genia.conversation.llm_conversation import LLMConversationService, LLMConversation
from genia.llm_function.llm_function_repository import LLMFunctionRepository
from genia.settings_loader import settings


class LLMToolValidator:
    logger = logging.getLogger(__name__)

    def is_tool_validation_required(
        self,
        llm_conversation_service: LLMConversationService,
        llm_functions_repository: LLMFunctionRepository,
        llm_tool,
        function_arguments: Dict,
        llm_conversation: LLMConversation,
    ):
        return (
            settings.chat.programmatic_user_tool_validation_required
            and llm_tool.get("validate", True)
            and not self._was_this_function_call_just_confirmed_already(
                llm_conversation_service, llm_tool, function_arguments, llm_conversation
            )
            and not self._is_within_skill_function_chain(
                llm_conversation_service, llm_functions_repository, llm_conversation
            )
        )

    def _was_this_function_call_just_confirmed_already(
        self, llm_conversation_service: LLMConversationService, llm_tool, function_arguments: Dict, llm_conversation
    ):
        return llm_conversation_service.get_last_function_call(llm_conversation) == llm_tool["tool_name"]

    def _is_within_skill_function_chain(
        self,
        llm_conversation_service: LLMConversationService,
        llm_functions_repository: LLMFunctionRepository,
        llm_conversation,
    ) -> bool:
        return llm_conversation_service.is_within_skill_function_chain(llm_functions_repository, llm_conversation)

    def validate_tool_usage(
        self,
        llm_conversation_service: LLMConversationService,
        llm_conversation: LLMConversation,
        function_arguments,
        llm_tool,
    ):
        user_response = settings.agent_prompt.user_validation_message.format(function_title=llm_tool["title"])
        model_response = settings.agent_prompt.model_validation_message.format(function_name=llm_tool["tool_name"])
        params_list = []
        if len(function_arguments) > 0:
            user_response += " with the following parameters?\n"
            for key, value in function_arguments.items():
                params_list.append(key.replace("_", " ") + " - " + str(value))
            user_response += "\n".join(params_list)
        else:
            user_response += "?"

        llm_conversation_service.add_assistant_validation_message(
            llm_conversation, model_response, llm_tool["tool_name"]
        )
        return user_response
