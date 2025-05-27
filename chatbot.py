# Main file for the chatbot functionality.

import os
import random
import google.generativeai as genai
# It's good practice to also import specific exceptions if you know them
# from google.api_core.exceptions import GoogleAPIError (example, adjust based on actual exceptions)

# 1. Imports and Configuration
API_KEY = os.environ.get('GEMINI_API_KEY')
model = None # Initialize model to None

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-pro') 
        print("Gemini API configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        model = None # Ensure model is None if configuration fails
else:
    print("GEMINI_API_KEY environment variable not found. Gemini features will be disabled.")

# --- Existing GREETINGS and greet_user() ---
GREETINGS = [
    "Hello!",
    "Hi there!",
    "Welcome! How can I help you today?",
    "Greetings!",
    "Hey! What can I do for you?",
]

def greet_user():
  """Returns a random greeting message."""
  return random.choice(GREETINGS)

# --- Simplified RESPONSES dictionary (lowercase keys) ---
RESPONSES = {
    "hello": "Hello there! How can I help you?",
    "hi": "Hi! What can I do for you?",
    "bye": "Goodbye! Have a great day!",
    "thanks": "You're welcome!",
    "goodbye": "Goodbye! See you next time!",
    "name": "I am a friendly chatbot, now powered by Gemini for advanced queries!",
}

# --- get_gemini_response function (remains unchanged from previous correct version) ---
def get_gemini_response(prompt, conversation_history):
    """
    Gets a response from the Gemini API.
    conversation_history is a list of strings like ["Bot: Greeting", "User: Q1", "Bot: A1"]
    It should contain the history *before* the current prompt.
    """
    if model is None:
        return "Gemini API is not configured. Please set the GEMINI_API_KEY environment variable."

    gemini_history = []
    for message_entry in conversation_history:
        cleaned_message = ""
        role = ""
        if message_entry.startswith("User: "):
            role = "user"
            cleaned_message = message_entry.replace("User: ", "", 1)
        elif message_entry.startswith("Bot: "):
            role = "model"
            cleaned_message = message_entry.replace("Bot: ", "", 1)
        else: 
            if not gemini_history: 
                role = "model"
            else: 
                role = "user" 
            cleaned_message = message_entry
        
        if cleaned_message.strip():
            gemini_history.append({"role": role, "parts": [cleaned_message]})
        else:
            print(f"Warning: Skipped empty message in history construction: '{message_entry}'")

    try:
        chat_session = model.start_chat(history=gemini_history)
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e: 
        print(f"Error calling Gemini API: {e}")
        return "Sorry, I encountered an error trying to reach the Gemini API."

# --- Modified answer_question function (NEW LOGIC) ---
def answer_question(user_input, context):
    user_input_lower = user_input.lower() # Ensure it's lowercased once

    # 1. Handle direct local context queries FIRST
    if user_input_lower in ["what was my last question?", "repeat my last statement"]:
        # Ensure context and conversation_history exist and are not empty
        if context and isinstance(context.get('conversation_history'), list) and context['conversation_history']:
            # History from chat() includes the current "User: what was my last question?" as the LAST element.
            # We need to search the history *before* this current request.
            history_to_search = context['conversation_history'][:-1] 
            
            if not history_to_search: # If history only contained the current "repeat" request
                 return "I don't have enough conversation history to recall your last question."

            for i in range(len(history_to_search) - 1, -1, -1):
                if history_to_search[i].startswith("User: "):
                    # Strip "User: " prefix before returning
                    return f"You previously asked: '{history_to_search[i][6:]}'" 
            # If no "User: " message found in the preceding history (e.g., only bot messages)
            return "I can't find a previous question from you in the history."
        else:
            # context is missing or conversation_history is not a list or is empty
            return "I don't have enough conversation history to recall your last question."

    # 2. Check for simple predefined keywords (RESPONSES keys are already lowercase)
    for keyword, response_text in RESPONSES.items():
        if keyword in user_input_lower:
            return response_text
            
    # 3. If not a local command or simple keyword, try Gemini
    if model: # Check if Gemini model is configured
        # Pass conversation_history *excluding* the current user_input itself, 
        # as user_input is the new prompt.
        return get_gemini_response(user_input, context['conversation_history'][:-1])
    else:
        # Fallback if Gemini is not available and no other rule matched
        return "Sorry, I can only handle very basic questions right now as advanced features are disabled."


# --- Modified chat function (remains unchanged from previous correct version) ---
def chat():
    """Manages the overall conversation with the chatbot."""
    context = {'conversation_history': []}
    
    bot_greeting = greet_user()
    print(f"Bot: {bot_greeting}")
    context['conversation_history'].append(f"Bot: {bot_greeting}")

    while True:
        user_input_raw = input("You: ") 
        
        context['conversation_history'].append(f"User: {user_input_raw}")

        if user_input_raw.lower() in ["quit", "exit"]:
            print("Bot: Goodbye!")
            break
        
        bot_response = answer_question(user_input_raw, context)
        print(f"Bot: {bot_response}")
        
        context['conversation_history'].append(f"Bot: {bot_response}")

if __name__ == "__main__":
  chat()
