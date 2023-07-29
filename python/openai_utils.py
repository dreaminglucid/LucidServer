from agentlogger import log, print_header, write_to_file
import requests
import json
import configparser
import random

from easycompletion import (
    compose_function,
    function_completion,
    text_completion,
    chat_completion,
    trim_prompt,
    chunk_prompt,
    count_tokens,
    get_tokens,
)
from agentmemory import search_memory

# Read config.ini file
config = configparser.ConfigParser()
config.read("config.ini")

# Get the API key from the config file
openai_api_key = config.get("openai", "api_key")


#  ANALYSIS AND IMAGE GENERATION FUNCTIONS
def get_image_summary(dream_entry):
    try:
        log(f"Generating summary for dream entry: {dream_entry}", type="info")
        response = text_completion(
            text=f"Awaken to the depths of your subconscious, where dreams transcend reality. Describe the enigmatic tale of your nocturnal journey, where the ethereal dance of {dream_entry} beguiles the senses. Condense this profound experience into a succinct prompt, grounding the essence of your dream in the realms of research, literature, science, mysticism, and ancient wisdom. This prompt will guide the DALLE AI image generation tool by OpenAI, all in under 100 characters.",
            model="gpt-3.5-turbo",
            api_key=openai_api_key,
        )

        log(f"Dream summary response: {response}", type="info")

        if "error" in response and response["error"] is not None:
            log(f"Error from GPT-4: {response['error']}", type="error", color="red")

        if "text" in response:
            return response["text"]
        else:
            log("Error: Unable to generate a summary.", type="error", color="red")
            return "Error: Unable to generate a summary."
    except Exception as e:
        log(f"Error generating Dream summary: {e}", type="error", color="red")
        return "Error: Unable to generate a summary."


def generate_dream_analysis(prompt, system_content):
    try:
        log(f"Generating GPT response for prompt: {prompt}", type="info")
        response = text_completion(
            text=f"""
            A profound dream has been shared, echoing with the resonance of {prompt}. Let's embark on a multi-faceted exploration of its depths, guided by the wisdom of diverse fields of human knowledge. 

            Weave an intricate tapestry of interpretation, touching upon the theories of psychology, the insights of philosophy, the narratives of literature, the revelations of science, the mysteries of mysticism, and the echoes of ancient wisdom. 

            Illuminate the dream's symbolism with scholarly references, thought-provoking quotes, and cross-cultural analogies. Unravel its emotional undertones, its connection to the dreamer's waking life, and its potential implications for personal growth.

            Bring forth an enlightened understanding that is both intellectually rigorous and deeply human. Shape this knowledge into a finely crafted response that serves as a beacon for semantic search, all within the limits of 500 characters.
            """,
            model="gpt-3.5-turbo",
            api_key=openai_api_key,
        )

        log(f"GPT-4 response: {response}", type="info")

        if "error" in response and response["error"] is not None:
            log(f"Error from GPT-4: {response['error']}", type="error", color="red")

        if "text" in response:
            return response["text"]
        else:
            log("Error: Unable to generate a response.", type="error", color="red")
            return "Error: Unable to generate a response."
    except Exception as e:
        log(f"Error generating GPT response: {e}", type="error", color="red")
        return "Error: Unable to generate a response."


def generate_dream_image(dreams, dream_id):
    try:
        log(f"Generating image for dream id: {dream_id}", type="info")
        dream = next((d for d in dreams if d["id"] == dream_id), None)
        if not dream:
            return None

        summary = get_image_summary(dream["metadata"]["entry"])

        data = {
            "prompt": f"A renaissance painting ef {summary}, high quality, lucid dream themed.",
            "n": 1,
            "size": "256x256",
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        }
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            data=json.dumps(data),
            headers=headers,
        )
        response_data = response.json()

        if "data" in response_data and len(response_data["data"]) > 0:
            image_data = response_data["data"][0]
            log(f"Generated image URL: {image_data['url']}", type="info")
            return image_data["url"]
        else:
            log(
                "Error generating dream-inspired image: No data in response",
                type="error",
                color="red",
            )
            return None
    except Exception as e:
        log(f"Error generating dream-inspired image: {e}", type="error", color="red")
        return None


# SEARCH WITH CHAT FUNCTIONS
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


# Define available functions
available_functions = [
    discuss_emotions_function,
    predict_future_function,
]

