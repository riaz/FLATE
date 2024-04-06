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

TEST = '{"type": "service_account", "project_id": "converse-2017", "private_key_id": "b91a67f5917bf278c58b43b08200f7e2cfadf97d", "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDTZz3wSRH8sA+W\nC3HwcPAzGTs18m4UjAtg5Tp++R//dPevhQjU5a3UTCgimNy+q8QirAJxaqZMhbw/\njjsFkqZtYHuOUinaznNGWSaVAFJkjwtx6JhJAK+SeZ8FVsCosL2pL6cl803TtEPr\nMDG/qYKVrfmsLDNFFrq064iR8pQXBEqDYnOK14mssn7OM9o59ulfYJqFHPl71ZL5\nDI6UmHO5gPXjsSMqq2q0+14MZqHAoKj4w1JtbNfFwU3yYhF/ZlRS69uGqor8HHfU\nevqvDXu8xOGCTPjg5ggkY3d4/1MM1VnNG7vxIMWSii9NrkI9ySVJh6++ga/09UKu\nkL+Pdmz7AgMBAAECggEAKEzmsF9lp+uyVPLCmkkVaVBWis638H/QDX01fQ4l7O+R\n5ipwyBEu5alM/2dvsYOSJN/wqUlhAXZ/MAh/tOzDgFdjxnpgUz+HFzKYmdARZO0m\nC+WA3m3ciopX588ldCMZTN7yONhcjk6voe6ylSyN4dXkIk/cyD9wgVvjUZtSYt6M\nLbaEN7wlTNqhjSXF2soNH8dScJlyNNvo4AUnNvcltBwI1c/aVO3euJk6HAnS3J+l\nbYGhDnhgtHSh1T3E92/Iiz0OMLg5AKXfIc5XEewyoxN27MduA7tMKWUSZf6F0csa\nRnghAdJMbrmn44f/tJrw9Xc8ALvzoJgBR7W1EJyEAQKBgQD3hdfSP1RWDd4EqWKe\nAEDc+gS8+4HeIVBo/G5omtu2XoNw8sObOrbWcVhJZu37AWF9HAFbVlJGdy7Zby3g\nPQF2fBeO/CznCfTZHOpMMdbfz+dIFLfhxBbZXM8FN81BvH836fVjh+pRBY49hd+T\nCDbLKPyZWozLqdy4tTnhUG0Y+wKBgQDapLiFMncppDhutu32jlGn/sYDQy6NJGbn\nnnZuwYOEHAnDe1QAd8Noo+c30smpx9+HuARKyuPf3HvEHG5PVd2BdORlVtsqW2W4\nr3DxsW2isRpAbAHw3Qk25nRaGEcArd4eALrh8f3n9r6vcCvPQSf5N+3vXdyP3FS2\nXNJcFUO8AQKBgQDPntkVZkGbnS4pwtsRpSzDLoRi8KRSaqdEKNmDrMG3Czg9uaQR\nxQIwhgqEJ25fKR1ZD/CjaJjCup31jKhyezmK5TPtn+EaOuPCadqt5vBR89YQRDCp\nkw2Hba3ItrHY/f/IKtrGje8h3wMc3/pVHoK3jr2y9J09CFI4LOtL72ZTmQKBgCx8\n7cq0bQi9EHp+oEbVyImtTm8lgVhYutOQK7r3hyIfbmEnO/1oYQtupkJ2knAIalQ8\nPitVwy4ut8Q8oLll2E9aEIsKNEgXFsiQciPLnWpILPZEw9RVtWVFWRFn9TKPLi3e\nqigFTEuhqkUaRt/B+zc7iR92csWW6Gm+01LHROQBAoGBAOVl0fbmWjhQQdaTpI5l\n+SyIDbZVA+eNIAr4iMIxiUm5fVpntRrT2ZRUAZXd2soPYdficp2NRVanjJMgp9I7\nTDKqCK3PmL0Nj8+l+ePh2Y0I+x0j9H8Kz/GW+FPz83wfHLu8VnyJ0ybPmxsnorEe\nYuOG7kPfQNljqT4Pm7W8/9un\n-----END PRIVATE KEY-----\n", "client_email": "firebase-adminsdk-2ch7k@converse-2017.iam.gserviceaccount.com", "client_id": "103867503846592127947", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-2ch7k%40converse-2017.iam.gserviceaccount.com", "universe_domain": "googleapis.com"}'
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

