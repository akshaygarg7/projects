import os

from openai import OpenAI
from src.ai.common.llm.base_proxy import BaseProxy

MODEL = "gpt-5.6-luna"

class OpenAiProxy(BaseProxy):
    def __init__(self):
        self.client = OpenAI()

    def invoke(self, input):
        try:
            response = self.client.responses.create(
                model=MODEL,
                input=input,
            )

            print(response.output_text)

            return response.output_text
        except Exception as e:
            print(f"falied - {e}")
            return None