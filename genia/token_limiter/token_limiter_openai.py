import json
import logging
import tiktoken
from genia.settings_loader import settings
from abc import ABC, abstractmethod


class TokenLimiter(ABC):
    @abstractmethod
    def has_limit_reached(self, model: str, messages, functions):
        pass

    @abstractmethod
    def limit_function_response_tokens(self, function_response):
        pass


class TokenLimiterOpenAI(TokenLimiter):
    logger = logging.getLogger(__name__)

    MAX_TOKENS = {
        "gpt-3.5-turbo": 4000,
        "gpt-3.5-turbo-0613": 4000,
        "gpt-3.5-turbo-0301": 4000,
        "gpt-3.5-turbo-16k": 16000,
        "gpt-3.5-turbo-16k-0613": 16000,
        "gpt-4": 8000,
        "gpt-4-0613": 8000,
        "gpt-4-32k": 32000,
    }

    def has_limit_reached(self, model: str, messages, functions):
        num_tokens = self.num_tokens_from_messages(messages, model)
        num_tokens += self.num_tokens_from_functions(functions, model)
        self.logger.debug("calculated number of tokens: %s", num_tokens)
        return num_tokens > min(
            settings.chat.max_chat_tokens,
            self.MAX_TOKENS.get(model, settings.chat.max_chat_tokens),
        )

    def limit_function_response_tokens(self, function_response):
        if len(function_response) > settings.chat.max_chat_function_len:
            self.logger.warning(
                "maximum len of function response, trimming the data: %s",
                function_response,
            )
        return function_response[: settings.chat.max_chat_function_len]

    def num_tokens_from_messages(self, messages, model: str):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
        }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                try:
                    if value != None:
                        if type(value) == str:
                            value_len = len(encoding.encode(value))
                        elif type(value) == dict:
                            value_len = len(encoding.encode(json.dumps(value)))
                        else:
                            value_len = len(encoding.encode(str(value)))
                except Exception as e:
                    self.logger.error("failed encoding key=%s value=%s, %s", key, str(value), str(e))
                    value_len = 0.75 * len(str(value))
                num_tokens += value_len
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def num_tokens_from_functions(self, functions, model):
        """Return the number of tokens used by a list of functions.
        https://community.openai.com/t/how-to-calculate-the-tokens-when-using-function-call/266573/11
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        num_tokens = 0
        for function in functions:
            function_tokens = len(encoding.encode(function["name"]))
            function_tokens += len(encoding.encode(function["description"]))

            if "parameters" in function:
                parameters = function["parameters"]
                if "properties" in parameters:
                    for propertiesKey in parameters["properties"]:
                        function_tokens += len(encoding.encode(propertiesKey))
                        v = parameters["properties"][propertiesKey]
                        for field in v:
                            if field == "type":
                                function_tokens += 2
                                function_tokens += len(encoding.encode(v["type"]))
                            elif field == "description":
                                function_tokens += 2
                                function_tokens += len(encoding.encode(v["description"]))
                            elif field == "enum":
                                function_tokens -= 3
                                for o in v["enum"]:
                                    function_tokens += 3
                                    function_tokens += len(encoding.encode(o))
                            else:
                                print(f"Warning: not supported field {field}")
                    function_tokens += 11

            num_tokens += function_tokens

        num_tokens += 12
        return num_tokens
