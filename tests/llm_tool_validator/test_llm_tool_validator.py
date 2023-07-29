import unittest
from unittest.mock import Mock

from genia.conversation.llm_conversation import (LLMConversation,
                                                 LLMConversationRepository,
                                                 LLMConversationService)
from genia.conversation.llm_conversation_in_memory_repository import LLMConversationInMemRepository
from genia.llm_function.llm_function_repository import LLMFunctionRepository
from genia.tool_validators.llm_tool_validator import LLMToolValidator


class TestLLMToolValidator(unittest.TestCase):
    def setUp(self):
        self._tools_validator = LLMToolValidator()
        self._llm_conversation_service = LLMConversationService(LLMConversationInMemRepository())

    def test_find_tools(self):
        # Specify the return value for the mocked method
        function_repository = Mock(spec=LLMFunctionRepository)
        function_repository.find_tool_by_name.return_value = {"category": "python"}
        conversation_messages = [
            {"role": "assistant", "content": None, "function_call": {...}},
            {"role": "user", "content": "yes"},
            {
                "role": "assistant",
                "content": "I must confirm with you before i am allowed to proceed calling function revoke_production_permissions",
                "validation": "find_tools",
            },
            {"role": "user", "content": "find tools"},
        ]
        conversation: LLMConversation = LLMConversation(0, 0, conversation_messages)
        self.assertFalse(self._tools_validator._is_within_skill_function_chain(
            self._llm_conversation_service, function_repository, conversation
        ))

    def test_chat(self):
        function_repository = Mock(spec=LLMFunctionRepository)
        conversation_messages = [
            {"role": "user", "content": "hi"}
        ]
        conversation: LLMConversation = LLMConversation(0, 0, conversation_messages)
        self.assertFalse(self._tools_validator._is_within_skill_function_chain(
            self._llm_conversation_service, function_repository, conversation
        ))

    def test_revoke_permissions(self):
        # Specify the return value for the mocked method
        function_repository = Mock(spec=LLMFunctionRepository)
        function_repository.find_tool_by_name.return_value = {"category": "skill"}
        conversation_messages = [
            {
                "role": "function",
                "name": "get_top_available_tools",
            },
            {"role": "assistant", "content": None, "function_call": {...}},
            {
                "role": "function",
                "name": "revoke_production_permissions",
            },
            {"role": "assistant", "content": None, "function_call": {...}},
            {"role": "user", "content": "yes"},
            {
                "role": "assistant",
                "content": "I must confirm with you before i am allowed to proceed calling function revoke_production_permissions",
                "validation": "revoke_production_permissions",
            },
            {"role": "user", "content": "now revoke those permissions"},
            {
                "role": "assistant",
                "content": "I have successfully granted the user 'shlomsh' production permissions by adding them to the 'production-shift-group' IAM group. The user now has temporary credentials for production access.",
            },
            {"role": "function", "name": "add_user_to_group", "content": "None"},
            {"role": "assistant", "content": None, "function_call": {...}},
            {
                "role": "function",
                "name": "get_top_available_tools",
            },
            {"role": "assistant", "content": None, "function_call": {...}},
            {
                "role": "function",
                "name": "grant_production_permissions",
            },
            {"role": "assistant", "content": None, "function_call": {...}},
        ]
        conversation: LLMConversation = LLMConversation(0, 0, conversation_messages)
        self.assertTrue(self._tools_validator._is_within_skill_function_chain(
            self._llm_conversation_service, function_repository, conversation
        ))

if __name__ == "__main__":
    unittest.main()
