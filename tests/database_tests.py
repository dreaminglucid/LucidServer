import sys
sys.path.append('.')

import pytest
from database import create_dream, get_dream, get_dreams, get_dream_analysis, get_dream_image, update_dream_analysis_and_image

# Mocking the create_memory function
def mock_create_memory(category, document, metadata=None):
    return "memory_id_12345"

# Mocking the get_memory function
def mock_get_memory(category, memory_id):
    return {
        "id": "memory_id_12345",
        "document": "Dream Title\nDream Entry",
        "metadata": {
            "title": "Dream Title",
            "date": "2022-08-07",
            "entry": "Dream Entry",
            "useremail": "user@example.com",
            "created_at": 1691807205.048965,
            "updated_at": 1691807205.048965
        }
    }

# Testing the create_dream function
def test_create_dream(monkeypatch):
    # Patching the create_memory and get_memory functions with mock functions
    monkeypatch.setattr('agentmemory.create_memory', mock_create_memory)
    monkeypatch.setattr('database.get_memory', mock_get_memory)

    # Test inputs
    title = "Dream Title"
    date = "2022-08-07"
    entry = "Dream Entry"
    user_email = "user@example.com"

    # Calling the create_dream function
    result = create_dream(title, date, entry, user_email)

    # Asserting the properties of the result
    assert isinstance(result['id'], str) and result['id'] != "", "ID should be a non-empty string."
    assert result['document'] == "Dream Title\nDream Entry"
    assert result['metadata']['title'] == title
    assert result['metadata']['date'] == date
    assert result['metadata']['entry'] == entry
    assert result['metadata']['useremail'] == user_email
    assert 'created_at' in result['metadata']
    assert 'updated_at' in result['metadata']
    
# Testing the get_dream function when the dream exists
def test_get_dream_existing(monkeypatch):
    # Patching the get_memory function with mock function
    monkeypatch.setattr('database.get_memory', mock_get_memory)

    # Test input
    dream_id = "memory_id_12345"

    # Calling the get_dream function
    result = get_dream(dream_id)

    # Asserting the properties of the result
    assert result is not None, "Result should not be None."
    assert isinstance(result['id'], str) and result['id'] != "", "ID should be a non-empty string."
    assert result['document'] == "Dream Title\nDream Entry"
    assert result['metadata']['title'] == "Dream Title"
    assert result['metadata']['date'] == "2022-08-07"
    assert result['metadata']['entry'] == "Dream Entry"
    assert result['metadata']['useremail'] == "user@example.com"

# Testing the get_dream function when the dream does not exist
def test_get_dream_non_existing(monkeypatch):
    # Mocking the get_memory function to return None
    def mock_get_memory_non_existing(category, memory_id):
        return None

    # Patching the get_memory function with mock function
    monkeypatch.setattr('database.get_memory', mock_get_memory_non_existing)

    # Test input
    dream_id = "non_existing_id"

    # Calling the get_dream function
    result = get_dream(dream_id)

    # Asserting that the result is None
    assert result is None, "Expected None, but got a result."

# Modifying the mock_get_memory function to include optional fields
def mock_get_memory_with_optional_fields(category, memory_id):
    dream = mock_get_memory(category, memory_id)
    dream['metadata']['analysis'] = "Some analysis"
    dream['metadata']['image'] = "image.png"
    return dream

# Testing the get_dream function with optional fields
def test_get_dream_with_optional_fields(monkeypatch):
    # Patching the get_memory function with modified mock function
    monkeypatch.setattr('database.get_memory', mock_get_memory_with_optional_fields)

    # Test input
    dream_id = "memory_id_12345"

    # Calling the get_dream function
    result = get_dream(dream_id)

    # Asserting that the optional fields are present
    assert result['analysis'] == "Some analysis", f"Expected analysis field, but got {result}"
    assert result['image'] == "image.png", f"Expected image field, but got {result}"

