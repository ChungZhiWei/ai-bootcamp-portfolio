import sys
sys.stdout.reconfigure(encoding="utf-8")  # Windows console defaults to cp1252, which can't print emoji

from litellm import completion

# Configuration
MODEL = "ollama/gemma4:e2b"  # Change this to whatever model you have pulled locally
OLLAMA = "http://localhost:11434"

def main():
    # Initialize session state (conversation history)
    # The system prompt sets the behavior of the AI
    messages = [
        {
            'role': 'system',
            'content': 'You are a helpful, witty, and concise AI assistant.'
        }
    ]

    print("=" * 60)
    print(f"Local Ollama Chatbot Initialized (Model: {MODEL})")
    print("Type your question and press Enter. Type 'exit' or 'quit' to end.")
    print("=" * 60)

    while True:
        try:
            # 1. Get user input
            user_input = input("\nYou: ").strip()

            # Check for exit commands
            if user_input.lower() in ['exit', 'quit']:
                print("\nGoodbye! Thanks for chatting.")
                break

            if not user_input:
                continue

            # 2. Append user message to the session state
            messages.append({'role': 'user', 'content': user_input})

            print("AI: Thinking...", end="\r", flush=True)

            # 3. Call local Ollama (via litellm) with the entire message history
            response = completion(
                model=MODEL,
                messages=messages,
                api_base=OLLAMA,
                stream=True  # Enables word-by-word streaming response
            )

            # 4. Stream the response to the console and capture full text
            print("AI: ", end="", flush=True)
            full_response = ""

            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
                    full_response += content
            print()  # Print a new line at the end

            # 5. Append the AI's response to the session state for next turn
            messages.append({'role': 'assistant', 'content': full_response})

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please ensure your local Ollama server is running (usually at http://localhost:11434).")
            break

if __name__ == "__main__":
    main()
