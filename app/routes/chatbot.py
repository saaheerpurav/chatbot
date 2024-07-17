from flask import (
    render_template,
    request,
    jsonify,
    session,
    send_from_directory,
    Blueprint,
)

import os
from ..utils import get_bot_response, init_bot_config, validate_email
from .. import db
from ..models import Leads


bp = Blueprint("chatbot", __name__)


@bp.route("/chatbot-iframe")
@bp.route("/chatbot/iframe")
def iframe():
    return render_template("chatbot.html")


@bp.route("/preview")
def preview():
    return render_template("preview.html")


@bp.route("/chatbot/css")
def send_css():
    return send_from_directory("static" + os.sep + "css", "output.css")


@bp.route("/embed")
def embed_chatbot():
    return send_from_directory("static" + os.sep + "js", "embed.js")


@bp.route("/chatbot/init-bot", methods=["POST"])
def init_bot():
    bot_id = request.args.get("id")
    session["bot_id"] = bot_id
    bot_config_result = init_bot_config(bot_id)

    return jsonify(bot_config_result), bot_config_result["status"]


@bp.route("/chatbot/message", methods=["POST"])
def bot():
    data = request.json
    user_input = data.get("message")
    bot_id = data.get("botId")
    response = get_bot_response(bot_id, user_input)

    return jsonify({"status": 200, "response": str(response)})


@bp.route("/chatbot/email-submit", methods=["POST"])
def email_submit():
    data = request.json
    email = data.get("email")

    if validate_email(email):
        lead = Leads(
            bot_id=data.get("botId"),
            email=email,
        )
        db.session.add(lead)
        db.session.commit()

        return jsonify({"status": 200})

    else:
        return jsonify({"status": 400, "error": "INVALID_EMAIL"}), 400