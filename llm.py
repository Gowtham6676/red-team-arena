import json, time
import ollama

MODEL = "llama3.2:3b"

def ask(prompt, system=None, as_json=False, temperature=0.7, retries=3):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    for attempt in range(retries):
        try:
            r = ollama.chat(
                model=MODEL,
                messages=messages,
                format="json" if as_json else None,
                options={"temperature": temperature},
            )
            text = r["message"]["content"]
            return json.loads(text) if as_json else text
        except Exception as e:
            print(f"  [retry {attempt + 1}] {e}")
            time.sleep(1)
    return None