import asyncio
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from .events import register_app_events, get_home_view
from .course_loop import start_course_loop

from course_classes import *
from app_logic_api import *

slack_app = None

class SlackApp:
  def __init__(self, config, logic: AppLogic):
    self._configure_app(config)
    self.logic: AppLogic = logic

    self.app = AsyncApp(
        token=self.config["SLACK_BOT_TOKEN"],
    )

    self._register_event_handlers()

    self.app.logger.info("Slack App initialized")

  def _configure_app(self, config):
    self.config = config

  def _register_event_handlers(self):
    register_app_events(self.app, self.logic)

  async def start(self):
    self.logic.start()
    
    if self.logic.course.channel_id is None:
      created_channel = self.app.client.conversations_create(name=f"{self.logic.course.name}_Educh_Channel".lower(),
                                                             is_private=False)
      channel_id = created_channel["channel"]["id"]
      self.app.client.conversations_setPurpose(channel=channel_id, purpose="Channel created by Educh App for learning!")
      self.logic.update_essensials(channel_id=channel_id)

    # users_list = self.app.client.users_list()
    # new_users: list[User] = []
    # for user_info in users_list["members"]:
    #   if user_info["is_bot"] or user_info["updated"] == 0:
    #     continue
    #   user = User(platform_id=user_info["id"], name=user_info["profile"]["display_name_normalized"], role=(U_MASTER if user_info["is_primary_owner"] else U_GUEST))
    #   if self.logic.course.add_user(user):
    #     new_users.append(user)

    # if len(new_users) > 0:
    #   self.app.client.conversations_invite(channel=self.logic.course.channel_id, users=[user.platform_id for user in new_users], force=True)
    #   self.logic.update_users()
    
    for user in self.logic.course.users.values():
      await self.update_home_page(user)

    if not self.logic.course.is_can_be_worked_with():
      raise Exception("course can not be worked with")
    
    handler = AsyncSocketModeHandler(self.app, self.config["SLACK_APP_TOKEN"])
    handler_task = asyncio.create_task(handler.start_async())
    
    if self.logic.is_in_process():
      start_course_loop(self.logic, self.app.client)

    await handler_task

  async def update_home_page(self, user: User):
    try:
      await self.app.client.views_publish(
          user_id=user.platform_id,
          view=get_home_view(user, self.logic)
      )
    except Exception as e:
      logger.error(f"Error publishing home tab: {e}")

def init_slack_app(config, app_logic):
  slack_app = SlackApp(config, app_logic)
  return slack_app
