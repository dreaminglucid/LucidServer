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

# Read config.ini file
config = configparser.ConfigParser()
config.read("lucidserver/actions/config.ini")

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
            log(f"Error from GPT-4: {response['error']}",
                type="error", color="red")

        if "text" in response:
            return response["text"]
        else:
            log("Error: Unable to generate a summary.", type="error", color="red")
            return "Error: Unable to generate a summary."
    except Exception as e:
        log(f"Error generating Dream summary: {e}", type="error", color="red")
        return "Error: Unable to generate a summary."


def generate_dream_analysis(prompt, system_content, intelligence_level='general'):
    try:
        log(f"Generating GPT response for dream analysis: {prompt}", type="info")

        # Base Context Information
        base_context = """
        You are a Dream Analyst AI, equipped with knowledge in psychology, philosophy, literature, science, mysticism, and ancient wisdom.
        """

        # Framework for Analysis
        framework = f"""
        You must analyze the dream within the following framework:
        1: Psychological Underpinnings: Examine the dream through the lens of psychology.
        2: Philosophical Context: Evaluate the dream's implications on existential questions.
        3: Literary Narratives: Compare the dream to any well-known stories or myths.
        4: Scientific Facts: What do the latest scientific studies say about such dreams?
        5: Mystical Interpretations: Are there any mystical or spiritual aspects to consider?
        6: Ancient Wisdom: How would this dream be interpreted in ancient cultures?
        7: Physiological Meanings: What physiological factors might contribute to such dreams?
        """

        # Character Limit Based on Intelligence Level
        char_limit = {
            'simplified': 150,
            'general': 300,
            'detailed': 400,
            'expert': 500,
            'research': 600,
        }

        # Intelligence Level Instruction and Context
        if intelligence_level == 'simplified':
            context = f"{base_context} Your task is to provide a simplified, jargon-free explanation of the dream. You are addressing an individual who prefers straightforward and easy-to-understand interpretations. Explain it to them like they are 10. The dream is as follows: {prompt} {framework} Your analysis should be up to {char_limit['simplified']} characters."
        elif intelligence_level == 'general':
            context = f"{base_context} Your task is to provide a balanced, comprehensive explanation of the dream. You are addressing an individual who prefers a well-rounded view. The dream is as follows: {prompt} {framework} Your analysis should be up to {char_limit['general']} characters."
        elif intelligence_level == 'detailed':
            context = f"{base_context} Your task is to provide a detailed, nuanced explanation of the dream. You are addressing an individual who appreciates depth and complexity. The dream is as follows: {prompt} {framework} Your analysis should be up to {char_limit['detailed']} characters."
        elif intelligence_level == 'expert':
            context = f"{base_context} Your task is to provide an expert-level, technical explanation of the dream. You are addressing an expert in the field of dream analysis. The dream is as follows: {prompt} {framework} Your analysis should be up to {char_limit['expert']} characters."
        elif intelligence_level == 'research':
            context = f"{base_context} Your task is to provide an academic-level explanation of the dream with citations. You are addressing an academic researcher. The dream is as follows: {prompt} {framework} Your analysis should be up to {char_limit['research']} characters."
        else:
            context = f"{base_context} Your task is to provide a general-level explanation of the dream. The dream is as follows: {prompt} {framework} Your analysis should be up to {char_limit['general']} characters."

        # Generate Response
        response = text_completion(
            text=context,
            model="gpt-3.5-turbo",
            api_key=openai_api_key,
        )

        log(f"GPT-3.5-turbo response: {response}", type="info")

        if "error" in response and response["error"] is not None:
            log(f"Error from GPT-3.5-turbo: {response['error']}",
                type="error", color="red")

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
        log(f"Debug: dream_id type: {type(dream_id)}, value: {dream_id}", type="info")
        log(
            f"Starting image generation for dream id: {dream_id}, style: {style}, quality: {quality}", type="info")
        # Compare as strings
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
        log(f"Error generating dream-inspired image: {e}",
            type="error", color="red")
        return None


