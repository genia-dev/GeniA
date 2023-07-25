import logging
import threading

from genia.conversation.llm_conversation import (
    LLMConversationRepository,
    LLMConversation,
)


class ThreadSafeDictionary:
    def __init__(self):
        self._dictionary = {}
        self._lock = threading.Lock()

    def __getitem__(self, key):
        with self._lock:
            return self._dictionary[key]

    def __setitem__(self, key, value):
        with self._lock:
            self._dictionary[key] = value

    def __delitem__(self, key):
        with self._lock:
            del self._dictionary[key]

    def __len__(self):
        with self._lock:
            return len(self._dictionary)

    def __contains__(self, key):
        with self._lock:
            return key in self._dictionary

    def get(self, key, default=None):
        with self._lock:
            return self._dictionary.get(key, default)

    def keys(self):
        with self._lock:
            return list(self._dictionary.keys())

    def values(self):
        with self._lock:
            return list(self._dictionary.values())

    def items(self):
        with self._lock:
            return list(self._dictionary.items())

    def update_with_lambda(self, key, value, function):
        with self._lock:
            function(key, self._dictionary.get(key), value)
            self._dictionary[key] = value


class LLMConversationInMemRepository(LLMConversationRepository):
    logger = logging.getLogger(__name__)

    _conversations_db: ThreadSafeDictionary
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, conversations_db=ThreadSafeDictionary()):
        self._conversations_db = conversations_db

    def find_conversation_by_id(self, uid: str):
        return self._conversations_db.get(uid)

    def update_conversation(self, llm_conversation: LLMConversation):
        self._conversations_db.update_with_lambda(
            llm_conversation.get_id(),
            llm_conversation,
            self._update_with_optimitic_lock,
        )

    def _update_with_optimitic_lock(
        self, uid, old_chat: LLMConversation, llm_conversation: LLMConversation
    ):
        if old_chat is None or llm_conversation.get_version() == old_chat.get_version():
            llm_conversation.increment_version()
        else:
            raise ValueError(
                "current stored version does not match the new value. new: %s, old: %s",
                llm_conversation,
                old_chat,
            )
