import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from flask import request


def setup_logging():
  if not os.path.exists("logs"):
    os.makedirs("logs")

  logger = logging.getLogger()

  # Prevent multiple handlers
  if not logger.hasHandlers():
    logger.setLevel(logging.INFO)

    # Custom formatter with filename and line number
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # TODO: revert
    # Create log file with date and time in its name
    # log_filename = datetime.now().strftime(
    #     "logs/[%Y_%m_%d]_%Hh%Mm%Ss_educh.log"
    # )
    # file_handler = RotatingFileHandler(
    #     log_filename, maxBytes=100000, backupCount=10
    # )
    # file_handler.setLevel(logging.INFO)
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

  return logger


def log_config(config):
  logger = logging.getLogger()
  for key, value in config.items():
    logger.info(f"{key}: {value}")


def list_registered_blueprints(app):
  logger = logging.getLogger()
  logger.info("Registered Blueprints:")
  for blueprint_name, blueprint in app.blueprints.items():
    logger.info(
        f"Blueprint name: {blueprint_name}, Blueprint URL prefix: {blueprint.url_prefix}"
    )


def log_request_info():
  logger = logging.getLogger()
  request_info = f"URL: {request.url}\nHeaders: {dict(request.headers)}"

  if request.args:
    request_info += f"\nArgs: {request.args}"

  # Check if the request has JSON content type before accessing request.json
  if request.is_json:
    request_info += f"\nJSON data: {request.json}"
  else:
    request_info += "\nJSON data: None or invalid content type"

  if request.form:
    request_info += f"\nForm data: {request.form}"

  # Logging raw data for non-form and non-JSON types if needed
  if request.data:
    request_info += f"\nRaw data: {request.data.decode('utf-8')}"

  logger.info(request_info)
