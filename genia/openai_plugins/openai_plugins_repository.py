import json
import logging
import os

import jsonref
import requests
import yaml


class OpenAIPluginsRepository:
    HUB_URL_EXAMPLE = "https://www.plugnplai.com/_functions/getUrls"
    manifests = []

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            # cls._instance.embeddings = kwargs.get('param1')
        return cls._instance

    # https://chat-calculator-plugin.supportmirage.repl.co/.well-known/ai-plugin.json
    #
    def __init__(self, base_url=HUB_URL_EXAMPLE):
        plugins_urls = self.get_all_plugins(base_url)
        logging.info(plugins_urls)
        filtered_urls = (
            "https://slack.com",
            # "https://zapier.com",
        )
        self.manifests_specs = [self.get_spec_from_url(item) for item in plugins_urls if item in filtered_urls]
        self.tools = [self.extract_all_parameters(manifest_spec[1]) for manifest_spec in self.manifests_specs]

    def requests(self, url: str, timeout=5):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # Raises stored HTTPError, if one occurred.
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("Something went wrong", err)
            return None
        return response

    def get_spec_from_url(self, url):
        manifest = self.get_plugin_manifest(url)
        openapi_spec = self.get_openapi_spec(self.get_openapi_url(url, manifest))
        logging.debug(openapi_spec)
        return manifest, openapi_spec

    def get_plugin_manifest(self, url: str):
        urlJson = os.path.join(url, ".well-known/ai-plugin.json")
        response = self.requests(urlJson)
        return response.json()

    def get_all_plugins(self, base_url):
        try:
            response = requests.get(base_url)
            # Check if the response status code is successful (200 OK)
            if response.status_code == 200:
                # Parse the JSON response
                return response.json()
            elif response.status_code in [400, 500]:
                # Handle unsuccessful responses
                return response.json()  # Assuming the API returns error info in JSON format
            else:
                # Handle other potential status codes
                return f"An error occurred: {response.status_code} {response.reason}"
        except requests.exceptions.RequestException as e:
            return str(e)

    def is_partial_url(self, url, openapi_url):
        if openapi_url.startswith("/"):
            # remove slash in the end of url if present
            url = url.strip("/")
            openapi_url = url + openapi_url
        elif "localhost" in openapi_url:
            openapi_url = "/" + openapi_url.split("/")[-1]
            return self._is_partial_url(url, openapi_url)
        return openapi_url

    def get_openapi_url(self, url, manifest):
        openapi_url = manifest["api"]["url"]
        return self.is_partial_url(url, openapi_url)

    def get_openapi_spec(self, openapi_url):
        openapi_spec_str = self.requests(openapi_url, timeout=20).text
        try:
            openapi_spec = json.loads(openapi_spec_str)
        except json.JSONDecodeError:
            openapi_spec = yaml.safe_load(openapi_spec_str)

        # Use jsonref to resolve references
        resolved_openapi_spec = jsonref.JsonRef.replace_refs(openapi_spec)
        return resolved_openapi_spec

    def extract_parameters(self, openapi_spec, path, method):
        parameters = {"required": []}

        # Extract path parameters and query parameters
        if "parameters" in openapi_spec["paths"][path][method]:
            for param in openapi_spec["paths"][path][method]["parameters"]:
                param_name = param["name"]
                # param_type = param["in"]  # e.g., 'path', 'query', 'header'
                parameters[param_name] = {
                    "type": param["schema"]["type"],
                    "description": param.get("description", param["schema"]["title"]),
                }
                if param["required"]:
                    parameters["required"].append(param_name)

        # Extract request body properties
        if "requestBody" in openapi_spec["paths"][path][method]:
            content = openapi_spec["paths"][path][method]["requestBody"]["content"]
            if "application/json" in content:
                json_schema = content["application/json"]["schema"]
                if "properties" in json_schema:
                    for prop_name, prop_schema in json_schema["properties"].items():
                        parameters[prop_name] = {"type": "body", "schema": prop_schema}

        return parameters

    def extract_all_parameters(self, openapi_spec):
        all_parameters = {}

        # Mapping of long type names to short names
        type_shorteners = {
            "string": "str",
            "integer": "int",
            "boolean": "bool",
            "number": "num",
            "array": "arr",
            "object": "obj",
        }

        # Iterate over all paths in the specification
        for path, path_item in openapi_spec["paths"].items():
            # Iterate over all methods (e.g., 'get', 'post', 'put') in the path item
            for method, operation in path_item.items():
                # Skip non-method keys such as 'parameters' that can be present in the path item
                if method not in [
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "options",
                    "head",
                    "trace",
                ]:
                    continue

                # Extract the operation ID
                operation_id = operation.get("operationId", f"{method}_{path}")

                # Extract the summary, or use an empty string if it doesn't exist
                summary = operation.get("summary", "")
                description = operation.get("description", summary)

                # Extract parameters for the current operation
                parameters = self.extract_parameters(openapi_spec, path, method)

                # Shorten the types in the parameters dictionary
                for param_info in parameters.values():
                    param_type = param_info["schema"].get("type")
                    if param_type in type_shorteners:
                        param_info["schema"]["type"] = type_shorteners[param_type]

                # Add the extracted information to the dictionary with the operation ID as the key
                all_parameters[operation_id] = {
                    "name": operation_id,
                    "description": description,
                    "path": path,
                    "method": method,
                    "parameters": {"type": "object", "properties": parameters},
                }

                # {
                #     "name": "get_all_available_skills",
                #     "description": "fetch all available skills/functions for the AI assistant to be used. this tool should be used when the user asks for the list of tools/functions/skills supported.",
                #     "parameters": {
                #         "type": "object",
                #         "properties": {
                #             "filter": {
                #                 "type": "string",
                #                 "description": "a filter natural language text to filter the list of skills"
                #             }
                #         },
                #         "required": []
                #     }
                # }

        return all_parameters

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            raise ValueError("Singleton instance not yet created")
        return cls._instance


class llm_function_repository_as_a_function:
    def find_all_skills(self, filter=""):
        return ""
