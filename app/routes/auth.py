from flask import render_template, request, Blueprint, redirect, url_for, jsonify, json
from flask_login import login_user, logout_user, login_required, current_user

from .. import db, bcrypt
from ..models import Users
from ..utils import (
    validate_email,
    get_user,
    get_bot_data,
    update_bot_data,
    create_new_bot,
    upload_knowledge,
    delete_bot_data,
    fetch_bot_config,
    check_bot_exists,
    clear_bot_cache,
    send_email
)


bp = Blueprint("auth", __name__)




@bp.route("/", methods=["GET"])
def home():
    return render_template("home.html")


@bp.route("/contact", methods=["POST"])
def contact():
    form_data = request.form.to_dict()
    response = send_email(form_data)

    if response:
        return jsonify({"status": 200})
    else:
        return jsonify({"status": 400, "error": "EMAIL_ERROR"}), 400
    


@bp.route("/signup", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.json.get("email")

        if get_user(email) != None:
            return jsonify({"status": 400, "error": "USER_ALREADY_EXISTS"}), 400

        if validate_email(email):
            password = request.json.get("password")
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            user = Users(email=email, password=hashed_password, bot_ids=[])

            db.session.add(user)
            db.session.commit()

            login_user(user)
            return jsonify({"status": 200, "redirect": url_for("auth.dashboard")})

        else:
            return jsonify({"status": 400, "error": "INVALID_EMAIL"}), 400

    return render_template("signup.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.json.get("email")

        if validate_email(email):
            user = get_user(email)
            password = request.json.get("password")

            if user:
                if bcrypt.check_password_hash(user.password, password):
                    login_user(user)
                    return jsonify(
                        {"status": 200, "redirect": url_for("auth.dashboard")}
                    )

                else:
                    return jsonify({"status": 400, "error": "INVALID_PASSWORD"}), 400

            else:
                return jsonify({"status": 400, "error": "USER_NOT_FOUND"}), 400

        else:
            return jsonify({"status": 400, "error": "INVALID_EMAIL"}), 400

    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/dashboard")
@login_required
def dashboard():
    data = []
    for bot in current_user.bot_ids:
        obj = fetch_bot_config(bot)
        data.append({"id": obj["id"], "bot_name": obj["bot_name"]})

    return render_template("dashboard.html", data=json.dumps(data))


@bp.route("/dashboard/delete-bot", methods=["POST"])
def delete_bot():
    delete_bot_data(request.json["id"])
    return jsonify({"status": 200})


@bp.route("/dashboard/new-bot", methods=["GET"])
def new_bot():
    return render_template("new-bot.html")


@bp.route("/dashboard/new-bot/create", methods=["POST"])
def upload_file():
    bot_data = json.loads(request.form.get("bot_data"))
    new_id = create_new_bot(bot_data)

    if "files[]" not in request.files:
        return jsonify({"status": 400, "error": "FILE_NOT_FOUND"}), 400

    files = request.files.getlist("files[]")
    if not files:
        return jsonify({"status": 400, "error": "FILE_NOT_FOUND"}), 400

    allowed_extensions = {"txt"}
    for file in files:
        if file.filename == "":
            return jsonify({"status": 400, "error": "FILE_NOT_FOUND"}), 400

        if (
            "." not in file.filename
            or file.filename.rsplit(".", 1)[1].lower() not in allowed_extensions
        ):
            return jsonify({"status": 400, "error": "UNSUPPORTED_FILE_TYPE"}), 400

        upload_knowledge(bot_data["id"], file)

    return jsonify({"status": 200, "redirect": url_for("auth.edit_bot", bot_id=new_id)})


@bp.route("/dashboard/update-bot", methods=["POST"])
def update_bot():
    bot_data = json.loads(request.form.get("bot_data"))
    files = request.files.getlist("files[]")

    allowed_extensions = {"txt"}
    for file in files:
        if file.filename == "":
            return jsonify({"status": 400, "error": "FILE_NOT_FOUND"}), 400

        if (
            "." not in file.filename
            or file.filename.rsplit(".", 1)[1].lower() not in allowed_extensions
        ):
            return jsonify({"status": 400, "error": "UNSUPPORTED_FILE_TYPE"}), 400

        upload_knowledge(bot_data["id"], file)

    update_bot_data(bot_data)
    clear_bot_cache(bot_data["id"])

    return jsonify({"status": 200})


@bp.route("/dashboard/edit-bot/<bot_id>")
@login_required
def edit_bot(bot_id):
    if not check_bot_exists(bot_id):
        return "Could not find bot"
    return render_template("edit-bot.html", data=json.dumps(get_bot_data(bot_id)))
