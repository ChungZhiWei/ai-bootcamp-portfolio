import streamlit as st
import config
from database.db_manager import init_db, get_sessions, create_session, save_message, get_chat_history
from services.llm_service import get_ollama_stream, parse_stream_chunks

# Initialize Web App Layout & DB Tables
st.set_page_config(page_title="Ollama SQLite Chatbot", layout="wide")
init_db()

# Track which chat window is actively viewed
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

# Sidebar Interface Component
with st.sidebar:
    st.title("💬 Chat History")

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_session_id = create_session()
        st.rerun()

    st.divider()

    # Dynamically draw past chat thread selectors
    sessions = get_sessions()
    for s_id, s_title in sessions:
        if st.button(s_title, key=f"session_{s_id}", use_container_width=True):
            st.session_state.current_session_id = s_id
            st.rerun()

    st.sidebar.divider()
    model_name = st.sidebar.text_input("Ollama Model", value=config.DEFAULT_MODEL)

# Main Chat View Window
st.title("Local LLM Chat")

if st.session_state.current_session_id is None:
    st.info("Start a new chat or select history from the sidebar.")
else:
    # Query database records through the persistence layer
    chat_history = get_chat_history(st.session_state.current_session_id)

    # Render chat elements on UI layout
    for message in chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Process new prompt input
    if prompt := st.chat_input("How can I help you?"):
        with st.chat_message("user"):
            st.markdown(prompt)

        # Save user interaction directly to database record
        save_message(st.session_state.current_session_id, "user", prompt)

        # Build streaming output visual structure
        with st.chat_message("assistant"):
            try:
                # Call the Infrastructure Service to fetch the streaming response
                raw_stream = get_ollama_stream(model_name, chat_history, prompt)
                clean_text_stream = parse_stream_chunks(raw_stream)

                # Stream out directly to user interface using native write_stream
                full_response = st.write_stream(clean_text_stream)

                # Write final fully compiled response to database record
                save_message(st.session_state.current_session_id, "assistant", full_response)

            except Exception as e:
                st.error(f"Error: {str(e)}. Ensure Ollama server is operational via `ollama serve`.")
