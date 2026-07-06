from litellm import completion

MODEL_PATH = "ollama/gemma4:e2b"
OLLAMA = "http://localhost:11434" 

def response(user_input):
    response = completion(
        model = MODEL_PATH,
        messages = [{"content": user_input, "role": "user"}],
        api_base = OLLAMA
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print(response("Say hello in one sentence"))