# Mocking the get_memories function
def mock_get_memories(category, n_results=None):
    return [
        {
            "id": "memory_id_12345",
            "document": "Dream Title\nDream Entry",
            "metadata": {
                "title": "Dream Title",
                "date": "2022-08-07",
                "entry": "Dream Entry",
                "useremail": "user@example.com",
                "analysis": "Some analysis",
                "image": "image.png",
            }
        },
        {
            "id": "memory_id_67890",
            "document": "Another Dream Title\nAnother Dream Entry",
            "metadata": {
                "title": "Another Dream Title",
                "date": "2022-08-08",
                "entry": "Another Dream Entry",
                "useremail": "another@example.com",
            }
        },
    ]

# Testing the get_dreams function when dreams exist for the user
def test_get_dreams_existing(monkeypatch):
    # Patching the get_memories function with mock function
    monkeypatch.setattr('database.get_memories', mock_get_memories)

    # Test input
    user_email = "user@example.com"

    # Calling the get_dreams function
    result = get_dreams(user_email)

    # Asserting the properties of the result
    assert len(result) == 1, "Expected one dream for the given email."
    assert result[0]['id'] == "memory_id_12345"
    assert result[0]['document'] == "Dream Title\nDream Entry"
    assert result[0]['metadata']['title'] == "Dream Title"
    assert result[0]['metadata']['date'] == "2022-08-07"
    assert result[0]['metadata']['entry'] == "Dream Entry"
    assert result[0]['metadata']['useremail'] == "user@example.com"
    assert result[0]['analysis'] == "Some analysis"
    assert result[0]['image'] == "image.png"

# Testing the get_dreams function when no dreams exist for the user
def test_get_dreams_non_existing(monkeypatch):
    # Patching the get_memories function with mock function
    monkeypatch.setattr('database.get_memories', mock_get_memories)

    # Test input
    user_email = "non_existing@example.com"

    # Calling the get_dreams function
    result = get_dreams(user_email)

    # Asserting that the result is empty
    assert result == [], "Expected an empty list, but got a result."

def mock_get_dream(dream_id):
    return {
        "id": "memory_id_12345",
        "document": "Dream Title\nDream Entry",
        "metadata": {
            "title": "Dream Title",
            "date": "2022-08-07",
            "entry": "Dream Entry",
            "useremail": "user@example.com",
            "analysis": "Some analysis",  # Optional field
            "image": "image.png",        # Optional field
        }
    }

# Mocking the generate_dream_analysis function
def mock_generate_dream_analysis(entry, prefix):
    return f"Analysis of: {entry}"

# Testing the get_dream_analysis function when the dream exists
def test_get_dream_analysis_existing(monkeypatch):
    # Patching the get_dream and generate_dream_analysis functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream)  # Using the new mock function
    monkeypatch.setattr('database.generate_dream_analysis', mock_generate_dream_analysis)

    # Test input
    dream_id = "memory_id_12345"

    # Calling the get_dream_analysis function
    result = get_dream_analysis(dream_id, max_retries=1)  # Ensuring only one attempt

    # Asserting that the analysis is correct
    assert result == "Analysis of: Dream Entry", f"Expected analysis, but got {result}"

# Testing the get_dream_analysis function when the dream does not exist
def test_get_dream_analysis_non_existing(monkeypatch):
    # Patching the get_dream function with mock function to return None
    monkeypatch.setattr('database.get_dream', lambda dream_id: None)

    # Test input
    dream_id = "non_existing_id"

    # Calling the get_dream_analysis function
    result = get_dream_analysis(dream_id)

    # Asserting that the result is None
    assert result is None, "Expected None, but got a result."

# Mocking the get_dreams function
def mock_get_dreams(userEmail):
    return [mock_get_dream("memory_id_12345")]

# Mocking the get_image_summary function
def mock_get_image_summary(entry):
    return "Image Summary"

