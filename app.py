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

# from paste.translogger import TransLogger
from llama_index.legacy import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    ServiceContext,
    load_index_from_storage,
)
from llama_index.legacy.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

cli.load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# ============ SET dev OR prod ============
app.config["ENV"] = "dev"
# =========================================

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
query_engine = None


def initBot(bot_id):
    bot_name = "Saaheer Purav"
    idx_list = list(pc.list_indexes().__dict__["index_list"]["indexes"])
    exists = False

    for i in idx_list:
        if bot_id in i.__dict__["_data_store"].values():
            exists = True
    
    if exists is True:
        print("EXISTS")
        pinecone_index = pc.Index(bot_id)
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        index = VectorStoreIndex.from_vector_store(vector_store)
    
    else:
        print("NEW")
        pc.create_index(
            name=bot_id,
            dimension=1536,
            metric="euclidean",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        pinecone_index = pc.Index(bot_id)
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        documents = SimpleDirectoryReader("client_data/" + bot_id).load_data()
        index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

    global query_engine
    query_engine = index.as_query_engine()
    session["bot_name"] = bot_name



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



@app.route("/static/css")
def send_css():
    return send_from_directory("static" + os.sep + "css", "output.css")


if __name__ == "__main__":
    if app.config["ENV"] == "dev":
        app.run(debug=True)

    elif app.config["ENV"] == "prod":
        serve(app, host="0.0.0.0", port=8080)
        # serve(TransLogger(app, setup_console_handler=False), host="0.0.0.0", port=8080)
