document.addEventListener('DOMContentLoaded', () => {
    const chatDisplay = document.getElementById('chat-display');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');

    // Stores conversation history: [{role: 'user'/'model', text: '...'}, ...]
    let conversationHistory = []; 

    // Function to append a message to the chat display
    function appendMessage(role, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', role === 'user' ? 'user-message' : 'bot-message');
        messageDiv.textContent = text;
        chatDisplay.appendChild(messageDiv);
        // Scroll to the bottom
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }

    // Function to send message to backend and get response
    async function sendMessage() {
        const userMessageText = userInput.value.trim();
        if (userMessageText === '') return;

        // Display user's message
        appendMessage('user', userMessageText);
        
        // Add to internal history for sending to backend
        // The backend expects history of previous turns, not including the current user message.
        // The current user_message is sent separately.
        const historyForBackend = conversationHistory.map(entry => ({
            role: entry.role,
            text: entry.text // Or 'parts': [entry.text] if Gemini prefers that structure via backend
        }));

        // Add user's current message to local history *after* preparing historyForBackend
        conversationHistory.push({ role: 'user', text: userMessageText });
        userInput.value = ''; // Clear input field

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessageText,
                    history: historyForBackend // Send history *before* this message
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error from server:', errorData);
                appendMessage('bot', `Error: ${errorData.error || 'Failed to get response'}`);
                return;
            }

            const data = await response.json();
            const botMessageText = data.response;

            // Display bot's message
            appendMessage('bot', botMessageText);
            // Add bot's message to local history
            conversationHistory.push({ role: 'model', text: botMessageText });

        } catch (error) {
            console.error('Failed to send message:', error);
            appendMessage('bot', 'Error: Could not connect to the server.');
        }
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Optional: Initial greeting from the bot when the page loads
    // This would require a new endpoint or a modification to the /api/chat endpoint
    // to handle an initial "greeting" request, or the bot can send a greeting
    // when it receives an empty history and a common first message like "hi".
    // For simplicity, we can let the user initiate.
    // Or, send a predefined greeting on load:
    appendMessage('bot', 'Hello! How can I help you today?');
    conversationHistory.push({ role: 'model', text: 'Hello! How can I help you today?' });

});