# Mocking the generate_dream_image function
def mock_generate_dream_image(dreams, dream_id, style, quality):
    return "Generated Image"

def test_get_dream_image_existing(monkeypatch):
    # Patching the dependent functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream) # Assuming existing mock function
    monkeypatch.setattr('database.get_dreams', mock_get_dreams) # Assuming existing mock function
    monkeypatch.setattr('database.get_image_summary', mock_get_image_summary)
    monkeypatch.setattr('database.generate_dream_image', mock_generate_dream_image)

    # Test input
    dream_id = "memory_id_12345"

    # Calling the get_dream_image function
    result = get_dream_image(dream_id, max_retries=1) # Ensuring only one attempt

    # Asserting that the image is correct
    assert result == "Generated Image", f"Expected image, but got {result}"

# Mocking the generate_dream_image function to simulate failure
def mock_generate_dream_image_failure(dreams, dream_id, style, quality):
    return None

def test_get_dream_image_failure(monkeypatch):
    # Patching the dependent functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream) # Assuming existing mock function
    monkeypatch.setattr('database.get_dreams', mock_get_dreams) # Assuming existing mock function
    monkeypatch.setattr('database.get_image_summary', mock_get_image_summary)
    monkeypatch.setattr('database.generate_dream_image', mock_generate_dream_image_failure)

    # Test input
    dream_id = "memory_id_12345"

    # Calling the get_dream_image function
    result = get_dream_image(dream_id, max_retries=1) # Ensuring only one attempt

    # Asserting that the result is None (failure case)
    assert result is None, "Expected None, but got a result."

# Mocking the update_memory function
def mock_update_memory(category, memory_id, metadata=None):
    pass

# Testing the successful update of dream analysis and image
def test_update_dream_analysis_and_image_success(monkeypatch):
    # Patching the dependent functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream) # Assuming existing mock function
    monkeypatch.setattr('database.update_memory', mock_update_memory)

    # Test input
    dream_id = "memory_id_12345"
    analysis = "New Analysis"
    image = "new_image.png"

    # Calling the update_dream_analysis_and_image function
    result = update_dream_analysis_and_image(dream_id, analysis=analysis, image=image)

    # Asserting that the update is successful and the new values are present
    assert result['metadata']['analysis'] == analysis, f"Expected analysis, but got {result}"
    assert result['metadata']['image'] == image, f"Expected image, but got {result}"

# Testing the update with invalid analysis type
def test_update_dream_analysis_and_image_invalid_analysis(monkeypatch):
    # Patching the dependent functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream) # Assuming existing mock function

    # Test input
    dream_id = "memory_id_12345"
    analysis = 123 # Invalid analysis type

    # Calling the update_dream_analysis_and_image function
    result = update_dream_analysis_and_image(dream_id, analysis=analysis)

    # Asserting that the result is None (failure case)
    assert result is None, "Expected None, but got a result."

# Testing the update with invalid image type
def test_update_dream_analysis_and_image_invalid_image(monkeypatch):
    # Patching the dependent functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream) # Assuming existing mock function

    # Test input
    dream_id = "memory_id_12345"
    image = 123 # Invalid image type

    # Calling the update_dream_analysis_and_image function
    result = update_dream_analysis_and_image(dream_id, image=image)

    # Asserting that the result is None (failure case)
    assert result is None, "Expected None, but got a result."

# Mocking the update_memory function to simulate an exception
def mock_update_memory_exception(category, memory_id, metadata=None):
    raise Exception("Update failed")

# Testing the update with an exception during the update process
def test_update_dream_analysis_and_image_exception(monkeypatch):
    # Patching the dependent functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream) # Assuming existing mock function
    monkeypatch.setattr('database.update_memory', mock_update_memory_exception)

    # Test input
    dream_id = "memory_id_12345"
    analysis = "New Analysis"
    image = "new_image.png"

    # Calling the update_dream_analysis_and_image function
    result = update_dream_analysis_and_image(dream_id, analysis=analysis, image=image)

    # Asserting that the result is None (failure case)
    assert result is None, "Expected None, but got a result."
