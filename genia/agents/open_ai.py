import logging
import os

import openai
from openai.error import APIConnectionError, APIError, Timeout, TryAgain
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from genia.agents.agent import Agent
from genia.settings_loader import settings


class OpenAIAgent(Agent):
    logger = logging.getLogger(__name__)

    def __init__(self, model=settings["openai"]["OPENAI_MODEL"]):
        self._model = model

    @retry(
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((Timeout, TryAgain, APIError, APIConnectionError)),
    )
    def call_model(self, messages, functions, function_call):
        try:
            params = {
                "temperature": settings["openai"]["temperature"],
                "messages": messages,
                "request_timeout": settings["openai"]["timeout"],
            }
            if len(functions) > 0:
                params["functions"] = functions
                params["function_call"] = function_call

            self.logger.debug("calling the model")

            if os.getenv("OPENAI_API_TYPE") == "azure":
                params["engine"] = os.getenv("OPENAI_API_DEPLOYMENT")
            else:
                params["model"] = self._model

            return openai.ChatCompletion.create(**params)

        except Exception as e:
            self.logger.error("call model error %s", str(e))
            raise e
