# GeniA Slack App Bot

## Installation

For the Slack GPT Bot to function effectively, it's crucial to establish the correct permissions for your Slack bot. Please follow the forthcoming guidelines to set up the necessary permissions.

!!! note 
    When it comes to [Choosing a protocol to connect to Slack](https://api.slack.com/apis/connections), there are two primary options. In this instance, we utilize `Socket Mode`, enabling your app to leverage the `Events API` and the platform's interactive components without the need for a public HTTP Request URL. Instead of sending payloads to a public endpoint, Slack employs a WebSocket URL to communicate with your app.

1. In the project's root directory, mv the [.env.template](./.env.template) into `.env` file and input your Slack keys
2. Create a new [Slack App](https://api.slack.com/authentication/basics).
3. Navigate to your [Slack API Dashboard](https://api.slack.com/apps) and select the app you've created for this bot.
4. On the left-hand side menu, click on `OAuth & Permissions`.
5. Within the `Scopes` division, there are two categories of scopes: `Bot Token Scopes` and `User Token Scopes`. Append the following scopes under `Bot Token Scopes`:
   `app_mentions:read`
   `chat:write`
   `channels:history`
   `groups:history`
   `im:history`
   `mpim:history`
6. Ascend to the `OAuth Tokens for Your Workspace` and hit the `Install App To Workspace` button. This operation will produce the `SLACK_BOT_TOKEN`.
7. On the left-hand side menu, click on `Socket Mode` and activate it. You'll be asked to `Generate an app-level token to enable Socket Mode`. Generate a token labeled `SLACK_APP_TOKEN` and include the `connections:write` scope.
8. In the `Socket Mode` page's `Features affected` section, hit `Event Subscriptions` and switch `Enable Events` to the `On` state. Append the app_mention event, coupled with the `app_mentions:read` scope in the `Subscribe to bot events` subsection below the toggle.
