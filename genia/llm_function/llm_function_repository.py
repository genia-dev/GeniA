import json
import logging
import os
import re
import threading
from typing import List, Set

from langchain.vectorstores import VectorStore

from genia.settings_loader import settings
from genia.utils.utils import (
    is_blank,
    safe_json_dump,
    safe_load_json_file,
    safe_load_yaml_file,
    safe_txt_dump,
    safe_yaml_dump,
)


class LLMFunctionRepository:
    logger = logging.getLogger(__name__)

    CORE_ROOT_PATH = "genia/tools_config"

    FUNCTIONS_EMBEDDINGS_FILE_PATH = "data/functions_embeddings"
    FUNCTIONS_EMBEDDINGS_FILE_NAME = "functions_index"

    _embeddings = None
    _llm_functions_dict: dict
    _vector_store: VectorStore
    _llm_tools_dict: dict
    _llm_skills_dict: dict

    _lock = threading.Lock()
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, embeddings, vector_store: VectorStore):
        self._embeddings = embeddings
        self._vector_store = vector_store
        # core
        core_functions_dict = self._load_functions(self.CORE_ROOT_PATH)
        core_tools_dict = self._load_tools(self.CORE_ROOT_PATH)
        core_skills_dict = self._load_skills(self.CORE_ROOT_PATH)
        # user defined
        root_folder = settings["skills"]["skills_repository_folder"]
        functions_dict = self._load_functions(root_folder)
        tools_dict = self._load_tools(root_folder)
        skills_dict = self._load_skills(root_folder)
        # merge the core into user defined
        functions_dict.update(core_functions_dict)
        tools_dict.update(core_tools_dict)
        skills_dict.update(core_skills_dict)

        self._init(functions_dict, tools_dict, skills_dict)

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            raise ValueError("Singleton instance not yet created")
        return cls._instance

    def _load_skills(self, root_path):
        skills_dict = {}
        for root, dirs, files in os.walk(root_path):
            for file_name in files:
                if file_name.endswith(".txt"):
                    file_path = os.path.join(root, file_name)
                    try:
                        with open(file_path, "r") as file:
                            # Read the contents of the file
                            file_contents = file.read()
                            skills_dict[os.path.splitext(file_name)[0]] = file_contents
                    except Exception:
                        self.logger.critical("failed loading file= %s, skipping", file_path)
        self.logger.debug(skills_dict)
        return skills_dict

    def _load_tools(self, root_path):
        tools_list = []
        for root, dirs, files in os.walk(root_path):
            for file_name in files:
                if file_name.endswith("tools.yaml"):
                    file_path = os.path.join(root, file_name)
                    try:
                        tools_list.extend(safe_load_yaml_file(file_path))
                    except Exception:
                        self.logger.critical("failed loading file= %s, skipping", file_path)
        self.logger.debug(tools_list)

        tools_list = self.validate_tools_title(tools_list)
        llm_tools_dict = dict(map(lambda obj: (obj["tool_name"], obj), tools_list))
        return llm_tools_dict

    def validate_tools_title(self, tools_list):
        return [
            {**element, "title": element["tool_name"].replace("_", " ")} if "title" not in element else element
            for element in tools_list
        ]

    def _load_functions(self, root_path):
        functions_list = []
        for root, dirs, files in os.walk(root_path):
            for file_name in files:
                if file_name.endswith("functions.json"):
                    file_path = os.path.join(root, file_name)
                    try:
                        functions_list.extend(safe_load_json_file(file_path))
                    except Exception:
                        self.logger.critical("failed loading file= %s, skipping", file_path)
        self.logger.debug(functions_list)
        llm_functions_dict = dict(map(lambda obj: (obj["name"], obj), functions_list))
        return llm_functions_dict

    def _init(self, llm_functions_dict, llm_tools_dict, skills_dict):
        self._llm_tools_dict = llm_tools_dict
        # remove functions that does not have matching tool config
        llm_tools_dict = {key: value for key, value in llm_functions_dict.items() if key in llm_tools_dict}
        self._llm_functions_dict = llm_tools_dict
        if skills_dict is not None:
            self._llm_skills_dict = skills_dict

        llm_functions_list = list(self._llm_functions_dict.values())
        if settings["embeddings"].get("CACHE_EMBEDDINGS", default=False) is False:
            self._init_vector_store(llm_functions_list)
        else:
            self.handle_embeding_local_cache(llm_functions_list)

    def handle_embeding_local_cache(self, llm_functions_list):
        if os.path.exists(self.FUNCTIONS_EMBEDDINGS_FILE_PATH):
            self._vector_store = self._vector_store.load_local(
                self.FUNCTIONS_EMBEDDINGS_FILE_PATH,
                self._embeddings,
                self.FUNCTIONS_EMBEDDINGS_FILE_NAME,
            )
        else:
            self._init_vector_store(llm_functions_list)
            self._vector_store.save_local(self.FUNCTIONS_EMBEDDINGS_FILE_PATH, self.FUNCTIONS_EMBEDDINGS_FILE_NAME)

    def _init_vector_store(self, llm_functions_list):
        self._vector_store = self._vector_store.from_texts(
            list(map(lambda obj: obj["description"].strip(), llm_functions_list)),
            self._embeddings,
            llm_functions_list,
        )

    def _vector_store_add_texts(self, llm_functions_list):
        return self._vector_store.add_texts(
            list(map(lambda obj: obj["description"].strip(), llm_functions_list)),
            llm_functions_list,
        )

    def _vector_store_remove_texts(self, skill_ids_list: List[str]):
        try:
            self._vector_store.delete(skill_ids_list)
        except NotImplementedError:
            llm_functions_list = list(self._llm_functions_dict.values())
            self._init_vector_store(llm_functions_list)

    def get_functions_dict(self) -> dict:
        return self._llm_functions_dict

    def similarity_search_with_score(self, query, k):
        """
        Returns:
            List of documents most similar to the query text with
            L2 distance in float. Lower score represents more similarity.
        """
        return self._vector_store.similarity_search_with_score(query, k=k)

    def find_tools(self, required_functions: Set, tools: List):
        tools_dict = {}
        # add mandatory tools that should always be available for the model
        required_functions.update(["get_top_available_tools"])  # "reasoning_acting"
        for required_function in required_functions:
            if self._llm_functions_dict.get(required_function) is not None:
                tools_dict[required_function] = [
                    self._llm_functions_dict[required_function],
                    0.0,
                ]
        for index, item in enumerate(tools):
            if index <= settings["tools_similarity"]["size_of_all_tools_request"]:
                tools_dict[item[0].get("name")] = [
                    self._llm_functions_dict[item[0].get("name")],
                    item[1],
                ]
        return list(tools_dict.values())

    def find_function_by_name(self, function_name, default_value) -> dict:
        return self._llm_functions_dict.get(function_name, default_value)

    def find_tool_by_name(self, tool_name, default_value=None) -> dict:
        return self._llm_tools_dict.get(tool_name, default_value)

    def find_skill_by_name(self, skill_name, default_value=None):
        with self._lock:
            return self._llm_skills_dict.get(skill_name, default_value)

    def update_skill(self, skill_name, new_function, new_tool, skill_code):
        pattern = "^[a-zA-Z0-9_-]{1,64}$"
        if not re.match(pattern, skill_name):
            raise ValueError(skill_name + " does not match the regex: " + pattern)

        with self._lock:
            root_folder = settings["skills"]["skills_repository_folder"]

            llm_functions_dict = self._load_functions(root_folder)
            llm_functions_dict.update({skill_name: new_function})
            safe_json_dump(
                list(llm_functions_dict.values()),
                os.path.join(root_folder, "functions.json"),
            )
            self._llm_functions_dict[skill_name] = new_function

            llm_tools_dict = self._load_tools(root_folder)
            new_tool = self.validate_tools_title([new_tool])[0]
            llm_tools_dict.update({skill_name: new_tool})
            safe_yaml_dump(os.path.join(root_folder, "tools.yaml"), list(llm_tools_dict.values()))
            self._llm_tools_dict[skill_name] = new_tool

            skills_dict = self._load_skills(root_folder)
            skills_dict.update({skill_name: skill_code})
            safe_txt_dump(os.path.join(root_folder, skill_name + ".txt"), skill_code)
            self._llm_skills_dict[skill_name] = skill_code

            self._vector_store_add_texts([new_function])

    def delete_skill(self, skill_name):
        with self._lock:
            root_folder: str = settings["skills.skills_repository_folder"]

            llm_functions_dict = self._load_functions(root_folder)
            if skill_name in llm_functions_dict:
                del llm_functions_dict[skill_name]
            safe_json_dump(
                list(llm_functions_dict.values()),
                os.path.join(root_folder, "functions.json"),
            )
            if skill_name in self._llm_functions_dict:
                del self._llm_functions_dict[skill_name]

            llm_tools_dict = self._load_tools(root_folder)
            if skill_name in llm_tools_dict:
                del llm_tools_dict[skill_name]
            safe_yaml_dump(os.path.join(root_folder, "tools.yaml"), list(llm_tools_dict.values()))
            if skill_name in self._llm_tools_dict:
                del self._llm_tools_dict[skill_name]

            skills_dict = self._load_skills(root_folder)
            if skill_name in skills_dict:
                del skills_dict[skill_name]
            try:
                os.remove(os.path.join(root_folder, skill_name + ".txt"))
            except OSError as e:
                self.logger.warning(str(e))
            if skill_name in self._llm_skills_dict:
                del self._llm_skills_dict[skill_name]

            self._vector_store_remove_texts([skill_name])


class LLMFunctionRepositoryAsAFunction:
    logger = logging.getLogger(__name__)

    def find_most_relevant_tools(self, filter: str = ""):
        repo = LLMFunctionRepository.get_instance()
        k = settings["tools_similarity"]["size_of_all_tools_request"]
        if is_blank(filter):
            tools_list = list(repo.get_functions_dict())[:k]
        else:
            most_similar_document_tools = repo.similarity_search_with_score(query=filter, k=k)
            self.logger.debug(
                "found the most similar tools with the following distances: %s",
                list(map(lambda item: item[1], most_similar_document_tools)),
            )
            tools_metadata = map(lambda item: item[0].metadata, most_similar_document_tools)
            tools_list = list(
                map(
                    lambda item: repo._llm_functions_dict[item.get("name")],
                    tools_metadata,
                )
            )
            tools_list = list(
                map(
                    lambda tool: {
                        "name": tool["name"],
                        "description": tool["description"],
                    },
                    tools_list,
                )
            )
            exact_match = repo._llm_functions_dict.get(filter)
            if exact_match is not None:
                tools_list.append({"name": exact_match["name"], "description": exact_match["description"]})
        return "These are the top {} tools found: ".format(k) + json.dumps(tools_list)
