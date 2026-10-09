import os

from src.ai.common.llm.base_proxy import BaseProxy
from openai import OpenAI
from langchain_groq import ChatGroq

class Groq(BaseProxy):
    _client = None

    def __init__(self):
        if Groq._client is None:
            Groq._client = OpenAI(
                api_key=os.environ.get("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
            )


    def invoke(self, input):
        payload = input
        if isinstance(payload, str):
            payload = [{"role": "user", "content": payload}]
        elif isinstance(payload, dict):
            payload = [payload]
        elif isinstance(payload, tuple):
            payload = list(payload)

        for message in payload:
            if not isinstance(message, dict):
                raise TypeError("Groq message payload must be a string, dict, or list of dicts.")
            if "role" not in message:
                message["role"] = "user"
            if "content" not in message:
                message["content"] = ""

        response = Groq._client.responses.create(
            input=payload,
            model="openai/gpt-oss-120b",
        )
        return response.output_text


    def get_langchain_model(self):
        return ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
        )