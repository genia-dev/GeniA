from abc import ABC


class Agent(ABC):
    def process_message(self, user_message, uid, **kwargs):
        pass
