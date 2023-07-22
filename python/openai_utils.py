import logging
import requests
import json
import configparser

from easycompletion import compose_function, openai_function_call
from agentmemory import search_memory

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Get the API key from the config file
openai_api_key = config.get('openai', 'api_key')


dream_summary_function = compose_function(
    name="get_dream_summary",
    description="This function is used to condense the dream entry into a short summary. The goal of this function is to capture the main events, characters, and emotions from the dream in a clear and concise manner. This allows the user to quickly review their dream without having to read through the full entry.",
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
    description="This function is used to generate an analysis of the dream based on the prompt and system content. The analysis should provide insights into potential meanings or interpretations of the dream. It should consider the symbolism of the dream's elements, the emotions experienced by the dreamer, and any recurring patterns or themes.",
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


def get_dream_summary(dream_entry):
    try:
        logger.info(f"Generating summary for dream entry: {dream_entry}")
        response = openai_function_call(
            text=f"You've just woken up from a dream about {dream_entry}. In a few sentences, summarize the main events and themes of this dream.",
            functions=dream_summary_function,
            function_call="get_dream_summary",
            api_key=openai_api_key
        )

        logger.info(f"Dream summary response: {response}")

        if 'error' in response and response['error'] is not None:
            logger.error(f"Error from GPT-4: {response['error']}")

        if 'arguments' in response and 'dream_entry' in response['arguments']:
            return response['arguments']['dream_entry']
        else:
            logger.error("Error: Unable to generate a summary.")
            return 'Error: Unable to generate a summary.'
    except Exception as e:
        logger.error(f"Error generating Dream summary: {e}", exc_info=True)
        return 'Error: Unable to generate a summary.'


def get_gpt_response(prompt, system_content):
    try:
        logger.info(f"Generating GPT response for prompt: {prompt}")
        response = openai_function_call(
            text=f"You've just shared a dream about {prompt}. Let's delve deeper into this dream and explore its potential meanings. Consider the symbolism of the elements in the dream, the emotions you felt, and any recurring themes or patterns. What might this dream be trying to tell you?",
            functions=gpt_response_function,
            function_call="get_gpt_response",
            api_key=openai_api_key
        )

        logger.info(f"GPT-4 response: {response}")

        if 'error' in response and response['error'] is not None:
            logger.error(f"Error from GPT-4: {response['error']}")

        if 'arguments' in response and 'prompt' in response['arguments']:
            return response['arguments']['prompt']
        else:
            logger.error("Error: Unable to generate a response.")
            return 'Error: Unable to generate a response.'
    except Exception as e:
        logger.error(f"Error generating GPT response: {e}", exc_info=True)
        return 'Error: Unable to generate a response.'


def generate_dream_image(dreams, dream_id):
    try:
        logger.info(f"Generating image for dream id: {dream_id}")
        dream = next((d for d in dreams if d['id'] == dream_id), None)
        if not dream:
            return None

        summary = get_dream_summary(dream['metadata']['entry'])

        data = {
            'prompt': f"{summary}, high quality, digital art, photorealistic style, very detailed, lucid dream themed",
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
            logger.info(f"Generated image URL: {image_data['url']}")
            return image_data['url']
        else:
            logger.error(
                "Error generating dream-inspired image: No data in response")
            return None
    except Exception as e:
        logger.error(
            f"Error generating dream-inspired image: {e}", exc_info=True)
        return None


def search_dreams(keyword):
    logger.info(f'Searching dreams for keyword: {keyword}.')
    search_results = search_memory("dreams", keyword, n_results=3)  # returns top 20 results
    dreams = [{"id": memory["id"], "document": memory["document"], "metadata": memory["metadata"]}
              for memory in search_results]
    return dreams


def search_chat_with_dreams(prompt):
    try:
        logger.info(f"Received prompt: {prompt}")  # Log the received prompt

        # Now we search the dreams based on the entire prompt
        search_results = search_dreams(prompt)

        # If we have search results, format them into a string that can be used in the GPT-4 prompt.
        if search_results:
            search_results_str = "Here are some similar dreams from the database: \n" + '\n'.join(
                [f"- Title: {dream['metadata']['title']}, Date: {dream['metadata']['date']}, Analysis: {dream['metadata'].get('analysis', 'Analysis not available')}\nDream Entry: {dream['metadata']['entry']}" for dream in search_results])

            prompt = f"{prompt}\n\n{search_results_str}"

        else:
            logger.info("No similar dreams found in the database.")
            prompt = f"{prompt}\n\nNo similar dreams were found in the database. Let's explore possible meanings of your dream."

        logger.info(f"Final prompt: {prompt}")  # Log the final prompt

        # Define the function to discuss the search results or the original dream if no similar dreams were found
        discuss_results_function = compose_function(
            name="discuss_search_results",
            description="Discuss the search results and point out common themes or patterns",
            properties={
                "discussion": {
                    "type": "string",
                    "description": "The discussion text generated from the search results",
                }
            },
            required_properties=["discussion"],
        )

        # Generate response using EasyCompletion
        response = openai_function_call(
            text=prompt,
            functions=[discuss_results_function],
            function_call="discuss_search_results",
            api_key=openai_api_key
        )
        logger.info(f"GPT-4 response: {response}")

        # If there's an error from GPT-4, return an error message.
        if 'error' in response and response['error'] is not None:
            logger.error(f"Error from GPT-4: {response['error']}")
            return 'Error: Unable to generate a response.'

        # If there's a response from GPT-4, return the response along with the search results.
        if 'arguments' in response and 'discussion' in response['arguments']:
            response['search_results'] = search_results
            return response
        else:
            logger.error("Error: Unable to generate a response.")
            return 'Error: Unable to generate a response.'
    except Exception as e:
        logger.error(
            f"Error generating GPT response with search: {e}", exc_info=True)
        return 'Error: Unable to generate a response.'
