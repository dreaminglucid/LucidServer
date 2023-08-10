from agentlogger import log
import requests
import json
import configparser
import random

from easycompletion import (
    compose_function,
    function_completion,
    text_completion,
    chat_completion,
    count_tokens,
)
from agentmemory import search_memory

# Read config.ini file
config = configparser.ConfigParser()
config.read("config.ini")

# Get the API key from the config file
openai_api_key = config.get("openai", "api_key")

# This dictionary will store the message history for each user
message_histories = {}


# ANALYSIS AND IMAGE GENERATION FUNCTIONS
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


def generate_dream_image(dreams, dream_id, style="renaissance", quality="low"):
    try:
        log(f"Starting image generation for dream id: {dream_id}, style: {style}, quality: {quality}", type="info")
        dream = next((d for d in dreams if d["id"] == dream_id), None)
        
        if not dream:
            log(f"Dream with id {dream_id} not found in the provided dreams list.", type="warning")
            return None
        
        log(f"Found dream with id: {dream_id}. Proceeding with image generation.", type="info")
        summary = get_image_summary(dream["metadata"]["entry"])
        log(f"Image summary obtained: {summary}", type="info")

        # Adjust prompt based on style
        if style == "renaissance":
            style_description = "A renaissance painting of"
        elif style == "abstract":
            style_description = "An abstract representation of"
        elif style == "modern":
            style_description = "A modern artwork of"
        else:
            style_description = "A renaissance painting of"  # default
        
        log(f"Selected style description: {style_description}", type="info")
            
        quality_resolution_map = {
            "low": "256x256",
            "medium": "512x512",
            "high": "1024x1024"
        }
        resolution = quality_resolution_map.get(quality, "256x256")
        
        # Log the image quality and resolution
        log(f"Using image quality: {quality} with resolution: {resolution}", type="info")

        prompt = f"{style_description} {summary}, high quality, lucid dream themed."
        log(f"Generated prompt: {prompt}", type="info")

        data = {
            "prompt": prompt,
            "n": 1,
            "size": resolution,
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        }

        log(f"Sending request to OpenAI API with data: {data}", type="info")
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            data=json.dumps(data),
            headers=headers,
        )

        response_data = response.json()
        log(f"Received response from OpenAI API: {response_data}", type="info")

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

discuss_lucidity_techniques_function = compose_function(
    name="discuss_lucidity_techniques",
    description="Discuss various techniques that can help the dreamer achieve lucidity in their dreams. This can include methods like reality checks, mnemonic induction of lucid dreams (MILD), wake back to bed (WBTB), etc. The suggestions can be customized based on the dream patterns of the dreamer.",
    properties={
        "lucidity_techniques": {
            "type": "string",
            "description": "Discussion on various techniques for achieving lucidity",
        }
    },
    required_properties=["lucidity_techniques"],
)

create_lucidity_plan_function = compose_function(
    name="create_lucidity_plan",
    description="Create a personalized lucidity plan for the dreamer, taking into account their dream patterns, sleep habits, and lifestyle. This could involve a step-by-step routine to follow before bedtime, specific reality checks to perform, or techniques to use when they recognize they are dreaming.",
    properties={
        "lucidity_plan": {
            "type": "string",
            "description": "A personalized plan designed to help the dreamer achieve lucidity",
        }
    },
    required_properties=["lucidity_plan"],
)

analyze_dream_signs_function = compose_function(
    name="analyze_dream_signs",
    description="Analyze the dreamer's dreams for recurring themes, characters, or situations that could serve as dream signs. Dream signs can be used by the dreamer as triggers for reality checks and help them become lucid in future dreams.",
    properties={
        "dream_signs": {
            "type": "string",
            "description": "Analysis of potential dream signs within the dreamer's dreams",
        }
    },
    required_properties=["dream_signs"],
)

track_lucidity_progress_function = compose_function(
    name="track_lucidity_progress",
    description="Track the dreamer's progress towards achieving lucidity over time. This could involve comparing the frequency of lucid dreams, the duration of lucidity, or the dreamer's control within the dream. This feedback can be useful for adjusting techniques or plans.",
    properties={
        "lucidity_progress": {
            "type": "string",
            "description": "Progress tracking of the dreamer's journey towards achieving lucidity",
        }
    },
    required_properties=["lucidity_progress"],
)

# Define available functions
available_functions = [
    discuss_emotions_function,
    predict_future_function,
    discuss_lucidity_techniques_function,
    create_lucidity_plan_function,
    analyze_dream_signs_function,
    track_lucidity_progress_function,
]