import sys
sys.path.append('.')

import pytest
from database import create_dream, get_dream, get_dreams, get_dream_analysis, get_dream_image, update_dream_analysis_and_image
from openai_utils import search_dreams


# Mocking the create_memory function //////////////////////////////////////////////////////////////////////////////////////////////////////
def mock_create_memory(category, document, metadata=None):
    return "memory_id_12345"

# Mocking the get_memory function
def mock_get_memory(category, memory_id):
    return {
        "id": "memory_id_12345",
        "document": "Dream Title\nDream Entry",
        "metadata": {
            "title": "Dream Title",
            "date": "2022-08-07",
            "entry": "Dream Entry",
            "useremail": "user@example.com",
            "created_at": 1691807205.048965,
            "updated_at": 1691807205.048965
        }
    }

# Testing the create_dream function
def test_create_dream(monkeypatch):
    # Patching the create_memory and get_memory functions with mock functions
    monkeypatch.setattr('agentmemory.create_memory', mock_create_memory)
    monkeypatch.setattr('database.get_memory', mock_get_memory)

    # Test inputs
    title = "Dream Title"
    date = "2022-08-07"
    entry = "Dream Entry"
    user_email = "user@example.com"

    # Calling the create_dream function
    result = create_dream(title, date, entry, user_email)

    # Asserting the properties of the result
    assert isinstance(result['id'], str) and result['id'] != "", "ID should be a non-empty string."
    assert result['document'] == "Dream Title\nDream Entry"
    assert result['metadata']['title'] == title
    assert result['metadata']['date'] == date
    assert result['metadata']['entry'] == entry
    assert result['metadata']['useremail'] == user_email
    assert 'created_at' in result['metadata']
    assert 'updated_at' in result['metadata']
   
    
# Testing the get_dream function when the dream exists ////////////////////////////////////////////////////////////////////////////////////////////
def test_get_dream_existing(monkeypatch):
    # Patching the get_memory function with mock function
    monkeypatch.setattr('database.get_memory', mock_get_memory)

    # Test input
    dream_id = "memory_id_12345"

    # Calling the get_dream function
    result = get_dream(dream_id)

    # Asserting the properties of the result
    assert result is not None, "Result should not be None."
    assert isinstance(result['id'], str) and result['id'] != "", "ID should be a non-empty string."
    assert result['document'] == "Dream Title\nDream Entry"
    assert result['metadata']['title'] == "Dream Title"
    assert result['metadata']['date'] == "2022-08-07"
    assert result['metadata']['entry'] == "Dream Entry"
    assert result['metadata']['useremail'] == "user@example.com"

# Testing the get_dream function when the dream does not exist
def test_get_dream_non_existing(monkeypatch):
    # Mocking the get_memory function to return None
    def mock_get_memory_non_existing(category, memory_id):
        return None

    # Patching the get_memory function with mock function
    monkeypatch.setattr('database.get_memory', mock_get_memory_non_existing)

    # Test input
    dream_id = "non_existing_id"

    # Calling the get_dream function
    result = get_dream(dream_id)

    # Asserting that the result is None
    assert result is None, "Expected None, but got a result."

# Modifying the mock_get_memory function to include optional fields
def mock_get_memory_with_optional_fields(category, memory_id):
    dream = mock_get_memory(category, memory_id)
    dream['metadata']['analysis'] = "Some analysis"
    dream['metadata']['image'] = "image.png"
    return dream

