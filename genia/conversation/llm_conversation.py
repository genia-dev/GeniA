import json
import logging
from abc import ABC, abstractmethod
from typing import List, Set

from termcolor import colored

from genia.llm_function.llm_function_repository import LLMFunctionRepository
from genia.settings_loader import settings


class LLMConversation:
    _uid: str
    _version: int
    _conversation_messages: List
    _model_functions: List

    def __init__(self, uid, version: int = 0, conversation_messages: List = list()):
        self._uid = uid
        self._version = version
        self._conversation_messages = conversation_messages

    def get_id(self) -> str:
        return self._uid

    def len(self):
        len(self._conversation_messages)

    def clear(self) -> None:
        self._conversation_messages.clear()

    def get_messages(self) -> List:
        # return a shallow copy to avoid internal changes by reference
        return self._conversation_messages[::]

    def append(self, message):
        self._conversation_messages.append(message)

    def slice(self, start):
        self._conversation_messages = self._conversation_messages[start:]

    def get_model_functions(self) -> List:
        return self._model_functions[::]

    def set_model_functions(self, model_functions: List):
        self._model_functions = model_functions

    def increment_version(self):
        self._version += 1

    def get_version(self):
        return self._version


class LLMConversationRepository(ABC):
    @abstractmethod
    def find_conversation_by_id(self, uid) -> LLMConversation:
        pass

    @abstractmethod
    def update_conversation(self, llm_conversation: LLMConversation):
        pass


