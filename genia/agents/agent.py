from abc import ABC, abstractmethod


class Agent(ABC):
    @abstractmethod
    def process_message(self, user_message, uid, **kwargs):
        pass
