![CI](https://github.com/genia-dev/GeniA/actions/workflows/ci.yml/badge.svg)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

<p align=center>
   <a href="https://genia.dev" target="_blank">
      <img src="./media/genia_title.png"/>
   </a>
</p>
<br>
<p>
Imagine a ChatGPT integrated with your team's tools and APIs, capable of executing tasks and handling queries independently, contributing to time and energy efficiency.
<br><br>
GeniA is an AI assistant developed for engineering tasks. GeniA is a dynamic, intuitive tool capable of managing tasks in your team's Slack channel.
</p>

## 📝 Table of Contents

1. [🎉 Introduction](#introduction)
2. [▶️ Getting started](#getting-started)
3. [🤝 Contributing](#contributing)
4. [📜 License](#license)
5. [📞 Contact](#contact)
6. [🚀 Future Plans](#future-plans)

#### Full documentation can be found [here](https://genia-dev.github.io/GeniA/)

## Introduction

While ChatGPT and CoPilot have garnered significant attention for their ability to assist with writing new code, as software engineers, we understand that coding is merely one aspect of our daily responsibilities and AI present many additional opportunities to minimize bolier plate, time wasters and cross team dependencies.

**Under the hood** GeniA is built upon the [function-calling capabilities offered by OpenAI](https://openai.com/blog/function-calling-and-other-api-updates) (OpenAI or Azure). GeniA requires OpenAI API Key, you can generate one [here](https://platform.openai.com/account/api-keys)

### GeniA is 100% open source!

Built with love by engineers for engineers, our goal is to help teams harness the power of LLMs to boost how fast you can go!

### GeniA is Production grade

we have set ourselves the goal of building a production-grade software right off the bat. Now, you can start working with GeniA in production by installing the GeniA container, integrate it into your team's Slack channel, and let it land on its feet running.

## Architecture

<p float="center">
   <img src="media/Genia_agents.png"/>
</p>
<br/>
### Imagine a virtual asisstant empowering you with:

#### Research & Development Scenarios

Deployment, troubleshooting, log summarization, build initiation, PR digesting

* Deploy your k8s-based service to staging/production using Argo
* Investigate the cause of the last Argo deployment failure
* Summarize the recent logs from your Node.js service
* Initiate a new Jenkins build
* Summarize GitHub pull request along with its content

#### FinOps Shift-Left

Reporting on unused resources, optimising cloud expenditure.

* Generate a report detailing unutilized cloud resources per team and share it on Slack
* Create a usage report for AWS ECR (Amazon Elastic Container Registry) to identify potential cost-saving opportunities

#### SecOps Shift-Left

Vulnerability checks, best practices, playbooks.

* Conduct a security vulnerability analysis on your S3 buckets
* Grant me temporary production permissions (Add me temporarily to an IAM user group with auditing)

#### SRE Shift-Left

lower your MTTR, Service usage monitoring, service optimization.

* Examine my service usage metrics for any anomalies
* Increase the memory for my Node service deployed on a k8s cluster

#### DevOps Shift-Left

Scaling services, managing EC2 instances and cron jobs, coding utilities.

* Scale out my Node.js k8s-based service
* Identify unlabeled EC2 instances
* Set up a cron job to trigger a task
* Develop code for a new utility and deploy my 'automate this task' snippet to a lambda function
* Trigger any of my company's predefined playbooks

<p float="center">
   <img src="media/Genia_in_a_war_room.gif"/>
</p>

### Many more great examples [can be found here](./media/)

<br/>

## Getting Started

```
pip3 install streamlit genia
```

Then you can run the streamlit web app by:

```
genia
```

For more details please see our [documentation here](https://genia-dev.github.io/GeniA/getting-started/)
Once installed and granted with permissions, a few great example scenarios [can be found here](./media/)

## Contributing

We would appreciate your contributions! 🙌🌟💖
👩‍💻➕👨‍💻 Fork GeniA repository, make your changes, and submit a pull request!
More details can be found [here](./CONTRIBUTING.md).

## License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

[LICENSE](./LICENSE)

## Contact

Got an idea to improve our project? We'd love to hear it and collaborate with you. Don't hesitate to reach out to us! Just open an [issue](https://github.com/GeniA-dev/GeniA/issues) and GeniA will respond to you 🦸‍♀️🦸‍♂️ !
You can see details [here](./.github/ISSUE_TEMPLATE/submit-a-request.md).

## Future Plans

- OKTA integration for SSO.
- RBAC Support.
- Extending capabilities with thousands of new tools.

#### Full documentation can be found [here](https://genia-dev.github.io/GeniA/)
