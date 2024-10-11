from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .events import register_app_events

slack_app = None

class SlackApp:
  def __init__(self, config):
    self._configure_app(config)
    
    self.app = App(
        token=self.config["SLACK_BOT_TOKEN"]
    )

    self._register_event_handlers()

    self.app.logger.info("Slack App initialized")

  def _configure_app(self, config):
    self.config = config

  def _register_event_handlers(self):
    register_app_events(self.app)

  def start(self):
    SocketModeHandler(self.app, self.config["SLACK_APP_TOKEN"]).start()

def init_slack_app(config):
  slack_app = SlackApp(config)
  return slack_app
