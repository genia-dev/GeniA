import logging

from genia.conversation.llm_conversation import LLMConversationService, LLMConversation
from genia.settings_loader import settings


class LLMToolValidator:
    logger = logging.getLogger(__name__)

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
