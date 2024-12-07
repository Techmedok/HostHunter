from bs4 import BeautifulSoup
from groq import Groq
import re
import json

def extract_json(text):
    pattern = r'```json(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return json.loads(match.group(1).strip())
    else:
        return None

def GetSiteAnalysis(content):
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    text = '\n'.join([line for line in text.splitlines() if line.strip()])

    client = Groq(api_key="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")
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[        {
                "role": "user",
                "content": f"""
                                I need the following data in JSON format:
                                    summary (Paragraphs appended in String),
                                    keywords (array),
                                    site category (String)
                                I dont need any other data other than this in your output.
                                Site Contents:
                                {text}
                            """,
            }],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    return extract_json(completion.choices[0].message.content)