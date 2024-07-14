from flask import session
import json
import os
import s3fs
import re

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
bot_cache = {}


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
        bot_cache[bot_id] = {"bot_id": bot_id, "storage_context": storage_context}

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
    bot_data = bot_cache[bot_id]

    storage_context = bot_data["storage_context"]
    index = load_index_from_storage(storage_context)

    query_engine = index.as_query_engine()
    response = query_engine.query(user_input)

    return response


def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)
