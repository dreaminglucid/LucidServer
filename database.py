from agentlogger import log, print_header, write_to_file
import time
from agentmemory import create_memory, get_memories, update_memory, get_memory
from openai_utils import generate_dream_analysis, generate_dream_image, get_image_summary


def create_dream(title, date, entry, userEmail):
    metadata = {
        "title": title,
        "date": date,
        "entry": entry,
        "useremail": userEmail, # Note the lowercase 'e'
    }
    document = f"{title}\n{entry}"
    memory_id = create_memory("dreams", document, metadata=metadata)
    dream = get_memory("dreams", memory_id)
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
        "document": dream["document"],
        "metadata": {
            "title": dream["metadata"]["title"],
            "date": dream["metadata"]["date"],
            "entry": dream["metadata"]["entry"],
            "useremail": dream["metadata"]["useremail"],
        }
    }

    # Optionally, extract analysis and image from metadata if present
    if "analysis" in dream["metadata"]:
        dream_data["analysis"] = dream["metadata"]["analysis"]
    if "image" in dream["metadata"]:
        dream_data["image"] = dream["metadata"]["image"]

    log(f"Successfully retrieved dream with id {dream_id}: {dream_data}", type="info")
    return dream_data


def get_dreams(userEmail):
    log("Fetching all dreams.", type="info")
    memories = get_memories("dreams", n_results=2222)
    dreams = []
    for memory in memories:
        if "useremail" in memory["metadata"] and memory["metadata"]["useremail"] == userEmail:
            dream_data = {
                "id": memory["id"],
                "document": memory["document"],
                "metadata": {
                    "title": memory["metadata"]["title"],
                    "date": memory["metadata"]["date"],
                    "entry": memory["metadata"]["entry"],
                    "useremail": memory["metadata"]["useremail"],
                }
            }
            # Optionally, extract analysis and image from metadata if present
            if "analysis" in memory["metadata"]:
                dream_data["analysis"] = memory["metadata"]["analysis"]
            if "image" in memory["metadata"]:
                dream_data["image"] = memory["metadata"]["image"]

            dreams.append(dream_data)

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

        userEmail = dream["metadata"]["useremail"]  # get useremail from dream metadata, updated line
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
