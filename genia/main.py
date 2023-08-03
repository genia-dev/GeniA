import logging
import sys
import threading
from dotenv import load_dotenv
from genia.user_interface.shell_app import ShellApp
from genia.settings_loader import settings
from genia.agents.chat import OpenAIChat

from gunicorn.app.base import BaseApplication
from flask import Flask, jsonify

load_dotenv()

app = Flask(__name__)


class ServerApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


# Configure logging levels
logging.basicConfig(level=settings.logger_level.DEFAULT_LOGGING_LEVEL)
for logger_name, log_level in settings.logger_level.to_dict().items():
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

oa = None


@app.route("/api/health", methods=["GET"])
def api():
    number_of_sessions, sessions_sizeof = oa.get_conversation_stats()
    return jsonify(
        {
            "chat_history": {
                "sessions_sizeof": sessions_sizeof,
                "number_of_sessions": number_of_sessions,
            }
        }
    )


def slack_app():
    logging.info("starting slack app")
    from genia.user_interface import slack_app


def streamlit():
    logging.info("starting streamlit app")
    from genia.user_interface.streamlit_app import StreamlitApp

    StreamlitApp()


def setup_slack():
    slack_app_thread = threading.Thread(target=slack_app)
    slack_app_thread.daemon = True
    slack_app_thread.start()


def local():
    oa = OpenAIChat()
    ShellApp(provider=oa).cmdloop()


def slack():
    setup_slack()

    host = settings.server.host
    port = settings.server.port
    workers = settings.server.workers

    logging.info(f"starting server listen on host: {host} with port: {port} with #workers: {workers}")
    options = {
        "bind": "%s:%s" % (host, port),
        "workers": workers,
    }
    ServerApplication(app, options).run()


if __name__ == "__main__":
    streamlit()