# Testing the get_dream function with optional fields
def test_get_dream_with_optional_fields(monkeypatch):
    # Patching the get_memory function with modified mock function
    monkeypatch.setattr('database.get_memory', mock_get_memory_with_optional_fields)

    # Test input
    dream_id = "memory_id_12345"

    # Calling the get_dream function
    result = get_dream(dream_id)

    # Asserting that the optional fields are present
    assert result['analysis'] == "Some analysis", f"Expected analysis field, but got {result}"
    assert result['image'] == "image.png", f"Expected image field, but got {result}"


# Mocking the get_memories function ///////////////////////////////////////////////////////////////////////////////////////////////////////////
def mock_get_memories(category, n_results=None):
    return [
        {
            "id": "memory_id_12345",
            "document": "Dream Title\nDream Entry",
            "metadata": {
                "title": "Dream Title",
                "date": "2022-08-07",
                "entry": "Dream Entry",
                "useremail": "user@example.com",
                "analysis": "Some analysis",
                "image": "image.png",
            }
        },
        {
            "id": "memory_id_67890",
            "document": "Another Dream Title\nAnother Dream Entry",
            "metadata": {
                "title": "Another Dream Title",
                "date": "2022-08-08",
                "entry": "Another Dream Entry",
                "useremail": "another@example.com",
            }
        },
    ]

# Testing the get_dreams function when dreams exist for the user
def test_get_dreams_existing(monkeypatch):
    # Patching the get_memories function with mock function
    monkeypatch.setattr('database.get_memories', mock_get_memories)

    # Test input
    user_email = "user@example.com"

    # Calling the get_dreams function
    result = get_dreams(user_email)

    # Asserting the properties of the result
    assert len(result) == 1, "Expected one dream for the given email."
    assert result[0]['id'] == "memory_id_12345"
    assert result[0]['document'] == "Dream Title\nDream Entry"
    assert result[0]['metadata']['title'] == "Dream Title"
    assert result[0]['metadata']['date'] == "2022-08-07"
    assert result[0]['metadata']['entry'] == "Dream Entry"
    assert result[0]['metadata']['useremail'] == "user@example.com"
    assert result[0]['analysis'] == "Some analysis"
    assert result[0]['image'] == "image.png"

# Testing the get_dreams function when no dreams exist for the user
def test_get_dreams_non_existing(monkeypatch):
    # Patching the get_memories function with mock function
    monkeypatch.setattr('database.get_memories', mock_get_memories)

    # Test input
    user_email = "non_existing@example.com"

    # Calling the get_dreams function
    result = get_dreams(user_email)

    # Asserting that the result is empty
    assert result == [], "Expected an empty list, but got a result."

def mock_get_dream(dream_id):
    return {
        "id": "memory_id_12345",
        "document": "Dream Title\nDream Entry",
        "metadata": {
            "title": "Dream Title",
            "date": "2022-08-07",
            "entry": "Dream Entry",
            "useremail": "user@example.com",
            "analysis": "Some analysis",  # Optional field
            "image": "image.png",        # Optional field
        }
    }


# Mocking the generate_dream_analysis function ///////////////////////////////////////////////////////////////////////////////////////////////////
def mock_generate_dream_analysis(entry, prefix):
    return f"Analysis of: {entry}"

# Testing the get_dream_analysis function when the dream exists
def test_get_dream_analysis_existing(monkeypatch):
    # Patching the get_dream and generate_dream_analysis functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream)  # Using the new mock function
    monkeypatch.setattr('database.generate_dream_analysis', mock_generate_dream_analysis)

    # Test input
    dream_id = "memory_id_12345"

    # Calling the get_dream_analysis function
    result = get_dream_analysis(dream_id, max_retries=1)  # Ensuring only one attempt

    # Asserting that the analysis is correct
    assert result == "Analysis of: Dream Entry", f"Expected analysis, but got {result}"

# Testing the get_dream_analysis function when the dream does not exist
def test_get_dream_analysis_non_existing(monkeypatch):
    # Patching the get_dream function with mock function to return None
    monkeypatch.setattr('database.get_dream', lambda dream_id: None)

    # Test input
    dream_id = "non_existing_id"

    # Calling the get_dream_analysis function
    result = get_dream_analysis(dream_id)

    # Asserting that the result is None
    assert result is None, "Expected None, but got a result."


