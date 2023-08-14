# Growing GeniA's Toolbox

## Teaching GeniA new Skills: Adding Tools Effortlessly

Adding a new tool adheres to the [OpenAI JSON configuration](https://platform.openai.com/docs/api-reference/chat/create#chat/create-functions) standards. This ensures compatibility, making it easy to import any existing function-calling project or ChatGPT plugin.
The only missing component is a brief description guiding the model on when to use the function. We prefer to maintain this in a separate file - refer to the [tools.yaml](https://github.com/genia-dev/GeniA/blob/main/genia/tools_config/core/tools.yaml).

GeniA is designed to be a quick learner, rapidly acquiring the capability to use new tools. We've made the learning process as straightforward as possible. Here's how you can teach GeniA:

1. **Incorporating Code Tools:** By adding a simple specification, GeniA can invoke any class and method within your codebase. For instance, below is an example of integrating a utility tool from your software development suite:

```yaml
- tool_name: bug_tracker_api
  category: python
  class: mypackage.utilities.bugtracker.BugTrackerAPIWrapper
  method: run

```

2. **Connecting to URLs:** GeniA can perform GET requests with either path or request parameters. You can integrate this by providing a URL, as shown in this example, which fetches the current CI/CD pipeline status:

```yaml
- tool_name: get_pipeline_status
  title: fetch the current pipeline status
  category: url
  template: https://ci.yourserver.com/api/v1/pipeline?project_id={project_id}&pipeline_id={pipeline_id}
```

3. **Utilizing OpenAPI Swagger Files:** Imagine your AI model being able to invoke any API out there - GeniA is capable of that! You can easily integrate any standard OpenAPI into GeniA using a Swagger file. This feature is still under development, but a working example is provided out of the box.
4. **Learning Natural Language Skills:** This is where LLM truly shines. GeniA has an experimental feature that allows it to acquire new skills using natural language. It retains the steps taken to accomplish a task in its long-term memory, categorizes them under a new skill, and loads them into memory for future use. In this way, GeniA can learn and execute complex tasks, all in natural language.

##### see complete function [documentation here](https://github.com/genia-dev/GeniA/blob/main/genia/tools_config/extended/)