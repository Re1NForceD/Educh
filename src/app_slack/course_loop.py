import asyncio
import json
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
    try:
      event = get_next_event(logic)
      await process_next_event(logic, event, client)
    except Exception as e:
      logger.error(f"course_loop_impl: {e}")
    finally:
      await asyncio.sleep(10)

next_event: Event = None
def get_next_event(logic: AppLogic):
  global next_event
  if next_event is None:
    next_event = logic.course.get_next_event()
  return next_event

def clear_next_event():
  global next_event
  next_event = None

async def process_next_event(logic: AppLogic, event: Event, client: WebClient):
  if event is None:
    logger.warning(f"no event to process!")
    return

  logger.info(f"event to process: {event.id}, {event.name}")
  
  now = datetime.datetime.now()
  if event.start_time < now:
    await publish_event(logic, event, client)
    clear_next_event()

async def publish_event(logic: AppLogic, event: Event, client: WebClient):
  blocks = [
    json.loads(event.info)
  ]

  if event.type == E_RESOURCES:
    blocks += get_blocks_event_resources(event)
  elif event.type == E_CLASS:
    blocks += get_blocks_event_class(event)
  elif event.type == E_TEST:
    blocks += get_blocks_event_test(event)
  elif event.type == E_ASSIGNMENT:
    blocks += get_blocks_event_assignment(event)

  await client.chat_postMessage(channel=logic.course.channel_id, blocks=blocks)

  logic.set_events_published([event])

def get_blocks_event_resources(event: ResourcesEvent):
  return []

async def get_blocks_event_class(event: ClassEvent):
  return [] # TODO

async def get_blocks_event_test(event: TestEvent):
  return [] # TODO

async def get_blocks_event_assignment(event: AssignmentEvent):
  return [] # TODO