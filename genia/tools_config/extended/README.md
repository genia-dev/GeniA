# Adding your extended functions

### Background

OpenAI plugins have created a lot of interest within the community, and by June 23, it has been decided to add functions to enrich the model with additional capabilities. introducing such functions should adhere to the following schema - [OpenAI function calling](https://platform.openai.com/docs/api-reference/chat/create#chat/create-functions)

We have decided to align to the open ai schema to allow anyone who have already created their plugin or function to easily teach them to GeniA with minimal work

keeping the functions.json untouched as a valid OpenAI schema, the additional, and minimal data required is where its implementation can be found

so for example if you have your code under my_module.MyClass with the method: my_method(my_param: str, another_param: int)

you should add a new entry to a YAML file (YAML uses less tokens)

```yaml
- tool_name: my_tool_unique_name
  category: python
  title: short title for human display
  class: my_module.MyClass
  method: my_method
```

and the following OpenAI compatible function.json entry according to following schema - [OpenAI function calling](https://platform.openai.com/docs/api-reference/chat/create#chat/create-functions)

```json
{
  {
    "name": "my_tool_unique_name",
    "description": "a description for the model",
    "parameters": {
      "type": "object",
      "properties": {
        "my_param": {
          "type": "string",
          "description": "my param model description"
        },
        "another_param": {
          "type": "int",
          "description": "my param model description"
        },
  
      },
      "required": [
        "my_param",
        "another_param"
      ]
    }
  }

```

## Complete example

#### adding a new function like Github ability to create a new repo.

1. first we need to come up with the code, not sure how to implement, simple - just ask GeniA

<p align="center">
<br/>
   <img src="/media/functions/ask_genia.png" />
<br/>
</p>

2. add your code to the project, in this case there's already an existing github class we can extend with additional capabilities which already handles the required credentials complexity

```python
import logging

from genia.tools.github_client.github_client import GithubClient


class GithubEnrichedClient(GithubClient):
    logger = logging.getLogger(__name__)

    def create_new_repo(self, new_repo_name: str):
        # Create a GitHub instance
        g = self.login()
        # Create a new repository
        repo = g.get_user().create_repo(new_repo_name)
        # Print the repository details
        result = "Repository {} created successfully on url: {}", repo.name, repo.html_url
        self.logger.debug(result)
        return result
```


3. add the configuration to function.json

```json
[
    {
        "name": "create_new_github_repo",
        "description": "create a new github repository",
        "parameters": {
            "type": "object",
            "properties": {
                "new_repo_name": {
                    "type": "string",
                    "description": "the new GitHub repository name"
                }
            },
            "required": [
                "new_repo_name"
            ]
        }
    }
]
```

4. add the following configuration to tools.yaml

   ```
   - tool_name: create_new_github_repo
     category: python
     title: create new github repository
     class: genia.tools.github_client.github_client.GithubEnrichedClient
     method: get_create_new_repo
   ```

5. add the files under the tools_config/extended/github folder as so:

<p align="center">
<br/>
   <img src="/media/functions/directory.png" />
<br/>
</p>