from flask import Blueprint, jsonify, current_app
import logging

logger = logging.getLogger()

ep_health = Blueprint("health", __name__)


@ep_health.route("/health", methods=["GET"])
def health():
  logic = current_app.config['logic']
  return jsonify({"status": "healthy", "name": logic.verify_app(1, "dGVzdF9jb3Vyc2U=")})