def regular_chat(message, user_email):
    global message_histories  # Access the global dictionary

    try:
        log(f"Generating GPT response for message: {message}", type="info")

        # Retrieve the user's history, or initialize a new one if it does not exist yet
        if user_email not in message_histories:
            message_histories[user_email] = []
            log(f"Initializing new message history for user: {user_email}", type="info")
        else:
            log(f"Retrieved existing message history for user: {user_email}", type="info")

        all_messages = message_histories[user_email]

        # Provide a default prompt for lucid dreaming conversation
        if not message:
            message = "Let's talk about the fascinating world of lucid dreaming."
        
        initial_message = """
            Let's delve deeper into the realm of dreams. Draw upon the vast reservoirs of knowledge about dreams from different perspectives - scientific, psychological, philosophical, and mystical. Interpret the dream imagery, unravel its symbolism, and explore its relevance to the dreamer's waking life and personal growth.

            In the context of lucid dreaming, discuss techniques for inducing lucidity, the benefits and potential challenges of lucid dreaming, and its implications for understanding consciousness and the human mind.

            Weave this understanding into a comprehensive response that provides valuable insights and guidance to the dreamer, all within the constraints of 500 characters.
            """
        
        # Combine system_message and user message
        all_messages += [
            {"role": "system", "content": initial_message},
            {"role": "user", "content": message}
        ]
        
        response = chat_completion(
            messages=all_messages,
            model='gpt-3.5-turbo-16k',
            api_key=openai_api_key
        )

        log(f"GPT-4 response: {response}", type="info")

        if "error" in response and response["error"] is not None:
            log(f"Error from GPT-4: {response['error']}", type="error", color="red")

        if "text" in response:
            # Add the system's response to the message history
            all_messages.append({"role": "system", "content": response["text"]})
            log(f"Added system message: {response['text']}", type="info")

            return response["text"]
        else:
            log("Error: Unable to generate a response.", type="error", color="red")
            return "Error: Unable to generate a response."
    except Exception as e:
        log(f"Error generating GPT response: {e}", type="error", color="red")
        return "Error: Unable to generate a response."


def search_dreams(keyword, user_email):
    log(f"Searching dreams for keyword: {keyword} and user email: {user_email}.", type="info")
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
        if memory['metadata']['userEmail'] == user_email  # filter results by user email
    ]
    return dreams


def call_function_by_name(function_name, prompt, messages):
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

    all_messages = []

    if messages is not None:
        all_messages += messages

    # Call the selected function
    response = function_completion(
        text=prompt,  # Use the last user message as the text for the function call
        messages=all_messages,  # Include the message history
        functions=[function_to_call],
        function_call=function_to_call["name"],
        api_key=openai_api_key,
        model='gpt-3.5-turbo-16k'  # Set the model to 'gpt-3.5-turbo-16k'
    )

    return response

def search_chat_with_dreams(function_name, prompt, user_email, messages=None):
    global message_histories  # Access the global dictionary

    try:
        log(f"Received prompt: {prompt}", type="info")

        if messages is None:
            messages = []

        # Retrieve the user's history, or initialize a new one if it does not exist yet
        if user_email not in message_histories:
            message_histories[user_email] = []
            log(f"Initializing new message history for user: {user_email}", type="info")
        else:
            log(f"Retrieved existing message history for user: {user_email}", type="info")

        all_messages = message_histories[user_email]

        # Count the tokens in the prompt
        prompt_tokens = count_tokens(prompt)
        log(f"Counted {prompt_tokens} tokens in the prompt.", type="info")

        # Search the dreams based on the entire prompt
        search_results = search_dreams(prompt, user_email)

        # If we have search results, add them to the messages.
        if search_results:
            log("Search results found. Adding to all_messages list.", type="info")
            for dream in search_results[:]:  # Limit to the top 3 results
                message = f"I found a relevant dream in the database. The dream, titled '{dream['metadata']['title']}', was recorded on {dream['metadata']['date']}. Here's the dream entry: '{dream['metadata']['entry']}'. The dream was analyzed as follows: '{dream['metadata'].get('analysis', 'Analysis not available')}'."
                all_messages.append({"role": "system", "content": message})
                log(f"Added system message: {message}", type="info")
        else:
            log("No relevant dreams found in the database.", type="info")

        # Append the user's original prompt to the messages.
        all_messages.append({"role": "user", "content": prompt})
        log(f"Added user message: {prompt}", type="info")

        # Log the final messages
        log(f"Final messages: {all_messages}", type="info")

        # Generate response using EasyCompletion, calling function based on user intent
        # Pass the all_messages, not just the prompt
        log("Calling function by name with all_messages list.", type="info")
        response = call_function_by_name(function_name, prompt, all_messages)

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