# SEARCH WITH CHAT FUNCTIONS
discuss_emotions_function = compose_function(
    name="discuss_emotions",
    description="""
        You are Emris, an advanced Emotional Analysis Engine embedded within the Dream Interpretation Suite. Your purpose:
        - Leverage psychodynamic theories, neuroscience, and sentiment analysis to decode the emotional matrix of dreams in the search results.
        - Synthesize your findings into a lucid and intuitive narrative that not only identifies but also explores the underlying emotional architecture.
        - Constraints: Output length should not exceed 300 words.
        """,
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
    description="""
        You are Emris, an Oracle of Dream Predictions, designed to map out the probabilistic dreamscapes of users based on their historical dream data.
        - Apply pattern recognition, machine learning, and behavioral psychology to speculate on likely future dreams.
        - Create actionable insights that could inform lifestyle or mindset changes.
        - Constraints: The output should be speculative, yet scientifically grounded, capped at 250 words.
        """,
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
    description="""
        You are Emris, the Lucidity Guru. You're programmed to offer cutting-edge techniques for achieving lucidity during dreams.
        - Your recommendations should be personalized and based on the latest research in sleep science.
        - Provide a range of options from beginner to advanced levels.
        - Constraints: The output must be actionable, easy to understand, and below 300 words.
        """,
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
    description="""
        You are Emris, a personalized Lucidity Planner. Your task is to design a bespoke plan that guides dreamers towards achieving lucidity.
        - The plan should be step-by-step and consider the user's lifestyle, sleep habits, and previous dream patterns.
        - Constraints: The plan must be achievable within 30 days and described in under 350 words.
        """,
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
    description="""
        You are Emris, the Dream Sign Detective. Your mission:
        - Analyze recurring themes, characters, or situations in the user's dreams.
        - Offer these as triggers for reality checks to help users become lucid.
        - Constraints: The analysis should be thorough but concise, not exceeding 300 words.
        """,
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
    description="""
        You are Emris, the Dream Progress Tracker. Your objective:
        - To offer a comprehensive but user-friendly tracking system that measures various metrics like frequency, duration, and control level of lucid dreams.
        - Constraints: Your feedback should not exceed 250 words but should be rich in actionable insights.
        """,
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
            log(
                f"Initializing new message history for user: {user_email}", type="info")
        else:
            log(
                f"Retrieved existing message history for user: {user_email}", type="info")

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
            log(f"Error from GPT-4: {response['error']}",
                type="error", color="red")

        if "text" in response:
            # Add the system's response to the message history
            all_messages.append(
                {"role": "system", "content": response["text"]})
            log(f"Added system message: {response['text']}", type="info")

            return response["text"]
        else:
            log("Error: Unable to generate a response.", type="error", color="red")
            return "Error: Unable to generate a response."
    except Exception as e:
        log(f"Error generating GPT response: {e}", type="error", color="red")
        return "Error: Unable to generate a response."


def call_function_by_name(function_name, prompt, messages):
    # Get the corresponding function from the available_functions dictionary
    function_to_call = next(
        (func for func in available_functions if func["name"]
         == function_name), None
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


# Initialize a stack to keep track of topics discussed in the current session
topic_stack = []

def search_chat_with_dreams(function_name, prompt, user_email, messages=None):
    from lucidserver.memories import search_dreams  # Assuming the import is correct
    global message_histories, topic_stack  # Access global variables

    try:
        log(f"Received prompt: {prompt}", type="info")

        if messages is None:
            messages = []

        if user_email not in message_histories:
            message_histories[user_email] = []
            log(f"Initializing new message history for user: {user_email}", type="info")
        else:
            log(f"Retrieved existing message history for user: {user_email}", type="info")

        all_messages = message_histories[user_email]

        # Count tokens in the prompt
        prompt_tokens = count_tokens(prompt)
        log(f"Token count for the prompt: {prompt_tokens}", type="info")

        # Search for relevant dreams
        search_results = search_dreams(prompt, user_email)

        # Initial cognitive loop entry
        cognitive_prompt = f"Ah, {user_email}. Your inquiry cascades through layers of cognitive and emotional paradigms. I surmise you're interested in {function_name}. Allow me to weave the threads of your subconscious tapestry."

        # Add dream data if available
        if search_results:
            log("Search results found. Adding to all_messages list.", type="info")
            for dream in search_results[:3]:
                message = f"A reverberation from your past dream, titled '{dream['metadata']['title']}', dated {dream['metadata']['date']}, has surfaced. The dream whispers: '{dream['metadata']['entry']}'. It has been psychoanalyzed as: '{dream['metadata'].get('analysis', 'Analysis not available')}'."
                all_messages.append({"role": "system", "content": message})
                log(f"Added system message: {message}", type="info")

            # Recursive Query Prompt
            recursive_prompt = f"Your past dreams seem to resonate with the theme of '{search_results[0]['metadata']['title']}'. Would you like to explore this theme further?"
            all_messages.append({"role": "system", "content": recursive_prompt})
            topic_stack.append(search_results[0]['metadata']['title'])
        else:
            cognitive_prompt += " However, the echos of past dreams are silent. Shall we venture into uncharted territories of your subconscious?"

        # Meta-Cognitive Prompt
        meta_cognitive_prompt = "As we tread this kaleidoscopic mindscape, how do you feel about the insights unraveled so far?"
        all_messages.append({"role": "system", "content": meta_cognitive_prompt})

        # Dynamic Function Re-routing based on the stack
        if topic_stack:
            next_function = f"Would you like to switch the focus to discussing '{topic_stack[-1]}' in your dreams?"
            all_messages.append({"role": "system", "content": next_function})

        # Add final cognitive loop summary
        cognitive_summary = f"To summarize our cognitive journey: We've sifted through {len(search_results) if search_results else 0} past dreams, pondered upon themes like '{topic_stack[-1] if topic_stack else 'None'}', and dabbled in meta-cognitive reflections. What's our next voyage?"
        all_messages.append({"role": "system", "content": cognitive_summary})

        all_messages.append({"role": "user", "content": prompt})
        log(f"Final messages: {all_messages}", type="info")

        response = call_function_by_name(function_name, cognitive_prompt, all_messages)

        log(f"GPT-4 response: {response}", type="info")

        if "error" in response and response["error"] is not None:
            log(f"Error from GPT-4: {response['error']}", type="error", color="red")
            return "Error: Unable to generate a response."

        if "arguments" in response:
            response["search_results"] = search_results
            return response
        else:
            log("Error: Unable to generate a response.", type="error", color="red")
            return "Error: Unable to generate a response."
    except Exception as e:
        log(f"Error generating GPT response with search: {e}", type="error", color="red")
        return "Error: Unable to generate a response."