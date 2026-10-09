import os

from src.ai.common.llm.base_proxy import BaseProxy
from google import genai

class Gemini(BaseProxy):

    _client = None

    def __init__(self):
        if Gemini._client == None:
            Gemini._client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

    def invoke(self, input):
        if isinstance(input, list):
            prompt = "\n".join(
                f"{message['role']}: {message['content']}" for message in input
            )
        else:
            prompt = input

        interaction = Gemini._client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        return interaction.output_text

