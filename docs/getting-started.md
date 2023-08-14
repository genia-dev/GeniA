# Getting started

The easiest way to get started with GeniA is using [Streamlit](https://streamlit.io/) web app. Make sure you have `python3` & `pip3` installed, then run:

```
pip3 install streamlit genia
```

Then you can run the streamlit web app by:

```
genia
```

You can also play with GeniA in a Terminal using GeniA 'local' mode.

Both quick start options provide a sneak peek, but **GeniA is crafted for team collaboration** and works best in **Slack**.

For simplicity, we recommend running it locally using [Docker](#run-via-docker). If you want to run docker locally, please refer to the [Installation](#installation) section.

### Open AI Azure deployment
When using Azure OpenAI, add those to your environment variables:
```
OPENAI_API_DEPLOYMENT=
OPENAI_API_TYPE="azure"
OPENAI_API_BASE=https://<your-endpoint.openai.azure.com/
OPENAI_API_VERSION="2023-07-01-preview"
```

### Additional notes

#### Cost implications

GeniA uses OpenAI, be mindful of cost implications and ensure you set usage limits. You can configure both soft and hard limits at the following URL: https://platform.openai.com/account/billing/limits.

#### Model version

By default, GeniA is set to use `gpt-3.5-turbo-0613`. We acknowledge that `gpt-4-0613` often delivers superior results, but have found the 3.5 version to be a more cost-effective choice.
