from groq import Groq
from config import ANTHROPIC_API_KEY

client = Groq(api_key=ANTHROPIC_API_KEY)

def call_claude(system_prompt, user_message):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=1000,
    )
    return response.choices[0].message.content

def call_claude_json(system_prompt, user_message):
    json_instruction = "\n\nIMPORTANT: Respond ONLY with valid JSON. No preamble, no explanation, no markdown backticks."
    return call_claude(system_prompt + json_instruction, user_message)
