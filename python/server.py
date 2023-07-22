from flask import Flask, request, jsonify
from database import create_dream, get_dreams, get_dream, update_dream_analysis_and_image, get_dream_analysis, get_dream_image
from openai_utils import search_dreams, search_chat_with_dreams
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/api/dreams', methods=['POST'])
def create_dream_endpoint():
    logger.info("Received request at /api/dreams POST endpoint.")
    data = request.json
    dream = create_dream(data['title'], data['date'], data['entry'])
    if dream is None:
        return jsonify({'error': 'Dream creation failed'}), 500
    if 'id' not in dream:
        return jsonify({'error': 'Dream ID not generated'}), 500
    logger.info(f"Response: {dream}")
    return jsonify(dream), 200


@app.route('/api/dreams/<string:dream_id>', methods=['PUT'])
def update_dream_endpoint(dream_id):
    logger.info(f"Received request at /api/dreams/{dream_id} PUT endpoint.")
    data = request.json
    analysis = data.get('analysis', None)
    image = data.get('image', None)
    dream = update_dream_analysis_and_image(dream_id, analysis, image)
    logger.info(f"Response: {dream}")
    return jsonify(dream), 200 if dream is not None else 500


@app.route('/api/dreams', methods=['GET'])
def get_dreams_endpoint():
    logger.info("Received request at /api/dreams GET endpoint.")
    dreams = get_dreams()
    logger.info(f"Response: {dreams}")
    return jsonify(dreams)


@app.route('/api/dreams/<string:dream_id>', methods=['GET'])
def get_dream_endpoint(dream_id):
    logger.info(f"Received request at /api/dreams/{dream_id} GET endpoint.")
    dream = get_dream(dream_id)
    if dream is None:
        return jsonify({'error': 'Dream not found'}), 404
    return jsonify(dream)


@app.route('/api/dreams/<string:dream_id>/analysis', methods=['GET'])
def get_dream_analysis_endpoint(dream_id):
    logger.info(
        f"Received request at /api/dreams/{dream_id}/analysis GET endpoint.")
    try:
        analysis = get_dream_analysis(dream_id)
        logger.info(f"Response: {analysis}")
        return jsonify(analysis)
    except ValueError as e:
        logger.error(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 404


@app.route('/api/dreams/<string:dream_id>/image', methods=['GET'])
def get_dream_image_endpoint(dream_id):
    logger.info(
        f"Received request at /api/dreams/{dream_id}/image GET endpoint.")
    try:
        image = get_dream_image(dream_id)
        logger.info(f"Response: {image}")
        return jsonify({'image': image})
    except ValueError as e:
        logger.error(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 404


@app.route('/api/dreams/search', methods=['POST'])
def search_dreams_endpoint():
    logger.info("Received request at /api/dreams/search POST endpoint.")
    data = request.json
    keyword = data.get('query', '')
    dreams = search_dreams(keyword)
    logger.info(f"Response: {dreams}")
    return jsonify(dreams)


@app.route('/api/dreams/search-chat', methods=['POST'])
def search_chat_with_dreams_endpoint():
    logger.info("Received request at /api/dreams/search-chat POST endpoint.")
    data = request.json
    response = search_chat_with_dreams(data['prompt'])
    logger.info(f"Response: {response}")
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
