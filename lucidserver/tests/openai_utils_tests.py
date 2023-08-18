import sys
sys.path.append('.')

import pytest
from lucidserver.database import search_dreams
from lucidserver.openai_utils import get_image_summary, generate_dream_analysis, generate_dream_image, regular_chat, call_function_by_name, search_chat_with_dreams
from unittest.mock import patch, Mock


# Mock response for text_completion function /////////////////////////////////////////////////////////////////////////////////////////////////////////////
def mock_text_completion_summary(*args, **kwargs):
    return {'text': 'Generated Summary'}

# Mock response for text_completion function for analysis
def mock_text_completion_analysis(*args, **kwargs):
    return {'text': 'Generated Analysis'}

# Mock response for text_completion function with error
def mock_text_completion_with_error(*args, **kwargs):
    return {'error': 'An error occurred'}

# Test case for successful summary generation
def test_get_image_summary_success():
    with patch('lucidserver.openai_utils.text_completion', side_effect=mock_text_completion_summary):
        dream_entry = "A mysterious dream about a forest"
        result = get_image_summary(dream_entry)
        assert result == "Generated Summary", f"Expected 'Generated Summary', but got {result}"


# Test case for summary generation with GPT-4 error
def test_get_image_summary_gpt4_error():
    with patch('lucidserver.openai_utils.text_completion', side_effect=mock_text_completion_with_error):
        dream_entry = "A mysterious dream about a forest"
        result = get_image_summary(dream_entry)
        assert result == "Error: Unable to generate a summary.", f"Expected error message, but got {result}"

# Test case for exception handling
def test_get_image_summary_exception():
    with patch('lucidserver.openai_utils.text_completion', side_effect=Exception("An unexpected exception")):
        dream_entry = "A mysterious dream about a forest"
        result = get_image_summary(dream_entry)
        assert result == "Error: Unable to generate a summary.", f"Expected error message, but got {result}"


# Mock response for text_completion function /////////////////////////////////////////////////////////////////////////////////////////////////////////////
def mock_text_completion(*args, **kwargs):
    return {'text': 'Generated Analysis'}

# Mock response for text_completion function with error
def mock_text_completion_with_error(*args, **kwargs):
    return {'error': 'An error occurred'}

# Test case for successful dream analysis generation
def test_generate_dream_analysis_success():
    with patch('lucidserver.openai_utils.text_completion', side_effect=mock_text_completion_analysis):
        prompt = "A profound dream about a journey"
        system_content = "System Content"
        result = generate_dream_analysis(prompt, system_content)
        assert result == "Generated Analysis", f"Expected 'Generated Analysis', but got {result}"

# Test case for dream analysis generation with GPT-4 error
def test_generate_dream_analysis_gpt4_error():
    with patch('lucidserver.openai_utils.text_completion', side_effect=mock_text_completion_with_error):
        prompt = "A profound dream about a journey"
        system_content = "System Content"
        result = generate_dream_analysis(prompt, system_content)
        assert result == "Error: Unable to generate a response.", f"Expected error message, but got {result}"

# Test case for exception handling in dream analysis generation
def test_generate_dream_analysis_exception():
    with patch('lucidserver.openai_utils.text_completion', side_effect=Exception("An unexpected exception")):
        prompt = "A profound dream about a journey"
        system_content = "System Content"
        result = generate_dream_analysis(prompt, system_content)
        assert result == "Error: Unable to generate a response.", f"Expected error message, but got {result}"


# Mock response for generate image function /////////////////////////////////////////////////////////////////////////////////////////////////////////////  
def mock_requests_post(*args, **kwargs):
    response_mock = Mock()
    response_mock.json.return_value = {"data": [{"url": "https://example.com/image.png"}]}
    return response_mock

# Test case for successful dream image generation
def test_generate_dream_image_success():
    with patch('lucidserver.openai_utils.get_image_summary', return_value="Generated Summary"):
        with patch('requests.post', side_effect=mock_requests_post):
            dreams = [{"id": "1", "metadata": {"entry": "A mysterious dream about a forest"}}]
            dream_id = "1"
            result = generate_dream_image(dreams, dream_id)
            assert result == "https://example.com/image.png", f"Expected image URL, but got {result}"

# Test case for dream image generation with dream not found
def test_generate_dream_image_dream_not_found():
    dreams = [{"id": "1", "metadata": {"entry": "A mysterious dream about a forest"}}]
    dream_id = "2"  # Dream ID not in the list
    result = generate_dream_image(dreams, dream_id)
    assert result is None, f"Expected None, but got {result}"

# Test case for dream image generation with error in OpenAI API response
def test_generate_dream_image_api_error():
    with patch('lucidserver.openai_utils.get_image_summary', return_value="Generated Summary"):
        with patch('requests.post', return_value=Mock(json=lambda: {})):  # No 'data' in response
            dreams = [{"id": "1", "metadata": {"entry": "A mysterious dream about a forest"}}]
            dream_id = "1"
            result = generate_dream_image(dreams, dream_id)
            assert result is None, f"Expected None, but got {result}"

