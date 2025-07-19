import os
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# --- Pydantic Models for Request Body ---
class ChatMessage(BaseModel):
    role: str
    parts: List[str]

class ChatRequest(BaseModel):
    api_key: str
    prompt: str
    history: List[ChatMessage]

# --- FastAPI App Initialization ---
app = FastAPI()

# Configure CORS to allow the Streamlit frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- System Prompt Definition ---
SYSTEM_PROMPT = """You are CodeMaster, an expert AI programming assistant. Your purpose is to help users with coding tasks. You are precise, knowledgeable, and helpful.

Your capabilities are:
1.  **Code Generation:** Write clean, efficient, and well-commented code.
2.  **Code Debugging:** Identify errors and provide corrected code with clear explanations.
3.  **Code Explanation:** Break down complex code into simple, easy-to-understand parts.

Your operational rules are:
-   **ALWAYS** format code blocks using Markdown. For a specific language, use the language identifier (e.g., ```python ... ```).
-   When debugging, first state the primary error (e.g., `SyntaxError`, `TypeError`), then provide the corrected code, and finally, explain *why* the error occurred and how the fix works.
-   When generating code, provide a brief explanation of how the code works either before or after the code block.
-   If a user's request is ambiguous, ask clarifying questions before generating a response.
-   Maintain a professional and encouraging tone. Do not express personal opinions.
-   Base your answers solely on the provided conversation context and your extensive knowledge base. Do not invent information."""


# --- API Endpoint ---
@app.post("/generate")
async def generate_response(request: ChatRequest):
    """
    Receives a prompt and conversation history, gets a response from Gemini, and returns it.
    """
    try:
        # Configure the generative AI library with the provided API key
        genai.configure(api_key=request.api_key)

        # Reformat history for the Gemini API
        formatted_history = []
        for message in request.history:
            formatted_history.append({
                "role": message.role,
                "parts": message.parts
            })

        # Prepend the system prompt to the history
        # Gemini works best when the system prompt is part of the first message
        if not formatted_history or formatted_history[0]['role'] != 'user':
             # If history is empty or doesn't start with a user message, prepend system prompt
             initial_prompt = f"{SYSTEM_PROMPT}\n\nHere is the first question:\n{request.prompt}"
        else:
            # If history exists, the system prompt is assumed to be part of the context
            initial_prompt = request.prompt


        # Initialize the model and start a chat session
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat = model.start_chat(history=formatted_history)

        # Send the user's prompt to the model
        response = chat.send_message(initial_prompt)

        return {"response": response.text}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}