from flask import Flask, request, jsonify, render_template, send_from_directory, session
import os
import uuid
import json
import s3fs
from llama_index.legacy import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    ServiceContext,
    load_index_from_storage,
)
from llama_index.legacy.evaluation import FaithfulnessEvaluator
from llama_index.legacy.llms.openai import OpenAI

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

s3 = s3fs.S3FileSystem(
    key=os.environ.get("AWS_KEY"),
    secret=os.environ.get("AWS_SECRET"),
    s3_additional_kwargs={"ACL": "public-read"},
)

evaluator, query_engine = None, None


def initBot(bot_id):
    PERSIST_DIR = "saaheer-chatbot-db/" + bot_id

    if not s3.exists(PERSIST_DIR):
        # NEW
        print("NEW")
        documents = SimpleDirectoryReader("client_data/" + bot_id).load_data()
        index = VectorStoreIndex.from_documents(
            documents,
            service_context=ServiceContext.from_defaults(chunk_size_limit=512),
        )
        index.storage_context.persist(PERSIST_DIR, fs=s3)

        with s3.open(PERSIST_DIR + "/config.json", "w") as f:
            json.dump(
                {
                    "id": bot_id,
                    "bot_name": "Saaheer Purav",
                },
                f,
            )
    else:
        # EXISTING
        print("EXISTING")
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR, fs=s3)
        index = load_index_from_storage(storage_context)

        with s3.open(PERSIST_DIR + "/config.json", "r") as f:
            session["bot_name"] = json.load(f)["bot_name"]

    service_context = ServiceContext.from_defaults(
        llm=OpenAI(temperature=0, model_name="gpt-3.5-turbo-0125")
    )

    global evaluator
    evaluator = FaithfulnessEvaluator(service_context=service_context)

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
    eval_result = evaluator.evaluate_response(response=response)

    if eval_result.passing:
        return jsonify({"response": str(response)})
    else:
        return jsonify(
            {
                "response": "I'm sorry as I can only answer questions relating to Saaheer Purav."
            }
        )


@app.route("/static/css/<path:path>")
def send_css(path):
    return send_from_directory("static/css", path)


if __name__ == "__main__":
    app.run(debug=True)
