import streamlit as st
import config
from services.ollama_service import get_ai_response_stream, parse_stream_chunks

# Page configuration and layout
st.set_page_config(page_title="Ollama Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 Local Ollama Chatbot")
st.caption(f"Running locally with model: **{config.MODEL_NAME}**")
st.markdown("---")

# 1. Initialize UI Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {'role': 'system', 'content': config.SYSTEM_PROMPT}
    ]

# 2. Render Existing Chat History
for msg in st.session_state.messages:
    if msg['role'] != 'system':
        with st.chat_message(msg['role']):
            st.write(msg['content'])

# 3. Accept User Interaction
if user_input := st.chat_input("Type your question here..."):

    # Render user query
    with st.chat_message("user"):
        st.write(user_input)

    # Track query in history
    st.session_state.messages.append({'role': 'user', 'content': user_input})

    # 4. Generate AI Response using Service Layer Functions
    with st.chat_message("assistant"):
        try:
            # Call the service function to get the network stream
            raw_stream = get_ai_response_stream(st.session_state.messages)

            # Call the formatting function to parse text on the fly
            clean_text_stream = parse_stream_chunks(raw_stream)

            # Stream directly to the UI container
            full_response = st.write_stream(clean_text_stream)

            # Save the final text string back to history
            st.session_state.messages.append({'role': 'assistant', 'content': full_response})

        except Exception as e:
            st.error(f"Error communicating with backend: {e}")
            st.info("Ensure Ollama is running locally via `ollama serve` in your terminal.")
