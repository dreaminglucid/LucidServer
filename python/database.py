import logging
from agentmemory import (
    create_memory,
    get_memories,
    update_memory,
    get_memory
)
from openai_utils import get_gpt_response, generate_dream_image, get_dream_summary

# Create a custom logger
logger = logging.getLogger(__name__)

def create_dream(title, date, entry):
    dream_data = {"title": title, "date": date, "entry": entry}
    dream_id = create_memory("dreams", f"{title}\n{entry}", metadata=dream_data)
    dream_data["id"] = dream_id
    logger.info('Dream created successfully.')
    return dream_data

def get_dreams():
    logger.info('Fetching all dreams.')
    memories = get_memories("dreams")
    dreams = [{"id": memory["id"], **memory['metadata']} for memory in memories]
    return dreams

def get_dream(dream_id):
    logger.info(f'Fetching dream with id {dream_id}.')
    dream = get_memory("dreams", dream_id)
    if dream is not None:
        dream_data = {"id": dream["id"], **dream["metadata"]}
        return dream_data
    else:
        logger.error(f"Dream with id {dream_id} not found.")
        return None

def get_dream_analysis(dream_id):
    try:
        logger.info(f'Fetching dream analysis for dream id {dream_id}.')
        dream = get_dream(dream_id)
        if 'analysis' in dream:
            return dream['analysis']
        else:
            analysis = get_gpt_response(dream['entry'], "You are dreaming about")
            update_memory("dreams", dream_id, metadata={'analysis': analysis})
            return analysis
    except Exception as e:
        logger.error(f"Error in get_dream_analysis: {e}")
        return None

def get_dream_image(dream_id):
    try:
        logger.info(f'Fetching dream image for dream id {dream_id}.')
        dream = get_dream(dream_id)
        if 'image' in dream:
            return dream['image']
        else:
            dreams = get_dreams()
            summary = get_dream_summary(dream['entry'])
            image = generate_dream_image(dreams, dream_id)
            update_memory("dreams", dream_id, metadata={'image': image})
            return image
    except Exception as e:
        logger.error(f"Error in get_dream_image: {e}")
        return None

def update_dream_analysis_and_image(dream_id, analysis=None, image=None):
    logger.info(f'Updating dream analysis and image for dream id {dream_id}.')
    dream = get_dream(dream_id)
    if dream:
        if analysis:
            dream['analysis'] = analysis
        if image:
            dream['image'] = image
        update_memory(dream_id, metadata=dream)  
        logger.info('Dream analysis and image updated successfully.')
        return dream
    return None