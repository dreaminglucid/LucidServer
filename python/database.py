from agentmemory.memory import (
    create_memory,
    get_memories,
    update_memory,
    get_memory
)
import json

dreams = []

def create_dream(title, date, entry):
    dream = {'id': len(dreams) + 1, 'title': title, 'date': date, 'entry': entry}
    dreams.append(dream)
    create_memory("dreams", json.dumps(dream), metadata={"id": dream['id']})  # Convert the dream dictionary to a string
    return dream

def get_dreams():
    memories = get_memories("dreams")
    dreams = [json.loads(memory['document']) for memory in memories]
    return dreams

def get_dream(dream_id):
    memories = get_memory("dreams", dream_id)
    if memories:
        return json.loads(memories[0]['document'])
    return None

def update_dream_analysis_and_image(dream_id, analysis, image):
    for dream in dreams:
        if dream['id'] == dream_id:
            dream['analysis'] = analysis
            dream['image'] = image
            update_memory("dreams", dream_id, dream)
            return dream
    return None

def get_dream_analysis(dream_id):
    for dream in dreams:
        if dream['id'] == dream_id:
            return dream.get('analysis')
    return None