from abc import ABC, abstractmethod
from genia.conversation.llm_conversation import LLMConversationService, LLMConversation

from genia.llm_function.llm_function_repository import LLMFunctionRepository


class LLMFunctionLookupStrategy(ABC):
    _llm_conversation_service: LLMConversationService
    _llm_functions_repository: LLMFunctionRepository

    def __init__(
        self,
        llm_conversation_service: LLMConversationService,
        llm_functions_repository: LLMFunctionRepository,
    ):
        self._llm_conversation_service = llm_conversation_service
        self._llm_functions_repository = llm_functions_repository

    @abstractmethod
    def find_potential_tools(self, llm_conversation: LLMConversation):
        pass


class LLMFunctionLookupStrategyLastUserAll(LLMFunctionLookupStrategy):
    def find_potential_tools(self, llm_conversation: LLMConversation):
        last_function_calls = self._llm_conversation_service.get_previous_function_calls(llm_conversation)
        # _take_k_or_less last_function_calls
        user_messages = self._llm_conversation_service.get_user_messages(llm_conversation, 5)
        assistant_messages = self._llm_conversation_service.get_assistant_messages(llm_conversation, 5)

        # top 3 tools for last user message
        last_user_similarities = self._llm_functions_repository.similarity_search_with_score(user_messages[-1], 3)
        all_user_similarities = self._llm_functions_repository.similarity_search_with_score(
            ".\n".join(user_messages), 5
        )
        if len(assistant_messages) > 0:
            all_assistant_similarities = self._llm_functions_repository.similarity_search_with_score(
                ";\n\n".join(assistant_messages), 5
            )
        else:
            all_assistant_similarities = []

        # self.logger.debug("found the most similar tools with the following distances: %s", list(map(lambda item: item[1], most_similar_document_tools)))
        tools_list = list(map(lambda item: [item[0].metadata, item[1]], last_user_similarities))
        tools_list.extend(self._filtered_ordered_list(all_user_similarities, 0.5))
        tools_list.extend(self._filtered_ordered_list(all_assistant_similarities, 0.5))
        model_functions = self._llm_functions_repository.find_tools(last_function_calls, tools_list)
        llm_conversation.set_model_functions(model_functions)
        return list(map(lambda obj: obj[0], model_functions))

    def _filtered_ordered_list(self, input_list, threshold):
        return [[item[0].metadata, item[1]] for item in input_list if item[1] < threshold]