# Test case for exception handling in dream image generation
def test_generate_dream_image_exception():
    with patch('lucidserver.openai_utils.get_image_summary', side_effect=Exception("An unexpected exception")):
        dreams = [{"id": "1", "metadata": {"entry": "A mysterious dream about a forest"}}]
        dream_id = "1"
        result = generate_dream_image(dreams, dream_id)
        assert result is None, f"Expected None, but got {result}"


# Mock response for regular_chat function /////////////////////////////////////////////////////////////////////////////////////////////////////////////  
def mock_chat_completion(*args, **kwargs):
    return {'text': 'Generated Chat Response'}

def mock_chat_completion_with_error(*args, **kwargs):
    return {'error': 'An error occurred'}

# Test case for successful regular chat
def test_regular_chat_success():
    with patch('lucidserver.openai_utils.chat_completion', side_effect=mock_chat_completion):
        message = "Tell me more about lucid dreaming techniques."
        user_email = "user@example.com"
        result = regular_chat(message, user_email)
        assert result == "Generated Chat Response", f"Expected 'Generated Chat Response', but got {result}"

# Test case for regular chat without user message
def test_regular_chat_default_message():
    with patch('lucidserver.openai_utils.chat_completion', side_effect=mock_chat_completion):
        message = ""
        user_email = "user@example.com"
        result = regular_chat(message, user_email)
        assert result == "Generated Chat Response", f"Expected 'Generated Chat Response', but got {result}"

# Test case for regular chat with GPT-4 error
def test_regular_chat_gpt4_error():
    with patch('lucidserver.openai_utils.chat_completion', side_effect=mock_chat_completion_with_error):
        message = "Tell me more about lucid dreaming techniques."
        user_email = "user@example.com"
        result = regular_chat(message, user_email)
        assert result == "Error: Unable to generate a response.", f"Expected error message, but got {result}"

# Test case for exception handling in regular chat
def test_regular_chat_exception():
    with patch('lucidserver.openai_utils.chat_completion', side_effect=Exception("An unexpected exception")):
        message = "Tell me more about lucid dreaming techniques."
        user_email = "user@example.com"
        result = regular_chat(message, user_email)
        assert result == "Error: Unable to generate a response.", f"Expected error message, but got {result}"
        
        
        
        
# Mock search_chat_with_dream function /////////////////////////////////////////////////////////////////////////////////////////////////////////////  
def mock_search_memory(*args, **kwargs):
    return [
        {'id': '1', 'document': 'Dream 1', 'metadata': {'useremail': 'user@example.com', 'date': 'Some Date', 'title': 'Some Title', 'entry': 'Some Entry'}},
        {'id': '2', 'document': 'Dream 2', 'metadata': {'useremail': 'another@example.com', 'date': 'Some Date', 'title': 'Some Title', 'entry': 'Some Entry'}}
    ]

def mock_function_completion(*args, **kwargs):
    return {'arguments': {'Function Response Key': 'Function Response Value'}}

# Mock count_tokens function
def mock_count_tokens(*args, **kwargs):
    return 5

# Test case for search_dreams function
def test_search_dreams():
    with patch('lucidserver.database.search_memory', side_effect=mock_search_memory):
        keyword = "Dream"
        user_email = "user@example.com"
        result = search_dreams(keyword, user_email)
        assert len(result) == 1, f"Expected 1 result, but got {len(result)}"

# Test case for call_function_by_name function
def test_call_function_by_name():
    with patch('lucidserver.openai_utils.function_completion', side_effect=mock_function_completion):
        function_name = "discuss_emotions"
        prompt = "Discuss emotions in dreams"
        messages = []
        result = call_function_by_name(function_name, prompt, messages)
        assert 'arguments' in result, "Expected 'arguments' in result"

# Test case for search_chat_with_dreams function with search results
def test_search_chat_with_dreams_with_results():
    with patch('lucidserver.database.search_dreams', side_effect=mock_search_memory), \
         patch('lucidserver.openai_utils.count_tokens', side_effect=mock_count_tokens), \
         patch('lucidserver.openai_utils.call_function_by_name', side_effect=mock_function_completion):
        function_name = "discuss_emotions"
        prompt = "Discuss emotions in dreams"
        user_email = "user@example.com"
        result = search_chat_with_dreams(function_name, prompt, user_email)
        assert 'arguments' in result, "Expected 'arguments' in result"
        assert 'search_results' in result, "Expected 'search_results' in result"

# Test case for search_chat_with_dreams function without search results
def test_search_chat_with_dreams_without_results():
    with patch('lucidserver.database.search_memory', side_effect=lambda *args, **kwargs: []), \
         patch('lucidserver.openai_utils.count_tokens', side_effect=mock_count_tokens), \
         patch('lucidserver.openai_utils.call_function_by_name', side_effect=mock_function_completion):
        function_name = "discuss_emotions"
        prompt = "Discuss emotions in dreams"
        user_email = "user@example.com"
        result = search_chat_with_dreams(function_name, prompt, user_email)
        assert 'arguments' in result, "Expected 'arguments' in result"
        assert result.get('search_results') == [], "Unexpected non-empty 'search_results' in result"