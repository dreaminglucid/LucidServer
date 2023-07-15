import logging
import os
from easycompletion import compose_function, openai_function_call
import requests
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set OpenAI API Key
openai_api_key = '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'

dream_summary_function = compose_function(
    name="get_dream_summary",
    description="Summarize the dream entry",
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
    description="Generate a GPT response based on the prompt and system content.",
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
            text=dream_entry,
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
            text=prompt,
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

        summary = get_dream_summary(dream['entry'])

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