import logging
import time
from agentmemory import (
    create_memory,
    get_memories,
    update_memory,
    get_memory,
    save_memory,
    search_memory
)
from openai_utils import get_gpt_response, generate_dream_image, get_dream_summary

# Create a custom logger
logger = logging.getLogger(__name__)


def create_dream(title, date, entry):
    dream = {'title': title, 'date': date, 'entry': entry}
    memory_id = create_memory("dreams", f"{title}\n{entry}", metadata=dream)
    save_memory()
    logger.info('Dream created successfully.')
    dream['id'] = memory_id
    return dream


def get_dream(dream_id):
    logger.info(f'Fetching dream with id {dream_id}.')
    dream = get_memory("dreams", dream_id)
    if dream is not None:
        dream_data = {
            "id": dream["id"],
            "document": dream["document"],
            "metadata": dream["metadata"]
        }
        if 'analysis' in dream['metadata']:
            dream_data['analysis'] = dream['metadata']['analysis']
        if 'image' in dream['metadata']:
            dream_data['image'] = dream['metadata']['image']
        return dream_data
    else:
        logger.error(f"Dream with id {dream_id} not found.")
        return None


def get_dreams():
    logger.info('Fetching all dreams.')
    memories = get_memories("dreams")
    dreams = [{"id": memory["id"], "document": memory["document"], "metadata": memory["metadata"]}
              for memory in memories]
    return dreams


def get_dream_analysis(dream_id, max_retries=5):
    try:
        logger.info(f'Fetching dream analysis for dream id {dream_id}.')
        dream = get_dream(dream_id)
        for _ in range(max_retries):
            analysis = get_gpt_response(dream['metadata']['entry'], "You are dreaming about")
            if analysis:
                return analysis
            time.sleep(5)
        logger.error(f"Failed to get dream analysis after {max_retries} attempts.")
        return None
    except Exception as e:
        logger.error(f"Error in get_dream_analysis: {e}")
        return None
    

def get_dream_image(dream_id, max_retries=5):
    try:
        logger.info(f'Fetching dream image for dream id {dream_id}.')
        dream = get_dream(dream_id)
        dreams = get_dreams()
        summary = get_dream_summary(dream['metadata']['entry'])
        for _ in range(max_retries):
            image = generate_dream_image(dreams, dream_id)
            if image:
                return image
            time.sleep(5)
        logger.error(f"Failed to get dream image after {max_retries} attempts.")
        return None
    except Exception as e:
        logger.error(f"Error in get_dream_image: {e}")
        return None


def update_dream_analysis_and_image(dream_id, analysis=None, image=None):
    logger.info(f'Updating dream analysis and image for dream id {dream_id}.')
    dream = get_dream(dream_id)
    if dream is None:
        logger.error(f"Dream with id {dream_id} not found.")
        return None
    if analysis:
        dream['metadata']['analysis'] = analysis  # Update 'analysis' inside 'metadata'
    if image:
        dream['metadata']['image'] = image  # Update 'image' inside 'metadata'
    update_memory("dreams", dream_id, metadata=dream['metadata'])  # Update only 'metadata'
    save_memory()
    logger.info('Dream analysis and image updated successfully.')
    return dream