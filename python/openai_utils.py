import logging
import os
from easycompletion import compose_function, openai_function_call
import requests
import json
import configparser

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