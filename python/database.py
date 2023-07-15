import logging
from agentmemory import (
    create_memory,
    get_memories,
    update_memory,
    get_memory
)
import json
from openai_utils import get_gpt_response, generate_dream_image, get_dream_summary

# Create a custom logger
logger = logging.getLogger(__name__)

def create_dream(title, date, entry):
    logger.info('Starting to create a dream.')
    memories = get_memories("dreams")
    dream_id = str(len(memories) + 1)  # keep your id as string
    dream = {'id': dream_id, 'title': title, 'date': date, 'entry': entry}
    create_memory("dreams", json.dumps(dream), metadata={"id": dream_id})
    logger.info('Dream created successfully.')
    return dream

def get_dream(dream_id):
    logger.info(f'Fetching dream with id {dream_id}.')
    dream_id = str(dream_id)
    memories = get_memories("dreams")
    for memory in memories:
        dream = json.loads(memory['document'])
        if dream['id'] == dream_id:
            return dream
    raise ValueError(f"Dream with id {dream_id} not found")

def get_dreams():
    logger.info('Fetching all dreams.')
    memories = get_memories("dreams")
    dreams = [json.loads(memory['document']) for memory in memories]
    return dreams

def get_dream_analysis(dream_id):
    try:
        logger.info(f'Fetching dream analysis for dream id {dream_id}.')
        dream = get_dream(dream_id)
        if dream:
            if 'analysis' in dream and dream['analysis']:
                return dream['analysis']
            else:
                analysis = get_gpt_response(dream['entry'], "You are dreaming about")
                return analysis
        return None
    except Exception as e:
        logger.error(f"Error in get_dream_analysis: {e}")
        return None
    
def get_dream_image(dream_id):
    try:
        logger.info(f'Fetching dream image for dream id {dream_id}.')
        dream = get_dream(dream_id)
        if dream:
            if 'image' in dream:
                return dream['image']
            else:
                dreams = get_dreams()
                summary = get_dream_summary(dream['entry'])
                image = generate_dream_image(dreams, dream_id)
                return image
        return None
    except Exception as e:
        logger.error(f"Error in get_dream_image: {e}")
        return None

def update_dream_analysis_and_image(dream_id, analysis=None, image=None):
    logger.info(f'Updating dream analysis and image for dream id {dream_id}.')
    dream_id = str(dream_id)  
    dream = get_dream(dream_id)
    if dream:
        if analysis:
            dream['analysis'] = analysis
        if image:
            dream['image'] = image
        update_memory("dreams", dream_id, json.dumps(dream))  
        logger.info('Dream analysis and image updated successfully.')
        return dream
    return None