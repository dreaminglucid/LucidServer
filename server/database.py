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
    log(f"Fetching dream with id {dream_id}.", type="info")
    dream = get_memory("dreams", dream_id)
    if dream is not None:
        dream_data = {
            "id": dream["id"],
            "document": dream["document"],
            "metadata": dream["metadata"],
        }
        if "analysis" in dream["metadata"]:
            dream_data["analysis"] = dream["metadata"]["analysis"]
        if "image" in dream["metadata"]:
            dream_data["image"] = dream["metadata"]["image"]
        return dream_data
    else:
        log(f"Dream with id {dream_id} not found.", type="error", color="red")
        return None


def get_dreams(userEmail):
    log("Fetching all dreams.", type="info")
    memories = get_memories("dreams", n_results=2222)
    dreams = [
        {
            "id": memory["id"],
            "document": memory["document"],
            "metadata": memory["metadata"],
        }
        for memory in memories if "userEmail" in memory["metadata"] and memory["metadata"]["userEmail"] == userEmail
    ]
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


def get_dream_image(dream_id, style="renaissance", max_retries=5):
    try:
        log(f"Fetching dream image for dream id {dream_id}.", type="info")
        
        # Log the style being used
        log(f"Using image style: {style}", type="info")

        dream = get_dream(dream_id)
        userEmail = dream["metadata"]["userEmail"]  # get userEmail from dream metadata
        dreams = get_dreams(userEmail)  # pass userEmail to get_dreams()
        summary = get_image_summary(dream["metadata"]["entry"])
        for _ in range(max_retries):
            image = generate_dream_image(dreams, dream_id, style)
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
    log(f"Updating dream analysis and image for dream id {dream_id}.", type="info")
    dream = get_dream(dream_id)
    if dream is None:
        log(f"Dream with id {dream_id} not found.", type="error", color="red")
        return None
    if analysis:
        dream["metadata"]["analysis"] = analysis
    if image:
        dream["metadata"]["image"] = image
    update_memory("dreams", dream_id, metadata=dream["metadata"])
    log("Dream analysis and image updated successfully.", type="info")
    return dream