from flask import Flask, request, jsonify, render_template
import os
# Assuming your chatbot logic is in chatbot.py
# We'll refine the interaction with chatbot.py later if needed.
# For now, let's import the necessary functions.
# Make sure chatbot.py handles Gemini initialization using environment variables.
import chatbot 

app = Flask(__name__)

# Ensure Gemini is configured (chatbot.py should handle this on import)
# chatbot.model will be None if API key is not set.

@app.route('/')
def index():
    # We'll create templates/index.html in the next step
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    user_message = data.get('message')
    client_history = data.get('history', []) # History from client

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Construct the context for the chatbot
    # The chatbot.answer_question expects context['conversation_history']
    # to be a list of strings with "User: " and "Bot: " prefixes.
    # The client_history is expected to be an array of objects like:
    # [{role: 'user', text: '...'}, {role: 'model', text: '...'}]
    # We need to convert client_history to the format chatbot.answer_question expects.
    
    conversation_for_chatbot = []
    for entry in client_history:
        if entry.get('role') == 'user':
            conversation_for_chatbot.append(f"User: {entry.get('text')}")
        elif entry.get('role') == 'model': # 'model' is used by Gemini, front-end might use 'bot'
            conversation_for_chatbot.append(f"Bot: {entry.get('text')}")
    
    # Add current user message to this history before passing to answer_question
    # This matches how the chat() function in chatbot.py constructs history:
    # current user input is appended before answer_question is called.
    conversation_for_chatbot.append(f"User: {user_message}")

    context = {'conversation_history': conversation_for_chatbot}
    
    # Call the chatbot's answer function
    # It's assumed that chatbot.answer_question takes the user_message 
    # (which it uses for its internal logic like "what was my last question?")
    # and the full context (including the latest user_message).
    # chatbot.answer_question internally uses context['conversation_history'][:-1] for Gemini history.
    bot_response_text = chatbot.answer_question(user_message, context)
    
    return jsonify({'response': bot_response_text})

if __name__ == '__main__':
    # Ensure the GEMINI_API_KEY is loaded by chatbot.py when it's imported.
    # Flask's reloader might affect when chatbot.py's global code (API key check) runs.
    # It's generally fine as imports happen per worker process.
    app.run(debug=True) # debug=True is fine for development