def regular_chat(message):
    try:
        log(f"Generating GPT response for message: {message}", type="info")
        # Provide a default prompt for lucid dreaming conversation
        if not message:
            message = "Let's talk about the fascinating world of lucid dreaming."
        
        system_message = f"""
            Let's delve deeper into the realm of dreams. Draw upon the vast reservoirs of knowledge about dreams from different perspectives - scientific, psychological, philosophical, and mystical. Interpret the dream imagery, unravel its symbolism, and explore its relevance to the dreamer's waking life and personal growth.

            In the context of lucid dreaming, discuss techniques for inducing lucidity, the benefits and potential challenges of lucid dreaming, and its implications for understanding consciousness and the human mind.

            Weave this understanding into a comprehensive response that provides valuable insights and guidance to the dreamer, all within the constraints of 500 characters.
            """
        
        response = chat_completion(
            messages = [{"role": "user", "content": message}],
            system_message = system_message,
            model='gpt-3.5-turbo',
            api_key=openai_api_key
        )

        log(f"GPT-4 response: {response}", type="info")

        if "error" in response and response["error"] is not None:
            log(f"Error from GPT-4: {response['error']}", type="error", color="red")

        if "text" in response:
            return response["text"]
        else:
            log("Error: Unable to generate a response.", type="error", color="red")
            return "Error: Unable to generate a response."
    except Exception as e:
        log(f"Error generating GPT response: {e}", type="error", color="red")
        return "Error: Unable to generate a response."


def search_dreams(keyword):
    log(f"Searching dreams for keyword: {keyword}.", type="info")
    search_results = search_memory("dreams", keyword, n_results=100)
    dreams = [
        {
            "id": memory["id"],
            "document": memory["document"],
            "metadata": {
                key: memory["metadata"][key]
                for key in ["date", "title", "entry", "analysis"]
                if key in memory["metadata"]
            },
        }
        for memory in search_results
    ]
    return dreams


def call_function_by_name(function_name, prompt):
    # Get the corresponding function from the available_functions dictionary
    function_to_call = next(
        (func for func in available_functions if func["name"] == function_name), None
    )

    # If the function name is not recognized, select a random function
    if function_to_call is None:
        log(
            f"Unknown function name: {function_name}. Selecting a function randomly.",
            type="info",
            color="yellow",
        )
        function_to_call = random.choice(available_functions)

    # Create a conversational context
    context = f"""
    User: {prompt}
    System: I see. You're asking me to {function_to_call['description']}. Let's delve into this, ill provide you a super intuitive and insightful and well structured response in under 300 chaarcters as your AI agent dream journal guide, Emris.
    """

    # Call the selected function
    response = function_completion(
        text=context,  # Use the context as the text for the function call
        functions=[function_to_call],
        function_call=function_to_call["name"],
        api_key=openai_api_key,
    )

    return response


def search_chat_with_dreams(function_name, prompt):
    try:
        # Observe: Log the received prompt
        log(f"Received prompt: {prompt}", type="info")

        # Search the dreams based on the entire prompt
        search_results = search_dreams(prompt)

        # Create the conversational context
        context = ""

        # If we have search results, add them to the context.
        if search_results:
            log("Search results found.", type="info")
            for dream in search_results[:]:  # Limit to the top 3 results
                context += f"""
                System: I found a relevant dream in the database. The dream, titled "{dream['metadata']['title']}", was recorded on {dream['metadata']['date']}. Here's the dream entry: "{dream['metadata']['entry']}". The dream was analyzed as follows: "{dream['metadata'].get('analysis', 'Analysis not available')}".
                """
        else:
            log("No relevant dreams found in the database.", type="info")

        # Append the user's original prompt to the context.
        context += f"User: {prompt}"

        log(f"Final context: {context}", type="info")  # Log the final context

        # Decide: Generate response using EasyCompletion, calling function based on user intent
        # Pass the context, not just the prompt
        response = call_function_by_name(function_name, context)

        log(f"GPT-4 response: {response}", type="info")

        # If there's an error from GPT-4, return an error message.
        if "error" in response and response["error"] is not None:
            log(f"Error from GPT-4: {response['error']}", type="error", color="red")
            return "Error: Unable to generate a response."

        # If there's a response from GPT-4, return the response along with the search results.
        if "arguments" in response:
            response["search_results"] = search_results
            return response
        else:
            log("Error: Unable to generate a response.", type="error", color="red")
            return "Error: Unable to generate a response."
    except Exception as e:
        log(
            f"Error generating GPT response with search: {e}", type="error", color="red"
        )
        return "Error: Unable to generate a response."

