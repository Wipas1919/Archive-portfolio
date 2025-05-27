import unittest
from unittest.mock import patch, MagicMock
import os
import importlib

# Import specific items from chatbot after potential reloads
import chatbot as initial_chatbot_module # For type hinting if needed, and initial access
# Functions will be called via reloaded_chatbot in tests.

# Helper to reload chatbot and its global 'model' variable
def reload_chatbot_module():
    # importlib.reload will re-execute chatbot.py,
    # re-initializing the global 'model' based on the current os.environ['GEMINI_API_KEY']
    return importlib.reload(initial_chatbot_module)

class TestChatbot(unittest.TestCase):

    def setUp(self):
        self.original_api_key = os.environ.get('GEMINI_API_KEY')
        # Ensure a clean slate by removing the key before each test
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        # Initial reload to ensure 'initial_chatbot_module.model' is None
        reload_chatbot_module() 
        
    def tearDown(self):
        if self.original_api_key:
            os.environ['GEMINI_API_KEY'] = self.original_api_key
        elif 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        # Reload chatbot after test to restore its model based on original_api_key or its absence
        # This also ensures the next test starts with a model based on its own setUp.
        reload_chatbot_module()

    def test_greet_user(self):
        reloaded_chatbot = reload_chatbot_module() # Not strictly necessary here, but good practice
        greeting = reloaded_chatbot.greet_user()
        self.assertIsInstance(greeting, str)
        self.assertIn(greeting, reloaded_chatbot.GREETINGS)

    def test_gemini_api_key_not_set(self):
        # API key is ensured not set by setUp and this line
        if 'GEMINI_API_KEY' in os.environ: del os.environ['GEMINI_API_KEY']
        reloaded_chatbot = reload_chatbot_module() # Ensures chatbot.model is None

        context = {'conversation_history': ["User: what is AI?"]}
        response = reloaded_chatbot.answer_question("what is AI?", context)
        # If model is None, answer_question returns its own message, not get_gemini_response's message
        self.assertEqual(response, "Sorry, I can only handle very basic questions right now as advanced features are disabled.")

    def test_simple_keywords_no_gemini(self):
        # API key can be unset or set, doesn't matter as Gemini shouldn't be called.
        # Let's ensure it's unset for consistency that Gemini is definitely not available.
        if 'GEMINI_API_KEY' in os.environ: del os.environ['GEMINI_API_KEY']
        reloaded_chatbot = reload_chatbot_module()

        with patch.object(reloaded_chatbot, 'get_gemini_response', wraps=reloaded_chatbot.get_gemini_response) as mock_get_gemini:
            context_hello = {'conversation_history': ["User: hello"]}
            response_hello = reloaded_chatbot.answer_question("hello", context_hello)
            self.assertEqual(response_hello, reloaded_chatbot.RESPONSES["hello"])
            mock_get_gemini.assert_not_called()

            context_bye = {'conversation_history': ["User: bye"]}
            response_bye = reloaded_chatbot.answer_question("bye", context_bye)
            self.assertEqual(response_bye, reloaded_chatbot.RESPONSES["bye"])
            mock_get_gemini.assert_not_called()
            
            context_name = {'conversation_history': ["User: what is your name?"]}
            response_name = reloaded_chatbot.answer_question("what is your name?", context_name)
            self.assertEqual(response_name, reloaded_chatbot.RESPONSES["name"])
            mock_get_gemini.assert_not_called()

    def test_complex_question_calls_gemini(self):
        os.environ['GEMINI_API_KEY'] = 'test_key_dummy' # Dummy key to make chatbot.model initialize
        reloaded_chatbot = reload_chatbot_module()    # chatbot.model will be a real model instance

        # Mock the model instance on the reloaded module
        mock_model_instance = MagicMock()
        mock_chat_session = MagicMock()
        mock_chat_session.send_message.return_value.text = "Mocked Gemini response about AI"
        mock_model_instance.start_chat.return_value = mock_chat_session

        with patch.object(reloaded_chatbot, 'model', mock_model_instance):
            context = {'conversation_history': ["User: What is AI?"]}
            response = reloaded_chatbot.answer_question("What is AI?", context)
            
            self.assertEqual(response, "Mocked Gemini response about AI")
            mock_model_instance.start_chat.assert_called_once()
            # History for get_gemini_response is context[:-1], which is empty.
            # get_gemini_response then formats this for the API.
            mock_model_instance.start_chat.assert_called_with(history=[])
            mock_chat_session.send_message.assert_called_with("What is AI?")

    def test_context_passing_to_gemini(self):
        os.environ['GEMINI_API_KEY'] = 'test_key_dummy'
        reloaded_chatbot = reload_chatbot_module()

        mock_model_instance = MagicMock()
        mock_chat_session = MagicMock()
        mock_chat_session.send_message.return_value.text = "Mocked response based on context"
        mock_model_instance.start_chat.return_value = mock_chat_session
        
        with patch.object(reloaded_chatbot, 'model', mock_model_instance):
            context = {
                'conversation_history': [
                    "Bot: Hello!", 
                    "User: Previous question", 
                    "Bot: Previous answer", 
                    "User: New question about context"
                ]
            }
            response = reloaded_chatbot.answer_question("New question about context", context)
            self.assertEqual(response, "Mocked response based on context")

            expected_gemini_history_for_api = [
                {'role': 'model', 'parts': ['Hello!']},
                {'role': 'user', 'parts': ['Previous question']},
                {'role': 'model', 'parts': ['Previous answer']}
            ]
            mock_model_instance.start_chat.assert_called_with(history=expected_gemini_history_for_api)
            mock_chat_session.send_message.assert_called_with("New question about context")

    def test_portfolio_design_calls_gemini(self):
        os.environ['GEMINI_API_KEY'] = 'test_key_dummy'
        reloaded_chatbot = reload_chatbot_module()

        mock_model_instance = MagicMock()
        mock_chat_session = MagicMock()
        mock_chat_session.send_message.return_value.text = "Mocked Gemini on portfolio design"
        mock_model_instance.start_chat.return_value = mock_chat_session

        with patch.object(reloaded_chatbot, 'model', mock_model_instance):
            user_query = "Tell me about portfolio design"
            context = {'conversation_history': [f"User: {user_query}"]}
            response = reloaded_chatbot.answer_question(user_query, context)
            
            self.assertEqual(response, "Mocked Gemini on portfolio design")
            mock_model_instance.start_chat.assert_called_with(history=[])
            mock_chat_session.send_message.assert_called_with(user_query)

    def test_portfolio_content_calls_gemini(self):
        os.environ['GEMINI_API_KEY'] = 'test_key_dummy'
        reloaded_chatbot = reload_chatbot_module()

        mock_model_instance = MagicMock()
        mock_chat_session = MagicMock()
        mock_chat_session.send_message.return_value.text = "Mocked Gemini on portfolio content"
        mock_model_instance.start_chat.return_value = mock_chat_session
        
        with patch.object(reloaded_chatbot, 'model', mock_model_instance):
            user_query = "What about portfolio content?"
            context = {'conversation_history': [f"User: {user_query}"]}
            response = reloaded_chatbot.answer_question(user_query, context)

            self.assertEqual(response, "Mocked Gemini on portfolio content")
            mock_model_instance.start_chat.assert_called_with(history=[])
            mock_chat_session.send_message.assert_called_with(user_query)

    def test_answer_question_local_context_awareness_no_gemini(self):
        # Ensure API key is not set so model is None, forcing non-Gemini paths
        if 'GEMINI_API_KEY' in os.environ: del os.environ['GEMINI_API_KEY']
        reloaded_chatbot = reload_chatbot_module() # chatbot.model is now None

        # We are testing a local rule, so Gemini should not be called.
        # We can mock get_gemini_response to be sure.
        with patch.object(reloaded_chatbot, 'get_gemini_response', wraps=reloaded_chatbot.get_gemini_response) as mock_get_gemini:
            user_q1_text = "Tell me about portfolios" # This is the raw question text
            user_q1_entry = f"User: {user_q1_text}"
            bot_r1_entry = "Bot: Portfolio suggestions..."
            current_q_text = "what was my last question?"
            current_q_entry = f"User: {current_q_text}"

            context_sufficient = {
                'conversation_history': [
                    "Bot: Hi there!",
                    user_q1_entry,
                    bot_r1_entry,
                    current_q_entry 
                ]
            }
            # The response should be based on user_q1_text (without "User: " prefix)
            expected_response_sufficient = f"You previously asked: '{user_q1_text}'" # CHANGED THIS LINE
            
            response = reloaded_chatbot.answer_question(current_q_text, context_sufficient)
            
            self.assertEqual(response, expected_response_sufficient)
            mock_get_gemini.assert_not_called()

            # Test insufficient history
            context_insufficient = {
                'conversation_history': [
                    "Bot: Hello!",
                    current_q_entry
                ]
            }
            expected_response_insufficient = "I don't have enough conversation history to recall your last question." # This fallback is from the "what was my last q" block
            # Check if current_q_text is "what was my last question?"
            # If history is only [Bot greeting, "User: what was my last q"], len(history_to_search) is 1.
            # The loop for i in range(len(history_to_search) - 1, -1, -1) -> range(0, -1, -1) will not run.
            # It should then return "I can't find a previous question from you in the history."
            # Let's trace chatbot.py for this case:
            # history_to_search = ["Bot: Hello!"]
            # loop for i in range(0, -1, -1): # Does not run
            # returns "I can't find a previous question from you in the history."

            # If history_to_search is empty (e.g. context_history was just [current_q_entry])
            # history_to_search = []
            # then it returns "I don't have enough conversation history to recall your last question."
            
            # In this test case: history_to_search = ["Bot: Hello!"]
            # So the expected message should be:
            expected_response_insufficient_actually = "I can't find a previous question from you in the history."


            response_insufficient = reloaded_chatbot.answer_question(current_q_text, context_insufficient)
            self.assertEqual(response_insufficient, expected_response_insufficient_actually) # CHANGED THIS LINE
            mock_get_gemini.assert_not_called()

if __name__ == '__main__':
    unittest.main()
