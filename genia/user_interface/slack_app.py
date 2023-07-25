import os
import logging
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from genia.agents import OpenAIChat
from genia.settings_loader import settings

logger = logging.getLogger(__name__)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

WAIT_MESSAGE = settings.slack.wait_message
ERROR_MESSAGE = settings.slack.error_message

USER_SELECTION_YES = "yes"

chat_controller = OpenAIChat()

app = App(token=SLACK_BOT_TOKEN)


def update_chat(channel_id, reply_message_ts, response_text: str):
    if settings.chat.programmatic_user_tool_validation_required and response_text.startswith(
        settings.agent_prompt.user_validation_title
    ):
        options = [
            {"text": "Yes", "value": USER_SELECTION_YES, "emoji": "👍"},
            {"text": "No", "value": "abort", "emoji": "👎"},
        ]

        # Create the attachments with buttons
        attachments = [
            {
                # "text": "Please select an option:",
                "fallback": "You are unable to choose an option",
                "callback_id": "predefined_validation_options",
                "color": "#3AA3E3",
                "attachment_type": "button",
                "actions": [
                    {
                        "name": "options_list",
                        "text": f"{option['emoji']} {option['text']}",
                        "type": "button",
                        "value": option["value"],
                    }
                    for option in options
                ],
            }
        ]
    else:
        attachments = None

    app.client.chat_update(
        channel=channel_id,
        ts=reply_message_ts,
        text=response_text,
        attachments=attachments,
    )


def get_conversation(channel_id, thread_ts):
    return app.client.conversations_replies(channel=channel_id, ts=thread_ts, inclusive=True)


@app.action("predefined_validation_options")
def handle_action_validation(ack, body):
    # Acknowledge the action
    ack()
    thread_ts = body["original_message"]["thread_ts"]
    user_id = body["user"]["id"]
    ts = body["original_message"]["ts"]
    original_message_text = body["original_message"]["text"]
    selected_answer = body["actions"][0]["value"]
    channel_id = body["channel"]["id"]
    # attachments = body["original_message"]["attachments"]
    logger.debug(
        "thread_ts=%s, selected_answer= %s, channel_id=%s",
        thread_ts,
        selected_answer,
        channel_id,
    )
    notify_user_selection(user_id, ts, original_message_text, selected_answer, channel_id)
    response_text = chat_controller.process_message(selected_answer, thread_ts)
    app.client.chat_postMessage(channel=channel_id, text=response_text, thread_ts=ts)
    # logger.info(body)


def notify_user_selection(user_id, ts, original_message_text, selected_answer, channel_id):
    attachments = [
        {
            "attachment_type": "default",
        }
    ]
    if selected_answer == USER_SELECTION_YES:
        attachments[0]["text"] = "✅ <@{}> approved this action".format(user_id)
        attachments[0]["color"] = "#008000"
    else:
        attachments[0]["text"] = "👎 <@{}> disapproved this action".format(user_id)
        attachments[0]["color"] = "#FF0000"

    app.client.chat_update(channel=channel_id, ts=ts, attachments=attachments, text=original_message_text)


def remove_bot_name(expression):
    cleaned_expression = re.sub(r"^<@.*?>", "", expression)
    return cleaned_expression.strip()


@app.event("app_mention")
def command_handler(body, context):
    try:
        channel_id = body["event"]["channel"]
        thread_ts = body["event"].get("thread_ts", body["event"]["ts"])

        reply_message_ts = update_chat_wait(channel_id, thread_ts)
        response_text = chat_controller.process_message(remove_bot_name(body["event"]["text"]), thread_ts)
        update_chat(channel_id, reply_message_ts, response_text)

    except Exception as e:
        logger.exception("Error: %s", e)
        app.client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=ERROR_MESSAGE)


def update_chat_wait(channel_id, thread_ts):
    slack_resp = app.client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=WAIT_MESSAGE)
    reply_message_ts = slack_resp["message"]["ts"]
    return reply_message_ts


handler = SocketModeHandler(app, SLACK_APP_TOKEN)
handler.start()
