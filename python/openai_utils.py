from agentlogger import log, print_header, write_to_file
import requests
import json
import configparser
import random

from easycompletion import compose_function, openai_function_call, openai_text_call
from agentmemory import search_memory

# Read config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Get the API key from the config file
openai_api_key = config.get('openai', 'api_key')

dream_summary_function = compose_function(
    name="get_dream_summary",
    description="This function is used to condense the dream entry into a short summary. The goal of this function is to capture the main events, characters, and emotions from the dream in a clear and concise manner. This will be used to generate the perfect dream image using DALLE AI generation from OpenAI.",
    properties={
        "dream_entry": {
            "type": "string",
            "description": "The dream entry to be summarized.",
        }
    },
    required_properties=["dream_entry"],
)

gpt_response_function = compose_function(
    name="get_gpt_response",
    description="This function is used to generate an analysis of the dream based on the prompt and system content. The analysis should provide insights into potential meanings or interpretations of the dream. It should consider the symbolism of the dream's elements, the emotions experienced by the dreamer, and any recurring patterns or themes. Format the response in a way that will later be useful for semantic search.",
    properties={
        "prompt": {
            "type": "string",
            "description": "The prompt for GPT.",
        },
        "system_content": {
            "type": "string",
            "description": "The system message for GPT.",
        },
    },
    required_properties=["prompt", "system_content"],
)

discuss_results_function = compose_function(
    name="discuss_search_results",
    description="I would like you to analyze and discuss the commonalities among the dream search results, pointing out recurring themes, symbols, or patterns. Consider the possible meanings and interpretations of these elements in the context of dream analysis theories.",
    properties={
        "discussion": {
            "type": "string",
            "description": "The discussion text generated from the search results",
        }
    },
    required_properties=["discussion"],
)

discuss_themes_function = compose_function(
    name="discuss_themes",
    description="Please provide a deep analysis of the main themes appearing in the dream search results. Explore the potential symbolic meanings of these themes and how they might relate to the dreamer's personal experiences or subconscious thoughts.",
    properties={
        "themes": {
            "type": "string",
            "description": "The discussion text generated from the themes in the search results",
        }
    },
    required_properties=["themes"],
)

discuss_emotions_function = compose_function(
    name="discuss_emotions",
    description="Analyze the emotional content of the dreams in the search results. Discuss what these emotions might suggest about the dreamer's subconscious feelings or concerns. Also, consider how these emotions interact with the other elements of the dreams.",
    properties={
        "emotions": {
            "type": "string",
            "description": "The discussion text generated from the emotions in the search results",
        }
    },
    required_properties=["emotions"],
)

discuss_characters_function = compose_function(
    name="discuss_characters",
    description="Examine the characters that appear in the dream search results. Discuss their possible symbolic meanings and roles within the dream narratives. Consider how these characters might reflect aspects of the dreamer's own personality or relationships.",
    properties={
        "characters": {
            "type": "string",
            "description": "The discussion text generated from the characters in the search results",
        }
    },
    required_properties=["characters"],
)

interpret_symbols_function = compose_function(
    name="interpret_dream_symbols",
    description="Interpret the key symbols or themes found in the dream. Discuss their potential meanings based on various dream interpretation theories. Consider both universal interpretations and meanings that might be specific to the dreamer's personal experiences or cultural background.",
    properties={
        "symbols": {
            "type": "string",
            "description": "The symbols or themes to be interpreted",
        }
    },
    required_properties=["symbols"],
)

personal_associations_function = compose_function(
    name="explore_personal_associations",
    description="Explore the dreamer's personal associations or experiences that might be relevant to the dream. Discuss how these personal factors could influence the interpretation of the dream's symbols and themes. Consider both the dreamer's recent experiences and long-term memories or relationships.",
    properties={
        "personal_associations": {
            "type": "string",
            "description": "The personal associations or experiences to be explored",
        }
    },
    required_properties=["personal_associations"],
)

recall_similar_function = compose_function(
    name="recall_similar_dreams",
    description="Retrieve similar dreams from the dream database. Discuss the similarities and differences between these dreams and the original dream, considering elements such as themes, symbols, emotions, and characters. Also, explore what these similarities might suggest about recurring patterns in the dreamer's dreams.",
    properties={
        "similar_dreams": {
            "type": "string",
            "description": "The similar dreams to be recalled",
        }
    },
    required_properties=["similar_dreams"],
)

predict_future_function = compose_function(
    name="predict_future_dreams",
    description="Speculate about possible future dreams the dreamer might have, based on the patterns observed in their current dreams. Discuss what changes in their life or subconscious thoughts could lead to different types of dreams. Keep in mind that this is purely speculative and not a definite prediction.",
    properties={
        "future_dreams": {
            "type": "string",
            "description": "The possible future dreams to be predicted",
        }
    },
    required_properties=["future_dreams"],
)

discuss_general_function = compose_function(
    name="discuss_general_dream_concept",
    description="Discuss the general concept of dreams and dream analysis. Provide an overview of common theories or perspectives on why we dream, what dreams might mean, and how dreams can be interpreted. Also, consider the limitations and challenges of dream analysis.",
    properties={
        "general_concept": {
            "type": "string",
            "description": "The general concept to be discussed",
        }
    },
    required_properties=["general_concept"],
)


