from flask import session
from flask_login import current_user
import json
import os
import s3fs
import re
import uuid
from .models import Users, Leads, db

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)

s3 = s3fs.S3FileSystem(
    key=os.environ.get("AWS_KEY"),
    secret=os.environ.get("AWS_SECRET"),
    s3_additional_kwargs={"ACL": "public-read"},
)

bot_cache = {
    "contexts": {},
    "client_data": {},
}


def init_bot_config(bot_id):
    DATA_DIR = "saaheer-chatbot-db/client_data/" + bot_id
    PERSIST_DIR = "saaheer-chatbot-db/indexes/" + bot_id

    if not s3.exists(DATA_DIR):
        return {
            "status": 400,
            "error": "BOT_NOT_FOUND",
        }

    else:
        if not s3.exists(PERSIST_DIR):
            # NEW
            documents = SimpleDirectoryReader(
                input_dir=DATA_DIR + "/knowledge", fs=s3
            ).load_data()
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(PERSIST_DIR, fs=s3)

        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR, fs=s3)
        bot_cache["contexts"][bot_id] = {
            "bot_id": bot_id,
            "storage_context": storage_context,
        }

        with s3.open(DATA_DIR + "/config.json", "r", encoding="utf-8") as f:
            obj = json.load(f)

            return {
                "status": 200,
                "bot_name": obj["bot_name"],
                "pic_url": obj["pic_url"],
                "welcome_message": obj["welcome_message"],
                "email_capture": obj["email_capture"],
            }


def get_bot_response(bot_id, user_input):
    bot_data = bot_cache["contexts"][bot_id]

    storage_context = bot_data["storage_context"]
    index = load_index_from_storage(storage_context)

    query_engine = index.as_query_engine()
    response = query_engine.query(user_input)

    return response


def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def get_user(email):
    return Users.query.filter_by(email=email).first()


def check_bot_exists(bot_id):
    return s3.exists("saaheer-chatbot-db/client_data/" + bot_id)


def fetch_bot_config(bot_id):
    DATA_DIR = "saaheer-chatbot-db/client_data/" + bot_id
    bot_data = {}

    if bot_id in bot_cache["client_data"]:
        bot_data = bot_cache["client_data"][bot_id]
    else:
        with s3.open(DATA_DIR + "/config.json", "r", encoding="utf-8") as f:
            bot_data = json.load(f)

        files = s3.ls(DATA_DIR + "/knowledge")
        filenames = [os.path.basename(file) for file in files]
        bot_data["knowledge"] = filenames

        bot_cache["client_data"][bot_id] = bot_data

    return bot_data


def get_bot_data(bot_id):
    if bot_id not in bot_cache["client_data"]:
        bot_data = fetch_bot_config(bot_id)
        bot_data["welcome_message"] = bot_data["welcome_message"].replace("'", r"\'")
    else:
        bot_data = bot_cache["client_data"][bot_id]

    leads = []

    for lead in Leads.query.filter_by(bot_id=bot_id).all():
        lead = lead.__dict__
        leads.append(
            {
                "email": lead["email"],
                "created_at": lead["created_at"],
            }
        )

    return {"bot_data": bot_data, "leads": leads}


def update_bot_data(bot_data):
    DATA_DIR = "saaheer-chatbot-db/client_data/" + bot_data["id"]

    with s3.open(DATA_DIR + "/config.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(bot_data, indent=4))


def delete_bot_data(bot_id):
    DATA_DIR = "saaheer-chatbot-db/client_data/" + bot_id
    PERSIST_DIR = "saaheer-chatbot-db/indexes/" + bot_id

    s3.rm(DATA_DIR, recursive=True)

    if s3.exists(PERSIST_DIR):
        s3.rm(PERSIST_DIR, recursive=True)

    current_user.bot_ids.remove(bot_id)
    db.session.commit()


def create_new_bot(bot_data):
    new_id = str(uuid.uuid4()).split("-")[0] + "-temp"
    bot_data["id"] = new_id
    current_user.bot_ids.append(new_id)
    db.session.commit()

    update_bot_data(bot_data)
    return new_id


def upload_knowledge(bot_id, file):
    DATA_DIR = "saaheer-chatbot-db/client_data/" + bot_id

    with s3.open(f"{DATA_DIR}/knowledge/{file.filename}", "wb") as f:
        f.write(file.read())


def clear_bot_cache(bot_id):
    del bot_cache["client_data"][bot_id]
    
    if bot_id in bot_cache["contexts"]:
        del bot_cache["contexts"][bot_id]
