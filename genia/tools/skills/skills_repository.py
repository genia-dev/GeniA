import logging
from genia.llm_function.llm_function_repository import LLMFunctionRepository


class LLMSkillsRepository:
    logger = logging.getLogger(__name__)

    def read_skill(self, skill_name):
        repo = LLMFunctionRepository.get_instance()
        current_function = repo.find_function_by_name(skill_name, {})
        skill = repo.find_skill_by_name(skill_name)
        return {
            "skill_name": skill_name,
            "skill_text": skill,
            "skill_description": current_function.get("description"),
        }

    def delete_skill(self, skill_name):
        LLMFunctionRepository.get_instance().delete_skill(skill_name)
        return f"The skill {skill_name} was deleted."

    def upsert_skill(self, skill_name, skill_description, skill_text):
        repo = LLMFunctionRepository.get_instance()
        current_function = repo.find_function_by_name(skill_name, {})
        new_function = {}
        new_function.update(current_function)
        new_function.update(
            {
                "name": skill_name,
                "description": skill_description,
                "parameters": {"type": "object", "properties": {}, "required": []},
            }
        )

        current_tool = repo.find_tool_by_name(skill_name, {})
        new_tool = {}
        new_tool.update(current_tool)
        new_tool.update(
            {
                "tool_name": skill_name,
                "category": "skill",
            }
        )

        repo.update_skill(skill_name, new_function, new_tool, skill_text)
        return "done."