def get_dream_summary(dream_entry):
    try:
        log(f"Generating summary for dream entry: {dream_entry}", type='info')
        response = openai_function_call(
            text=f"You've just woken up from a dream about {dream_entry}. In a short sentence, summarize the main events and themes of this dream into the perfect prompt to be used with the DALLE AI image generation tool by OpenAI.",
            functions=dream_summary_function,
            function_call="get_dream_summary",
            api_key=openai_api_key
        )

        log(f"Dream summary response: {response}", type='info')

        if 'error' in response and response['error'] is not None:
            log(f"Error from GPT-4: {response['error']}",
                type='error', color='red')

        if 'arguments' in response and 'dream_entry' in response['arguments']:
            return response['arguments']['dream_entry']
        else:
            log("Error: Unable to generate a summary.", type='error', color='red')
            return 'Error: Unable to generate a summary.'
    except Exception as e:
        log(f"Error generating Dream summary: {e}", type='error', color='red')
        return 'Error: Unable to generate a summary.'


def get_gpt_response(prompt, system_content):
    try:
        log(f"Generating GPT response for prompt: {prompt}", type='info')
        response = openai_function_call(
            text=f"You've just shared a dream about {prompt}. Let's delve deeper into this dream and explore its potential meanings. Consider the symbolism of the elements in the dream, the emotions you felt, and any recurring themes or patterns. Format the response in a way that will later be useful for semantic search.",
            functions=gpt_response_function,
            function_call="get_gpt_response",
            api_key=openai_api_key
        )

        log(f"GPT-4 response: {response}", type='info')

        if 'error' in response and response['error'] is not None:
            log(f"Error from GPT-4: {response['error']}",
                type='error', color='red')

        if 'arguments' in response and 'prompt' in response['arguments']:
            return response['arguments']['prompt']
        else:
            log("Error: Unable to generate a response.", type='error', color='red')
            return 'Error: Unable to generate a response.'
    except Exception as e:
        log(f"Error generating GPT response: {e}", type='error', color='red')
        return 'Error: Unable to generate a response.'


def generate_dream_image(dreams, dream_id):
    try:
        log(f"Generating image for dream id: {dream_id}", type='info')
        dream = next((d for d in dreams if d['id'] == dream_id), None)
        if not dream:
            return None

        summary = get_dream_summary(dream['metadata']['entry'])

        data = {
            'prompt': f"{summary}, high quality, digital art, lucid dream themed",
            'n': 1,
            'size': '512x512',
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {openai_api_key}"
        }
        response = requests.post(
            'https://api.openai.com/v1/images/generations', data=json.dumps(data), headers=headers)
        response_data = response.json()

        if 'data' in response_data and len(response_data['data']) > 0:
            image_data = response_data['data'][0]
            log(f"Generated image URL: {image_data['url']}", type='info')
            return image_data['url']
        else:
            log("Error generating dream-inspired image: No data in response",
                type='error', color='red')
            return None
    except Exception as e:
        log(f"Error generating dream-inspired image: {e}",
            type='error', color='red')
        return None


def search_dreams(keyword):
    log(f'Searching dreams for keyword: {keyword}.', type='info')
    search_results = search_memory("dreams", keyword, n_results=100)
    dreams = [{"id": memory["id"], "document": memory["document"], "metadata": memory["metadata"]}
              for memory in search_results]
    return dreams


# Define available functions
available_functions = [
    discuss_results_function, 
    discuss_themes_function, 
    discuss_emotions_function, 
    discuss_characters_function,
    interpret_symbols_function, 
    personal_associations_function, 
    recall_similar_function,
    predict_future_function, 
    discuss_general_function
]


def call_function_by_name(function_name, prompt):
    # Get the corresponding function from the available_functions dictionary
    function_to_call = next(
        (func for func in available_functions if func['name'] == function_name), None)

    # If the function name is not recognized, select a random function
    if function_to_call is None:
        log(f"Unknown function name: {function_name}. Selecting a function randomly.", type='info', color='yellow')
        function_to_call = random.choice(available_functions)

    # Create a conversational context
    context = f"""
    User: {prompt}
    System: I see. You're asking me to {function_to_call['description']}. Let's delve into this.
    """

    # Call the selected function
    response = openai_function_call(
        text=context,  # Use the context as the text for the function call
        functions=[function_to_call],
        function_call=function_to_call['name'],
        api_key=openai_api_key,
    )

    return response


def search_chat_with_dreams(function_name, prompt):
    try:
        # Observe: Log the received prompt
        log(f"Received prompt: {prompt}", type='info')

        # Search the dreams based on the entire prompt
        search_results = search_dreams(prompt)

        # Create the conversational context
        context = ""

        # If we have search results, add them to the context.
        if search_results:
            for dream in search_results:
                context += f"""
                System: I found a similar dream in the database. The dream, titled "{dream['metadata']['title']}", was recorded on {dream['metadata']['date']}. Here's the dream entry: "{dream['metadata']['entry']}". The dream was analyzed as follows: "{dream['metadata'].get('analysis', 'Analysis not available')}".
                """
        else:
            log("No similar dreams found in the database.", type='info')
            context = "System: I'm sorry, but I couldn't find any similar dreams in the database. Let's explore possible meanings of your dream."

        # Append the user's original prompt to the context.
        context += f"User: {prompt}"

        log(f"Final context: {context}", type='info')  # Log the final context

        # Decide: Generate response using EasyCompletion, calling function based on user intent
        response = call_function_by_name(function_name, context)  # Pass the context, not just the prompt

        log(f"GPT-4 response: {response}", type='info')

        # If there's an error from GPT-4, return an error message.
        if 'error' in response and response['error'] is not None:
            log(f"Error from GPT-4: {response['error']}",
                type='error', color='red')
            return 'Error: Unable to generate a response.'

        # If there's a response from GPT-4, return the response along with the search results.
        if 'arguments' in response:
            response['search_results'] = search_results
            return response
        else:
            log("Error: Unable to generate a response.", type='error', color='red')
            return 'Error: Unable to generate a response.'
    except Exception as e:
        log(f"Error generating GPT response with search: {e}",
            type='error', color='red')
        return 'Error: Unable to generate a response.'
