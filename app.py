"""
This is a Youtube Q/A Bot
"""

from __future__ import annotations

import json
import os

import fastapi_poe as fp
from firebase_admin import credentials, db, initialize_app

from typing import AsyncIterable

from modal import Image, Stub, Secret, asgi_app

from yt_qa_bot import YTQABot

image = Image.debian_slim().pip_install("fastapi-poe==0.0.36", "firebase-admin==6.2.0", "youtube-transcript-api==0.6.2", "pytube==15.0.0")

stub = Stub("echobot-poe")


@stub.function(image=image, secrets=[Secret.from_name("yt-qa-secret")])
@asgi_app()
def fastapi_app():
    #bot = EchoBot()
    bot = YTQABot()
    print(os.environ["FIREBASE_KEY_JSON"])
    cred = credentials.Certificate(json.loads(os.environ["FIREBASE_KEY_JSON"]))
    initialize_app(
        cred, {"databaseURL": "https://converse-2017-default-rtdb.firebaseio.com/"}
    )
    # Optionally, provide your Poe access key here:
    # 1. You can go to https://poe.com/create_bot?server=1 to generate an access key.
    # 2. We strongly recommend using a key for a production bot to prevent abuse,
    # but the starter examples disable the key check for convenience.
    # 3. You can also store your access key on modal.com and retrieve it in this function
    # by following the instructions at: https://modal.com/docs/guide/secrets
    # POE_ACCESS_KEY = ""
    # app = make_app(bot, access_key=POE_ACCESS_KEY)
    app = fp.make_app(bot, access_key=os.environ["BOT_KEY"])
    return app

