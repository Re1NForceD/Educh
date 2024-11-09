import asyncio
from slack_sdk import WebClient

from course_classes import *
from app_logic_api import *

loop_task = None

def start_course_loop(logic: AppLogic, client: WebClient):
  global loop_task
  if loop_task is None:
    loop_task = asyncio.create_task(course_loop_impl(logic, client))
    return loop_task
  
  logger.warning(f"course loop is already started")
  return None

async def course_loop_impl(logic: AppLogic, client: WebClient):
  while (True):
    logger.info(f"process course_loop_impl")
    # await client.chat_postMessage(channel=self.course.channel_id, text=f"process course_loop_impl", blocks=[], attachments=[])
    await asyncio.sleep(10)
