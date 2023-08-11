from agentlogger import log, print_header, write_to_file
import time
from agentmemory import create_memory, get_memories, update_memory, get_memory
from openai_utils import generate_dream_analysis, generate_dream_image, get_image_summary


def create_dream(title, date, entry, userEmail):
    dream = {"title": title, "date": date, "entry": entry, "userEmail": userEmail}
    memory_id = create_memory("dreams", f"{title}\n{entry}", metadata=dream)
    log("Dream created successfully.", type="info")
    dream["id"] = memory_id
    return dream


def get_dream(dream_id):
    log(f"Initiating retrieval of dream with id {dream_id}.", type="info")

    # Fetching the dream
    dream = get_memory("dreams", dream_id)
    if dream is None:
        log(f"Dream with id {dream_id} not found.", type="error", color="red")
        return None

    # Constructing the dream data
    dream_data = {
        "id": dream["id"],
        "title": dream["title"],
        "date": dream["date"],
        "entry": dream["entry"],
        "useremail": dream["useremail"],
        # Include other fields if needed
    }

    # Optionally, extract analysis and image if present
    if "analysis" in dream:
        dream_data["analysis"] = dream["analysis"]
    if "image" in dream:
        dream_data["image"] = dream["image"]

    log(f"Successfully retrieved dream with id {dream_id}: {dream_data}", type="info")
    return dream_data


def get_dreams(userEmail):
    log("Fetching all dreams.", type="info")
    memories = get_memories("dreams", n_results=2222)
    dreams = [
        {
            "id": memory["id"],
            "title": memory["title"],
            "date": memory["date"],
            "entry": memory["entry"],
            "useremail": memory["useremail"],
            # Include other fields if needed
        }
        for memory in memories if memory["useremail"] == userEmail
    ]
    log(f"Debug: Retrieved dreams for userEmail {userEmail}: {dreams}", type="info")
    return dreams


def get_dream_analysis(dream_id, max_retries=5):
    try:
        log(f"Fetching dream analysis for dream id {dream_id}.", type="info")
        dream = get_dream(dream_id)
        for _ in range(max_retries):
            analysis = generate_dream_analysis(
                dream["metadata"]["entry"], "You are dreaming about"
            )
            if analysis:
                return analysis
            time.sleep(5)
        log(
            f"Failed to get dream analysis after {max_retries} attempts.",
            type="error",
            color="red",
        )
        return None
    except Exception as e:
        log(f"Error in get_dream_analysis: {e}", type="error", color="red")
        return None


def get_dream_image(dream_id, style="renaissance", quality="low", max_retries=5):
    try:
        log(f"Fetching dream image for dream id {dream_id}.", type="info")
        dream = get_dream(dream_id)
        log(f"Debug: Retrieved dream object: {dream}", type="info")
        
        # Log the style being used
        log(f"Using image style: {style}", type="info")

        userEmail = dream["metadata"]["userEmail"]  # get userEmail from dream metadata
        dreams = get_dreams(userEmail)  # pass userEmail to get_dreams()
        summary = get_image_summary(dream["metadata"]["entry"])
        for _ in range(max_retries):
            image = generate_dream_image(dreams, dream_id, style, quality)
            if image:
                return image
            time.sleep(5)
        log(
            f"Failed to get dream image after {max_retries} attempts.",
            type="error",
            color="red",
        )
        return None
    except Exception as e:
        log(f"Error in get_dream_image: {e}", type="error", color="red")
        return None


def update_dream_analysis_and_image(dream_id, analysis=None, image=None):
    log(f"Initiating update for dream analysis and image for dream id {dream_id}.", type="info")

    # Fetching the dream
    dream = get_dream(dream_id)
    if dream is None:
        log(f"Dream with id {dream_id} not found.", type="error", color="red")
        return None

    # Validating metadata
    metadata = dream.get("metadata")
    if metadata is None:
        log(f"Metadata for dream with id {dream_id} not found.", type="error", color="red")
        return None

    # Ensuring analysis and image are valid
    if analysis:
        if isinstance(analysis, str): # Validate the type or content of analysis as needed
            metadata["analysis"] = analysis
        else:
            log(f"Invalid analysis data for dream id {dream_id}.", type="error", color="red")
            return None

    if image:
        if isinstance(image, str): # Validate the type or content of image as needed
            metadata["image"] = image
        else:
            log(f"Invalid image data for dream id {dream_id}.", type="error", color="red")
            return None

    # Logging the state before the update
    log(f"Updating dream id {dream_id} with metadata: {metadata}", type="info")

    # Updating the memory
    try:
        update_memory("dreams", dream_id, metadata=metadata)
        log("Dream analysis and image updated successfully.", type="info")
        return dream
    except Exception as e:
        log(f"Failed to update dream id {dream_id}. Error: {str(e)}", type="error", color="red")
        return None
