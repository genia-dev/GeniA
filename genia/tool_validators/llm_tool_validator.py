import logging

from genia.conversation.llm_conversation import LLMConversationService, LLMConversation
from genia.settings_loader import settings


class LLMToolValidator:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self._validation_messgae = (
            settings.agent_prompt.user_validation_title + "\n" + settings.agent_prompt.user_validation_message
        )

    def is_tool_validation_required(
        self,
        llm_conversation_service: LLMConversationService,
        llm_tool,
        function_arguments,
        llm_conversation: LLMConversation,
    ):
        return (
            settings.chat.programmatic_user_tool_validation_required
            and llm_tool.get("validate", True)
            and llm_conversation_service.get_last_function_call(llm_conversation) != llm_tool["tool_name"]
        )

    def validate_tool_usage(
        self,
        llm_conversation_service: LLMConversationService,
        llm_conversation: LLMConversation,
        function_arguments,
        llm_tool,
    ):
        response = self._validation_messgae.format(function_title=llm_tool["title"])
        params_list = []
        if len(function_arguments) > 0:
            response += " with the following parameters?\n"
            for key, value in function_arguments.items():
                params_list.append(key.replace("_", " ") + " - " + str(value))

        response += "\n".join(params_list)
        llm_conversation_service.add_assistant_validation_message(llm_conversation, response, llm_tool["tool_name"])
        return response