# Mocking the get_dreams function /////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def mock_get_dreams(userEmail):
    return [mock_get_dream("memory_id_12345")]

# Mocking the get_image_summary function
def mock_get_image_summary(entry):
    return "Image Summary"

# Mocking the generate_dream_image function
def mock_generate_dream_image(dreams, dream_id, style, quality):
    return "Generated Image"

def test_get_dream_image_existing(monkeypatch):
    # Patching the dependent functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream) # Assuming existing mock function
    monkeypatch.setattr('database.get_dreams', mock_get_dreams) # Assuming existing mock function
    monkeypatch.setattr('database.get_image_summary', mock_get_image_summary)
    monkeypatch.setattr('database.generate_dream_image', mock_generate_dream_image)

    # Test input
    dream_id = "memory_id_12345"

    # Calling the get_dream_image function
    result = get_dream_image(dream_id, max_retries=1) # Ensuring only one attempt

    # Asserting that the image is correct
    assert result == "Generated Image", f"Expected image, but got {result}"

# Mocking the generate_dream_image function to simulate failure
def mock_generate_dream_image_failure(dreams, dream_id, style, quality):
    return None

def test_get_dream_image_failure(monkeypatch):
    # Patching the dependent functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream) # Assuming existing mock function
    monkeypatch.setattr('database.get_dreams', mock_get_dreams) # Assuming existing mock function
    monkeypatch.setattr('database.get_image_summary', mock_get_image_summary)
    monkeypatch.setattr('database.generate_dream_image', mock_generate_dream_image_failure)

    # Test input
    dream_id = "memory_id_12345"

    # Calling the get_dream_image function
    result = get_dream_image(dream_id, max_retries=1) # Ensuring only one attempt

    # Asserting that the result is None (failure case)
    assert result is None, "Expected None, but got a result."


# Mocking the update_memory function ///////////////////////////////////////////////////////////////////////////////////////////////////////
def mock_update_memory(category, memory_id, metadata=None):
    pass

# Testing the successful update of dream analysis and image
def test_update_dream_analysis_and_image_success(monkeypatch):
    # Patching the dependent functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream) # Assuming existing mock function
    monkeypatch.setattr('database.update_memory', mock_update_memory)

    # Test input
    dream_id = "memory_id_12345"
    analysis = "New Analysis"
    image = "new_image.png"

    # Calling the update_dream_analysis_and_image function
    result = update_dream_analysis_and_image(dream_id, analysis=analysis, image=image)

    # Asserting that the update is successful and the new values are present
    assert result['metadata']['analysis'] == analysis, f"Expected analysis, but got {result}"
    assert result['metadata']['image'] == image, f"Expected image, but got {result}"

# Testing the update with invalid analysis type
def test_update_dream_analysis_and_image_invalid_analysis(monkeypatch):
    # Patching the dependent functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream) # Assuming existing mock function

    # Test input
    dream_id = "memory_id_12345"
    analysis = 123 # Invalid analysis type

    # Calling the update_dream_analysis_and_image function
    result = update_dream_analysis_and_image(dream_id, analysis=analysis)

    # Asserting that the result is None (failure case)
    assert result is None, "Expected None, but got a result."

# Testing the update with invalid image type
def test_update_dream_analysis_and_image_invalid_image(monkeypatch):
    # Patching the dependent functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream) # Assuming existing mock function

    # Test input
    dream_id = "memory_id_12345"
    image = 123 # Invalid image type

    # Calling the update_dream_analysis_and_image function
    result = update_dream_analysis_and_image(dream_id, image=image)

    # Asserting that the result is None (failure case)
    assert result is None, "Expected None, but got a result."

