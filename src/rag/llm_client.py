import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class LLMClient:

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model="gpt-5-mini",
            input=prompt,
        )

        return response.output_text


if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set")

    llm_client = LLMClient(
        api_key=api_key,
    )

    result = llm_client.generate(
        "What is 2 + 2?"
    )

    print(result)
