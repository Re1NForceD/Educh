from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .events import register_app_events

from course_classes import *

slack_app = None

class SlackApp:
  def __init__(self, config, logic):
    self._configure_app(config)
    self.logic = logic

    self.app = App(
        token=self.config["SLACK_BOT_TOKEN"],
    )

    self._register_event_handlers()

    self.app.logger.info("Slack App initialized")

  def _configure_app(self, config):
    self.config = config

  def _register_event_handlers(self):
    register_app_events(self.app, self.logic)

  def start(self):
    self.logic.start()

    if self.logic.is_first_launch():
      # use this event for master init?
      # DEBUG:slack_bolt.IgnoringSelfEvents:Skipped self event: {'subtype': 'channel_join', 'user': 'U07MC9JFN6R', 
      # text': '<@U07MC9JFN6R> has joined the channel', 'inviter': 'U07MAGQ4PU2', 'type': 'message', 
      # 'ts': '1729060335.359069', 'channel': 'C07LY55M7QF', 'event_ts': '1729060335.359069', 'channel_type': 'channel'}
      users_list = self.app.client.users_list()
      for user_info in users_list["members"]:
        if user_info["is_bot"] or user_info["updated"] == 0:
          continue
        self.logic.course.add_user(User(platform_id=user_info["id"], name=user_info["profile"]["display_name_normalized"], role=(U_MASTER if user_info["is_primary_owner"] else U_GUEST)))
      self.logic.launch_update_users()

    SocketModeHandler(self.app, self.config["SLACK_APP_TOKEN"]).start()

def init_slack_app(config, app_logic):
  slack_app = SlackApp(config, app_logic)
  return slack_app