# Mocking the update_memory function to simulate an exception
def mock_update_memory_exception(category, memory_id, metadata=None):
    raise Exception("Update failed")

# Testing the update with an exception during the update process
def test_update_dream_analysis_and_image_exception(monkeypatch):
    # Patching the dependent functions with mock functions
    monkeypatch.setattr('database.get_dream', mock_get_dream) # Assuming existing mock function
    monkeypatch.setattr('database.update_memory', mock_update_memory_exception)

    # Test input
    dream_id = "memory_id_12345"
    analysis = "New Analysis"
    image = "new_image.png"

    # Calling the update_dream_analysis_and_image function
    result = update_dream_analysis_and_image(dream_id, analysis=analysis, image=image)

    # Asserting that the result is None (failure case)
    assert result is None, "Expected None, but got a result."


# Mocking the search_dreams function /////////////////////////////////////////////////////////////////////////////////////////////////////////
def mock_search_memory(category, keyword, n_results=100):
    if keyword == "NonExisting":
        return []
    return [
        {
            "id": "memory_id_12345",
            "document": "Dream Title\nDream Entry",
            "metadata": {
                "title": "Dream Title",
                "date": "2022-08-07",
                "entry": "Dream Entry",
                "useremail": "user@example.com",
                "analysis": "Some analysis",
            }
        },
        {
            "id": "memory_id_67890",
            "document": "Another Dream Title\nAnother Dream Entry",
            "metadata": {
                "title": "Another Dream Title",
                "date": "2022-08-08",
                "entry": "Another Dream Entry",
                "useremail": "another@example.com",
            }
        },
    ]

# Testing the search_dreams function when there are matching dreams for the given user
def test_search_dreams_existing(monkeypatch):
    # Patching the search_memory function with mock function
    monkeypatch.setattr('openai_utils.search_memory', mock_search_memory)

    # Test inputs
    keyword = "Dream"
    user_email = "user@example.com"

    # Calling the search_dreams function
    result = search_dreams(keyword, user_email)

    # Asserting the properties of the result
    assert len(result) == 1, "Expected one matching dream for the given email."
    assert result[0]['id'] == "memory_id_12345"
    assert result[0]['document'] == "Dream Title\nDream Entry"
    assert result[0]['metadata']['title'] == "Dream Title"
    assert result[0]['metadata']['date'] == "2022-08-07"
    assert result[0]['metadata']['entry'] == "Dream Entry"
    assert result[0]['metadata']['analysis'] == "Some analysis"

# Testing the search_dreams function when no matching dreams exist for the given user
def test_search_dreams_non_existing(monkeypatch):
    # Patching the search_memory function with mock function
    monkeypatch.setattr('openai_utils.search_memory', mock_search_memory)

    # Test inputs
    keyword = "NonExisting"
    user_email = "user@example.com"

    # Calling the search_dreams function
    result = search_dreams(keyword, user_email)

    # Asserting that the result is empty
    assert result == [], "Expected an empty list, but got a result."

# Testing the search_dreams function with multiple dreams but filtering by user email
def test_search_dreams_filter_by_email(monkeypatch):
    # Patching the search_memory function with mock function
    monkeypatch.setattr('openai_utils.search_memory', mock_search_memory)

    # Test inputs
    keyword = "Dream"
    user_email = "another@example.com"

    # Calling the search_dreams function
    result = search_dreams(keyword, user_email)

    # Asserting that the result includes the dream for the given email
    assert len(result) == 1, "Expected one matching dream for the given email."
    assert result[0]['id'] == "memory_id_67890"
    assert result[0]['document'] == "Another Dream Title\nAnother Dream Entry"
    assert result[0]['metadata']['title'] == "Another Dream Title"
    assert result[0]['metadata']['date'] == "2022-08-08"
    assert result[0]['metadata']['entry'] == "Another Dream Entry"
    assert 'analysis' not in result[0]['metadata'], "Did not expect analysis field, but got one."