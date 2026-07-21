from litellm import completion
import config

def get_ollama_stream(model_name, conversation_history, fresh_prompt):
    """
    Combines database conversation history with the new user prompt,
    and returns a streaming completion response from the local Ollama server (via litellm).
    """
    # Create the complete payload containing past interactions + current question
    payload = conversation_history + [{"role": "user", "content": fresh_prompt}]

    return completion(
        model=f"ollama/{model_name}",
        messages=payload,
        api_base=config.OLLAMA_API_BASE,
        stream=True
    )

def parse_stream_chunks(raw_stream):
    """
    A generator function that cleanly yields incoming word content text chunks
    from the raw litellm stream response.
    """
    for chunk in raw_stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content
