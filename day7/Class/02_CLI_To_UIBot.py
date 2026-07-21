import streamlit as st
from litellm import completion

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Ollama Chatbot", page_icon="🤖", layout="centered")

MODEL = "ollama/gemma4:e2b"  # Change this to whatever model you have pulled locally
OLLAMA = "http://localhost:11434"

st.title("🤖 Local Ollama Chatbot")
st.caption(f"Running locally with model: **{MODEL}**")
st.markdown("---")

# --- 1. INITIALIZE SESSION STATE ---
# Because Streamlit reruns the script from top to bottom on every interaction,
# we store the history in st.session_state so it survives the reruns.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            'role': 'system',
            'content': 'You are a helpful, witty, and concise AI assistant.'
        }
    ]

# --- 2. DISPLAY CONVERSATION HISTORY ---
# Iterate through past messages and render them using Streamlit's native chat UI elements.
# We skip the 'system' message visually so the user doesn't see the underlying prompt.
for msg in st.session_state.messages:
    if msg['role'] != 'system':
        with st.chat_message(msg['role']):
            st.write(msg['content'])

# --- 3. HANDLE NEW USER INPUT ---
# st.chat_input creates a sticky input box at the bottom of the screen.
if user_input := st.chat_input("Type your question here..."):

    # Render user's message immediately on screen
    with st.chat_message("user"):
        st.write(user_input)

    # Append user's message to the persistent session history
    st.session_state.messages.append({'role': 'user', 'content': user_input})

    # --- 4. CALL LOCAL OLLAMA (VIA LITELLM) & STREAM RESPONSE ---
    with st.chat_message("assistant"):
        try:
            # We call litellm directly inside the block, just like the CLI version
            response_stream = completion(
                model=MODEL,
                messages=st.session_state.messages,
                api_base=OLLAMA,
                stream=True
            )

            # Helper generator to feed individual word chunks directly into st.write_stream
            def stream_parser():
                for chunk in response_stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content

            # st.write_stream automatically handles the typing effect and aggregates the full string
            full_response = st.write_stream(stream_parser())

            # Append the completed AI response to the history for the next turn
            st.session_state.messages.append({'role': 'assistant', 'content': full_response})

        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Please ensure your local Ollama server is running (usually at http://localhost:11434). Run `ollama serve` in your terminal.")
