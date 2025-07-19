import streamlit as st
import requests
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="CodeMaster Chatbot",
    page_icon="🤖",
    layout="centered"
)

# --- Backend API URL ---
BACKEND_URL = "http://127.0.0.1:8000/generate"

# --- App Title and Description ---
st.title("🤖 CodeMaster Chatbot")
st.caption("Your Expert AI Programming Assistant")

# --- API Key Input in Sidebar ---
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your Gemini API Key", type="password")
    if not api_key:
        st.warning("Please enter your Gemini API Key to start the chat.")
        st.stop()

# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input ---
if prompt := st.chat_input("Ask me anything about coding..."):
    # Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare data for backend request
    # Reformat history for the backend Pydantic model
    history_for_api = []
    for msg in st.session_state.messages[:-1]: # Exclude the current user prompt
        history_for_api.append({
            "role": msg["role"],
            "parts": [msg["content"]]
        })

    payload = {
        "api_key": api_key,
        "prompt": prompt,
        "history": history_for_api
    }

    # --- Get AI Response ---
    with st.chat_message("assistant"):
        with st.spinner("CodeMaster is thinking..."):
            try:
                # Send request to backend
                response = requests.post(BACKEND_URL, json=payload)
                response.raise_for_status()  # Raise an exception for bad status codes

                # Extract and display the response
                backend_response = response.json()
                if "response" in backend_response:
                    ai_response = backend_response["response"]
                    st.markdown(ai_response)
                    # Add AI response to session state
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                else:
                    error_message = backend_response.get("error", "An unknown error occurred.")
                    st.error(f"Error from backend: {error_message}")

            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the backend: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")