import logging

import requests
from traitlets import Any

from genia.llm_function.llm_function import LLMFunction


class URLFunction(LLMFunction):
    logger = logging.getLogger(__name__)

    def evaluate(self, function_config: dict, parameters: dict) -> Any:
        return requests.get(self.format_url(function_config, parameters)).json()

    def format_url(self, function_config: dict, parameters: dict = {}):
        url = function_config["template"]
        if len(parameters) > 0:
            formatted_url = url.format(**parameters)
        else:
            formatted_url = url
        self.logger.debug(formatted_url)
        return formatted_url
