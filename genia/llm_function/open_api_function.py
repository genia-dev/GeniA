from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient

import logging
from traitlets import Any

from genia.llm_function.llm_function import LLMFunction


class OpenApiFunction(LLMFunction):
    logger = logging.getLogger(__name__)

    def evaluate(self, function_config: dict, parameters: dict) -> Any:
        swagger_url = function_config["swagger_url"]
        tag = function_config["tag"]
        function_name = function_config["function_name"]
        return self.invoke_api(swagger_url, tag, function_name, parameters)

    def invoke_api(self, swagger_url, tag, function_name, parameters) -> Any:
        # Create a RequestsClient instance to handle HTTP requests
        http_client = RequestsClient()

        # Load the Swagger file from the URL
        swagger_client = SwaggerClient.from_url(swagger_url, http_client=http_client, config={"use_models": False})

        # Get the API definition from the SwaggerClient
        tag_obj = getattr(swagger_client, tag)
        fun_obj = getattr(tag_obj, function_name)

        # Invoke the API call
        response = fun_obj(**parameters).result(timeout=4)
        self.logger.debug("API call succeeded. Result: %s", response)
        # Handle the response
        # if response.status_code == 200:
        #     result = response.response()
        #     self.logger.debug("API call succeeded. Result: %s", result)
        # else:
        #     self.logger.debug("API call failed. Status code:", response.status_code)
        return response
