from slack_bolt.adapter.socket_mode import SocketModeHandler
from events import *
from app import app
import os

import logging

logging.basicConfig(level=logging.DEBUG)


def startApp():
  SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()


if __name__ == "__main__":
  startApp()
