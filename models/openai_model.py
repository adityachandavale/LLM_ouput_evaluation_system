import os


def generate_with_openai(prompt, model="gpt-4.1-mini"):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Set the OPENAI_API_KEY environment variable to use OpenAI.")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError("Install the `openai` package to use the OpenAI option.") from exc

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=prompt,
    )
    return response.output_text
