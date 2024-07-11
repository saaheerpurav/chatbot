from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    send_from_directory,
    cli,
)
import os
import json
import s3fs
from waitress import serve

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)

cli.load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")


# ============ SET dev OR prod ============
app.config["ENV"] = "prod"
# =========================================


s3 = s3fs.S3FileSystem(
    key=os.environ.get("AWS_KEY"),
    secret=os.environ.get("AWS_SECRET"),
    s3_additional_kwargs={"ACL": "public-read"},
)

bot_cache = {}


def init_bot_config(bot_id):
    DATA_DIR = "saaheer-chatbot-db/client_data/" + bot_id
    PERSIST_DIR = "saaheer-chatbot-db/indexes/" + bot_id

    if not s3.exists(PERSIST_DIR):
        # NEW
        print("NEW")

        documents = SimpleDirectoryReader(
            input_dir=DATA_DIR + "/knowledge", fs=s3
        ).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(PERSIST_DIR, fs=s3)

    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR, fs=s3)
    bot_cache[bot_id] = {"bot_id": bot_id, "storage_context": storage_context}

    with s3.open(DATA_DIR + "/config.json", "r") as f:
        obj = json.load(f)
        session["bot_name"] = obj["bot_name"]
        session["pic_url"] = obj["pic_url"]


def get_bot_response(user_input):
    bot_data = bot_cache[session["bot_id"]]

    storage_context = bot_data["storage_context"]
    index = load_index_from_storage(storage_context)

    query_engine = index.as_query_engine()
    response = query_engine.query(user_input)

    return response


@app.route("/chatbot-iframe")
def main():
    return render_template("index.html")


@app.route("/static/css")
def send_css():
    return send_from_directory("static" + os.sep + "css", "output.css")


@app.route("/init-bot", methods=["POST"])
def init_bot():
    bot_id = request.args.get("id")
    session["bot_id"] = bot_id
    init_bot_config(bot_id)

    return jsonify(
        {"status": 200, "bot_name": session["bot_name"], "pic_url": session["pic_url"]}
    )


@app.route("/chatbot", methods=["POST"])
def bot():
    data = request.json
    user_input = data.get("message")
    response = get_bot_response(user_input)

    return jsonify({"status": 200, "response": str(response)})


if __name__ == "__main__":
    if app.config["ENV"] == "dev":
        app.run(debug=True)

    elif app.config["ENV"] == "prod":
        serve(app, host="0.0.0.0", port=8080)
