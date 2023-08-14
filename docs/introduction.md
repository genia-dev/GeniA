# Introduction

## Introducing Tools 3.0: Enhance Coding with Large Language Models

Tools 2.0 with low-code/no-code approaches have been revolutionary, allowing users to leverage drag-and-drop functions over traditional coding for certain use cases.

However, with the advent of Language Learning Models (LLMs), Tools 3.0 pushes the boundary further, empowering everyone to write code using natural language. It signifies a shift from proprietary, restrictive design paradigms to a more open, innovative approach where the model assists in understanding and revising complex code snippets.

Tools 3.0 negates the need for proprietary YAML files and vendor-specific domain languages (DSLs), urging users to rely on native code. Rather than waiting for vendor updates to fulfill requirements, users can now instruct LLMs to write code, create it themselves, or utilize the vast range of community-contributed tools.

Remember, any class, method, or API available becomes a learning and application tool for GeniA. Tools 3.0 redefines coding, transforming it into an intuitive, flexible, and democratized process.

## Features

GeniA's unique features include:

1. **Production-Grade**: Engineered for real-world applications.
2. **Collaborative assistant**: Designed to make the development process more interactive and enjoyable.
3. **Proactively taking action**: building, coding, executing, summarizing. not just giving you a good advice.
4. **Customizable and Extensible**: As an open-source tool, GeniA can be tailored to your specific needs.
5. **Quick Learner**: Rapidly adapts to new tools and APIs.

## Comparison to LLM

**Safety Prioritized:** While LLMs offer suggestions, GeniA goes a step further but with utmost caution. It's designed to function responsibly in live environments, ensuring it doesn't take unrestricted decisions.

**Beyond Recommendations:** Where LLMs provide guidance, GeniA offers proactive assistance. It doesn't just advise on the steps you need to take but goes ahead to perform the tasks itself. You could provide a code snippet, and GeniA will handle its deployment to Lambda, integrating seamlessly with your production environment and CI/CD tools.

**Intelligent Tool Selection:** GeniA is not just another tool, it's also a tool-finding system. It's designed to acquaint itself with an expansive set of tools. However, mindful of the limitations of the LLM context window and token costs, it optimizes and feeds the model with only the most relevant tools. Utilizing vector databases (FAISS by default), GeniA selects tools with descriptions that align best with your intent. This smart selection process allows GeniA to work more efficiently and be more responsive to your specific needs.

## Can GeniA Interface with Any Existing API?

Indeed, GeniA has the capability to connect with any available API. Although it's currently an active area of academic research rather than a full-fledged production-grade tool, we've adapted OpenAI's plugin approach for increased simplicity and wider integration possibilities. You can incorporate GeniA into any existing code classes or APIs.

Our ultimate achievement is empowering GeniA to acquire new skills without necessitating model fine-tuning or, in many cases, redeployment of your service. However, it's worth noting that the introduction of a completely new tool might call for some prompt adjustments and testing.

Presently, the authentication process for a new tool falls on the tool creator. However, we plan to standardize this aspect within the project framework shortly.