
from openai import OpenAI


client = OpenAI(api_key="sk-your_api_key_here")  

def get_ai_decision(user_text):
    prompt = f"""
You are a smart decision assistant.

User problem:
{user_text}

Return structured response in this format:

PROS:
- ...

CONS:
- ...

RECOMMENDATION:
...

CONFIDENCE: (0-100%)
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a smart decision assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠ AI service unavailable. ({str(e)})"