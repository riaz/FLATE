"""

Sample bot that echoes back messages.

This is the simplest possible bot and a great place to start if you want to build your own bot.

"""

from __future__ import annotations

import json
import os

import fastapi_poe as fp
from firebase_admin import credentials, db

from typing import AsyncIterable

from modal import Image, Stub, asgi_app

from yt_summarizer_bot import YTSummarizerBot

os.environ["FIREBASE_KEY_JSON"] = "converse-2017-firebase-adminsdk-2ch7k-b91a67f591.json"

class EchoBot(fp.PoeBot):
    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        last_message = request.query[-1].content
        last_message = "Riaz Says " + last_message
        yield fp.PartialResponse(text=last_message)


REQUIREMENTS = ["fastapi-poe==0.0.36"]
image = Image.debian_slim().pip_install(*REQUIREMENTS)
stub = Stub("echobot-poe")


@stub.function(image=image)
@asgi_app()
def fastapi_app():
    #bot = EchoBot()
    bot = YTSummarizerBot()
    cred = credentials.Certificate(json.loads(os.environ["FIREBASE_KEY_JSON"]))
    firebase_admin.initialize_app(
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
    app = fp.make_app(bot, allow_without_key=True)
    return app
