import json
from urllib import error, request


def _post_json(url, payload, timeout=60):
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.URLError as exc:
        raise ConnectionError(
            f"Could not reach {url}. Start the Ollama server with `ollama serve` or open the Ollama app, then try again."
        ) from exc


def generate_with_ollama(prompt, model="llama3:latest"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = _post_json("http://localhost:11434/api/generate", payload)
    except ConnectionError:
        raise

    if "error" in response:
        raise ValueError(response["error"])

    return response.get("response", "").strip()


def generate_with_lm_studio(prompt, model="local-model"):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    response = _post_json("http://localhost:1234/v1/chat/completions", payload)
    choices = response.get("choices", [])
    if not choices:
        raise ValueError("LM Studio returned no choices.")
    return choices[0]["message"]["content"].strip()
