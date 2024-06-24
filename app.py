from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    send_from_directory,
    session,
    cli,
)
import os
from waitress import serve
import s3fs
import json

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
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

query_engine = None


def initBot(bot_id):
    PERSIST_DIR = "saaheer-chatbot-db/indexes/" + bot_id
    DATA_DIR = "saaheer-chatbot-db/client_data/" + bot_id

    if not s3.exists(PERSIST_DIR):
        # NEW
        print("NEW")

        bot_name = "Saaheer Purav"
        documents = SimpleDirectoryReader(
            input_dir="saaheer-chatbot-db/client_data/" + bot_id, fs=s3
        ).load_data()

        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(PERSIST_DIR, fs=s3)
        session["bot_name"] = bot_name

        with s3.open(DATA_DIR + "/config.json", "w") as f:
            json.dump(
                {
                    "id": bot_id,
                    "bot_name": bot_name,
                },
                f,
            )
    else:
        # EXISTING
        print("EXISTING")

        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR, fs=s3)
        index = load_index_from_storage(storage_context)

        with s3.open(DATA_DIR + "/config.json", "r") as f:
            session["bot_name"] = json.load(f)["bot_name"]

    global query_engine
    query_engine = index.as_query_engine()


@app.route("/init-llm", methods=["POST"])
def init_llm():
    bot_id = request.args.get("id")
    session["bot_id"] = bot_id
    initBot(bot_id)

    return jsonify({"status": 200, "bot_name": session["bot_name"]})


@app.route("/chatbot-iframe")
def main():
    return render_template("index.html")


@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.json
    user_message = data.get("message")
    response = query_engine.query(user_message)

    return jsonify({"response": str(response)})


@app.route("/static/css")
def send_css():
    return send_from_directory("static" + os.sep + "css", "output.css")


if __name__ == "__main__":
    if app.config["ENV"] == "dev":
        app.run(debug=True)

    elif app.config["ENV"] == "prod":
        serve(app, host="0.0.0.0", port=8080)
