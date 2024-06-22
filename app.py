from flask import Flask, request, jsonify, render_template, send_from_directory, session, cli
import os
import json
import s3fs
from waitress import serve
#from paste.translogger import TransLogger

from llama_index.legacy import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    ServiceContext,
    load_index_from_storage,
)

#pipenv install -r requirements.txt
# from llama_index.legacy.evaluation import FaithfulnessEvaluator
from llama_index.legacy.llms.openai import OpenAI

cli.load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# ============ SET dev OR prod ============
app.config["ENV"] = "prod"
# =========================================

s3 = s3fs.S3FileSystem(
    key=os.environ.get("AWS_KEY"),
    secret=os.environ.get("AWS_SECRET"),
    s3_additional_kwargs={"ACL": "public-read"},
)

# evaluator, query_engine = None, None
query_engine = None



def initBot(bot_id):
    PERSIST_DIR = "saaheer-chatbot-db/" + bot_id
    bot_name = "Saaheer Purav"

    if not s3.exists(PERSIST_DIR):
        # NEW
        print("NEW")
        documents = SimpleDirectoryReader("client_data/" + bot_id).load_data()
        service_context = ServiceContext.from_defaults(
            llm=OpenAI(temperature=0.3, model_name="gpt-3.5-turbo-0125")
        )
        # ServiceContext.from_defaults(chunk_size_limit=512),
        index = VectorStoreIndex.from_documents(
            documents, service_context=service_context
        )
        index.storage_context.persist(PERSIST_DIR, fs=s3)
        session["bot_name"] = bot_name

        with s3.open(PERSIST_DIR + "/config.json", "w") as f:
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

        with s3.open(PERSIST_DIR + "/config.json", "r") as f:
            session["bot_name"] = json.load(f)["bot_name"]

    """service_context = ServiceContext.from_defaults(
        llm=OpenAI(temperature=0.3, model_name="gpt-3.5-turbo-0125")
    )

    global evaluator
    evaluator = FaithfulnessEvaluator(service_context=service_context)"""

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

    # eval_result = evaluator.evaluate_response(response=response)
    # print(eval_result)

    return jsonify({"response": str(response)})

    """eval_result = evaluator.evaluate_response(response=response)

    if eval_result.passing:
        return jsonify({"response": str(response)})
    else:
        return jsonify(
            {
                "response": "I'm sorry as I can only answer questions relating to Saaheer Purav."
            }
        )"""



@app.route("/static/css")
def send_css():
    return send_from_directory("static" + os.sep + "css", "output.css")



if __name__ == "__main__":
    if app.config["ENV"] == "dev":
        app.run(debug=True)

    elif app.config["ENV"] == "prod":
        serve(app, host="0.0.0.0", port=8080)
        #serve(TransLogger(app, setup_console_handler=False), host="0.0.0.0", port=8080)
