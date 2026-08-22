import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ.get("LLM_BASE_URL"),
    api_key=os.environ.get("LLM_API_KEY"),
)

response = client.chat.completions.create(
    model=os.environ.get("LLM_MODEL"),
    messages=[
        {"role": "user", "content": "Reply with exactly the word: ready"}
    ],
)

print(response.choices[0].message.content)