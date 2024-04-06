"""

BOT_NAME="KnowledgeTest"; modal deploy --name $BOT_NAME bot_${BOT_NAME}.py; curl -X POST https://api.poe.com/bot/fetch_settings/$BOT_NAME/$POE_ACCESS_KEY

There are three states in the conversation
- Before getting the problem
- After getting the problem, before making a submission
- After making a submission
"""

from __future__ import annotations

import re
from typing import AsyncIterable

import fastapi_poe as fp
import pandas as pd
from fastapi_poe.types import PartialResponse, ProtocolMessage
from modal import Dict, Image, Stub, asgi_app

stub = Stub("poe-bot-KnowledgeTest")
stub.my_dict = Dict.new()

df = pd.read_csv("mmlu.csv")
# using https://huggingface.co/datasets/cais/mmlu
# from datasets import load_dataset
# dataset = load_dataset("cais/mmlu", "all")
# df["subject"] = [" ".join(word.capitalize() for word in subject.split("_")) for subject in df["subject"]]
# df["option_1"] = [choices[0] for choices in df["choices"]]
# df["option_2"] = [choices[1] for choices in df["choices"]]
# df["option_3"] = [choices[2] for choices in df["choices"]]
# df["option_4"] = [choices[3] for choices in df["choices"]]
# df = df.drop("choices", axis=1)
# dataset["test"].data.to_pandas()

TEMPLATE_STARTING_REPLY = """
{question}
""".strip()

# You will test the user the following questions from the subject {subject}

FREEFORM_SYSTEM_PROMPT = """
You will test the user the following questions

{question}

The options are
1) {option_1}
2) {option_2}
3) {option_3}
4) {option_4}

The correct answer is option {answer}.

You will explain why the user is wrong or correct, and continue the conversation in a helpful manner.
"""

SUGGESTED_REPLIES_SYSTEM_PROMPT = """
You will suggest replies based on the conversation given by the user.
"""

SUGGESTED_REPLIES_USER_PROMPT = """
Read the conversation above.

Suggest three concise questions the user would ask to learn more about the topic.

Begin each suggestion with <a> and end each suggestion with </a>.
Do not use inverted commas. Do not prefix each suggestion.
""".strip()

PASS_STATEMENT = "I will pass this question."

NEXT_STATEMENT = "I want another question."

SUGGESTED_REPLIES_REGEX = re.compile(r"<a>(.+?)</a>", re.DOTALL)


def extract_suggested_replies(raw_output: str) -> list[str]:
    suggested_replies = [
        suggestion.strip() for suggestion in SUGGESTED_REPLIES_REGEX.findall(raw_output)
    ]
    return suggested_replies


def stringify_conversation(messages: list[ProtocolMessage]) -> str:
    stringified_messages = ""

    for message in messages:
        # NB: system prompt is intentionally excluded
        if message.role == "bot":
            stringified_messages += f"User: {message.content}\n\n"
        else:
            stringified_messages += f"Character: {message.content}\n\n"
    return stringified_messages


def get_conversation_info_key(conversation_id):
    assert conversation_id.startswith("c")
    return f"KnowledgeTest-question-{conversation_id}"


class GPT35TurboAllCapsBot(fp.PoeBot):
    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        conversation_info_key = get_conversation_info_key(request.conversation_id)
        last_user_reply = request.query[-1].content
        print(last_user_reply)

        # reset if the user passes or asks for the next statement
        if last_user_reply in (NEXT_STATEMENT, PASS_STATEMENT):
            if conversation_info_key in stub.my_dict:
                stub.my_dict.pop(conversation_info_key)

        # for new conversations, sample a problem
        if conversation_info_key not in stub.my_dict:
            question_info = df.sample(n=1).to_dict(orient="records")[0]
            stub.my_dict[conversation_info_key] = question_info

            yield self.text_event(
                TEMPLATE_STARTING_REPLY.format(                    
                    question=question_info["prompt"],
                )
            )

            yield PartialResponse(
                text=f"1) {question_info['A']}", is_suggested_reply=True
            )
            yield PartialResponse(
                text=f"2) {question_info['B']}", is_suggested_reply=True
            )
            yield PartialResponse(
                text=f"3) {question_info['C']}", is_suggested_reply=True
            )
            yield PartialResponse(
                text=f"4) {question_info['D']}", is_suggested_reply=True
            )

            yield PartialResponse(text=PASS_STATEMENT, is_suggested_reply=True)
            return

        # retrieve the previously cached question
        question_info = stub.my_dict[conversation_info_key]

        print(question_info["answer"])
        # continue as per normal
        request.query = [
            ProtocolMessage(
                role="system",
                content=FREEFORM_SYSTEM_PROMPT.format(
                    question=question_info["prompt"],
                    answer=question_info["answer"], # + 1,  # this is zero-indexed
                    #subject=question_info["subject"],
                    option_1=question_info["A"],
                    option_2=question_info["B"],
                    option_3=question_info["C"],
                    option_4=question_info["D"],
                ),
            )
        ] + request.query
        bot_reply = ""
        async for msg in fp.stream_request(request, "ChatGPT", request.access_key):
            bot_reply += msg.text
            yield msg.model_copy()
        print(bot_reply)

        # generate suggested replies
        request.query = request.query + [ProtocolMessage(role="bot", content=bot_reply)]
        current_conversation_string = stringify_conversation(request.query)

        request.query = [
            ProtocolMessage(role="system", content=SUGGESTED_REPLIES_SYSTEM_PROMPT),
            ProtocolMessage(role="user", content=current_conversation_string),
            ProtocolMessage(role="user", content=SUGGESTED_REPLIES_USER_PROMPT),
        ]
        response_text = ""
        async for msg in fp.stream_request(request, "ChatGPT", request.access_key):
            response_text += msg.text
        print("suggested_reply", response_text)

        suggested_replies = extract_suggested_replies(response_text)

        for suggested_reply in suggested_replies[:3]:
            yield PartialResponse(text=suggested_reply, is_suggested_reply=True)
        yield PartialResponse(text=NEXT_STATEMENT, is_suggested_reply=True)
        return

    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(
            server_bot_dependencies={"ChatGPT": 1, "GPT-3.5-Turbo": 1},
            introduction_message="Say 'start' to get a knowledge question.",
        )


REQUIREMENTS = ["fastapi-poe==0.0.24", "pandas"]
image = (
    Image.debian_slim()
    .pip_install(*REQUIREMENTS)
    .copy_local_file("mmlu.csv", "/root/mmlu.csv")
)


@stub.function(image=image)
@asgi_app()
def fastapi_app():
    bot = GPT35TurboAllCapsBot()
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