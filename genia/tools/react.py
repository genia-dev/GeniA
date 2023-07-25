import logging
import re


class ReAct:
    def plan(self, task_category, thoughts) -> str:
        logging.info("react task_category %s, thoughts %s", task_category, thoughts)
        # ״plan", "research", "design", "code",
        if task_category == "code":
            res = re.sub(
                r"\s+",
                " ",
                """
            AI should follow the below step by step and for each one, reflect and improve the solution along the steps.
            1. Identify the task's definition of done
            2. input parameters and what is the return value
            3. write the code
            4. AI should rewrite to use open source whenever possible
            5. add documententation to your code. for example in python use Docstrings 
            6. add tests to your code if needed
            7. AI should review the code best practices, smells and security conserns. AI should fix the code if needed.
            8. AI should reflect on the code you wrote and look for any improvments 
            """,
            )
            # Be very concise short and percise.
            # before you proceed to next step validate with me first. for example did you get the definition of done correctly?
        elif task_category == "plan":
            res = re.sub(
                r"\s+",
                " ",
                """
            share your thoughts with the user, take it step by step
            if you are happy with the plan, stop and present it and your thoughts to the user in a format that can be saved into memory.
            """,
            )
        elif task_category == "design":
            res = re.sub(
                r"\s+",
                " ",
                """
            You should design, reflect and improve the solution along the steps.
            """,
            )
        else:
            res = (
                "AI should follow the below step by step and for each one, reflect and improve the solution along the steps. "
                + thoughts
            )
        """
            1. Identify the main objectives of the task.
            2. Identify knowledge gaps the AI might have, skill-gaps, open questions regarding the definitions/specifications/requirements of the task. bridge them with research (searching the web, crawling, summarizing, learning) or if you must, by asking the user.
                2.1 for example: before you start a new development task, search for seeds/boilerplates, references, libraries and other dependencies online
            3. Break down each task into subtasks.
            4. Prioritize the tasks and subtasks.
            5. Create a timeline for completing each task and subtask.
            6. Begin working on the tasks in order of priority.
            7. Follow the plan and adapt.
            8. Test, Verify, or fact check your intermediary steps and results.
            9. if you are not confident enough in your verification or results, ask the user.
            """
        return res