class LLMConversationService:
    logger = logging.getLogger(__name__)
    _conversation_repository: LLMConversationRepository

    def __init__(self, conversation_repository: LLMConversationRepository):
        self._conversation_repository = conversation_repository
        self._max_chain_length = min(
            settings["tools_similarity"]["size_of_all_tools_request"],
            settings["chat"]["max_user_message_chain"],
        )

    def find_conversation_by_id(self, uid) -> LLMConversation:
        llm_conversation = self._conversation_repository.find_conversation_by_id(uid)
        if llm_conversation is None:
            llm_conversation = LLMConversation(uid)
        return llm_conversation

    def persist(self, llm_conversation: LLMConversation):
        self._conversation_repository.update_conversation(llm_conversation)

    def handle_context_too_long(self, llm_conversation: LLMConversation):
        self.shorten_conversation(llm_conversation)

    def add_system_message(self, llm_conversation: LLMConversation, message):
        self._add_conversation_message(llm_conversation, {"role": "system", "content": message})

    def add_user_message(self, llm_conversation: LLMConversation, message):
        self._add_conversation_message(llm_conversation, {"role": "user", "content": message})

    def add_assistant_message(self, llm_conversation: LLMConversation, message):
        self._add_conversation_message(llm_conversation, {"role": "assistant", "content": message})

    def get_last_function_call(self, llm_conversation: LLMConversation):
        messages_reverse = llm_conversation.get_messages()[::-1]
        res = None
        for msg in messages_reverse:
            if msg["role"] == "assistant" and msg.get("validation") is not None:
                res = msg.get("validation")
                break
            elif msg["role"] == "assistant" and msg.get("function_call") is not None:
                res = msg["function_call"].get("name")
                break
            elif msg["role"] == "function":
                res = msg.get("name")
                break
        return res

    def get_previous_function_calls(self, llm_conversation: LLMConversation) -> Set:
        messages_reverse = llm_conversation.get_messages()[::-1]

        res = set()
        for index, msg in enumerate(messages_reverse):
            if index <= self._max_chain_length:
                if msg["role"] == "assistant" and msg.get("validation") is not None:
                    res.add(msg.get("validation"))
                elif msg["role"] == "assistant" and msg.get("function_call") is not None:
                    res.add(msg["function_call"].get("name"))
                elif msg["role"] == "function":
                    res.add(msg.get("name"))
        return res

    def is_within_skill_function_chain(
        self, llm_functions_repository: LLMFunctionRepository, llm_conversation: LLMConversation
    ):
        result = False
        messages_reverse = llm_conversation.get_messages()[::-1]
        for index, msg in enumerate(messages_reverse):
            if msg["role"] == "function":
                if llm_functions_repository.find_tool_by_name(msg["name"])["category"] == "skill":
                    result = True
                    break
            elif msg["role"] == "user":
                break
        return result

    def is_concecutive_function_call(self, llm_conversation: LLMConversation):
        messages_reverse = llm_conversation.get_messages()[::-1]
        list_length = len(messages_reverse)
        length = 0
        for index, msg in enumerate(messages_reverse):
            if index < list_length - 1:
                # count user messages which are not a reply to validation request
                if msg["role"] != "user" or messages_reverse[index + 1].get("validation") is not None:
                    length += 1
                else:
                    break
        return length > 2

    def add_assistant_validation_message(self, llm_conversation: LLMConversation, message, function_name: str):
        self._add_conversation_message(
            llm_conversation,
            {"role": "assistant", "content": message, "validation": function_name},
        )

    def add_assistant_function_call_message(
        self, llm_conversation: LLMConversation, function_name: str, function_arguments
    ):
        """{
        'role': 'assistant',
        'content': None,
        'function_call': {
            'name': 'get_current_weather',
            'arguments': {
            "latitude": "32....34.7818"
            }
        }
        }"""
        self._add_conversation_message(
            llm_conversation,
            {
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": function_name,
                    "arguments": json.dumps(function_arguments),
                },
            },
        )

    def add_function_response_message(self, llm_conversation: LLMConversation, function_name, function_response):
        self._add_conversation_message(
            llm_conversation,
            {
                "role": "function",
                "name": function_name,
                "content": str(function_response),
            },
        )

    def _add_conversation_message(self, llm_conversation: LLMConversation, msg):
        messages = llm_conversation.get_messages()
        if msg is not None and self.is_message_chain_too_long(messages):
            self.shorten_conversation(llm_conversation)
        llm_conversation.append(msg)

    def is_message_chain_too_long(self, messages):
        length = 1
        for index, msg in enumerate(messages):
            # count user messages which are not a reply to validation request
            if msg["role"] == "user" and index > 0 and messages[index - 1].get("validation") is None:
                length += 1
        return length >= settings["chat"]["max_user_message_chain"]

    def shorten_conversation(self, llm_conversation: LLMConversation):
        try:
            messages = llm_conversation.get_messages()
            next_user_message_idx = len(messages)
            for index, value in enumerate(messages):
                # get non first user messages which is also not a reply to validation request
                if value["role"] == "user" and index > 0 and messages[index - 1].get("validation") is None:
                    next_user_message_idx = index
                    break
            # clear all messages befor this one
            llm_conversation.slice(next_user_message_idx)
        except Exception as e:
            self.logger.exception(str(e))
            llm_conversation.clear()

    def build_messages_for_model(self, llm_conversation: LLMConversation):
        """remove the validation key as it is not part of openai schema which is enforced"""
        messages = self.get_init_message()
        output = []
        for message in llm_conversation.get_messages():
            output.append({k: v for k, v in message.items() if k != "validation"})
        messages.extend(output)
        return messages

    def get_init_message(self):
        return [{"role": "system", "content": settings["agent_prompt"]["system"]}]

    def get_user_messages(self, llm_conversation: LLMConversation, k):
        return self._take_k_or_less(
            [item["content"] for item in llm_conversation.get_messages() if item["role"] == "user"],
            k,
        )

    def get_assistant_messages(self, llm_conversation: LLMConversation, k):
        #  (item['role'] == 'assistant' and item['content']!= None and item.get("validation") != None)], k)
        return self._take_k_or_less(
            [
                item["content"]
                for item in llm_conversation.get_messages()
                if (item["role"] == "assistant" and item["content"] is not None)
            ],
            k,
        )

    def _take_k_or_less(self, assistant_messages, k):
        return assistant_messages[:k] if len(assistant_messages) >= k else assistant_messages

    def pretty_print_conversation(self, llm_conversation: LLMConversation, logger):
        if not logger.isEnabledFor(logging.DEBUG):
            return

        role_to_color = {
            "system": "light_red",
            "user": "green",
            "assistant": "light_yellow",
            "assistant_function": "light_blue",
            "function": "magenta",
        }
        formatted_messages = []
        for message in llm_conversation.get_messages():
            if message["role"] == "assistant" and message.get("function_call"):
                formatted_messages.append(colored(message, role_to_color["assistant_function"]))
            else:
                formatted_messages.append(colored(message, role_to_color[message["role"]]))

        formatted_messages.append(colored("list of functions:", "light_cyan"))
        for index, function in enumerate(llm_conversation.get_model_functions()):
            formatted_messages.append(
                colored(
                    str(index)
                    + ". "
                    + function[0]["name"]
                    + " {"
                    + "{:.3f}".format(function[1])
                    + "}: "
                    + function[0]["description"],
                    "light_cyan",
                )
            )
        logger.debug("\n".join(formatted_messages))
