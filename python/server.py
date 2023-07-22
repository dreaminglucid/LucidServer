from flask import Flask, request, jsonify
from database import create_dream, get_dreams, get_dream, update_dream_analysis_and_image, get_dream_analysis, get_dream_image
from openai_utils import search_dreams, search_chat_with_dreams
from agentlogger import log, print_header, write_to_file

app = Flask(__name__)

print_header('LUCID JOURNAL', font='slant', color='cyan')


@app.route('/api/dreams', methods=['POST'])
def create_dream_endpoint():
    log("Received request at /api/dreams POST endpoint.", type='info')
    data = request.json
    dream = create_dream(data['title'], data['date'], data['entry'])
    if dream is None:
        return jsonify({'error': 'Dream creation failed'}), 500
    if 'id' not in dream:
        return jsonify({'error': 'Dream ID not generated'}), 500
    log(f"Response: {dream}", type='info')
    return jsonify(dream), 200


@app.route('/api/dreams/<string:dream_id>', methods=['PUT'])
def update_dream_endpoint(dream_id):
    log(f"Received request at /api/dreams/{dream_id} PUT endpoint.", type='info')
    data = request.json
    analysis = data.get('analysis', None)
    image = data.get('image', None)
    dream = update_dream_analysis_and_image(dream_id, analysis, image)
    log(f"Response: {dream}", type='info')
    return jsonify(dream), 200 if dream is not None else 500


@app.route('/api/dreams', methods=['GET'])
def get_dreams_endpoint():
    log("Received request at /api/dreams GET endpoint.", type='info')
    dreams = get_dreams()
    log(f"Response: {dreams}", type='info')
    return jsonify(dreams)


@app.route('/api/dreams/<string:dream_id>', methods=['GET'])
def get_dream_endpoint(dream_id):
    log(f"Received request at /api/dreams/{dream_id} GET endpoint.", type='info')
    dream = get_dream(dream_id)
    if dream is None:
        return jsonify({'error': 'Dream not found'}), 404
    return jsonify(dream)


@app.route('/api/dreams/<string:dream_id>/analysis', methods=['GET'])
def get_dream_analysis_endpoint(dream_id):
    log(
        f"Received request at /api/dreams/{dream_id}/analysis GET endpoint.", type='info')
    try:
        analysis = get_dream_analysis(dream_id)
        log(f"Response: {analysis}", type='info')
        return jsonify(analysis)
    except ValueError as e:
        log(f"Error occurred: {str(e)}", type='error', color='red')
        return jsonify({'error': str(e)}), 404


@app.route('/api/dreams/<string:dream_id>/image', methods=['GET'])
def get_dream_image_endpoint(dream_id):
    log(
        f"Received request at /api/dreams/{dream_id}/image GET endpoint.", type='info')
    try:
        image = get_dream_image(dream_id)
        log(f"Response: {image}", type='info')
        return jsonify({'image': image})
    except ValueError as e:
        log(f"Error occurred: {str(e)}", type='error', color='red')
        return jsonify({'error': str(e)}), 404


@app.route('/api/dreams/search', methods=['POST'])
def search_dreams_endpoint():
    log("Received request at /api/dreams/search POST endpoint.", type='info')
    data = request.json
    keyword = data.get('query', '')
    dreams = search_dreams(keyword)
    log(f"Response: {dreams}", type='info')
    return jsonify(dreams)


@app.route('/api/dreams/search-chat', methods=['POST'])
def search_chat_with_dreams_endpoint():
    log("Received request at /api/dreams/search-chat POST endpoint.", type='info')
    data = request.json
    response = search_chat_with_dreams(data['prompt'])
    log(f"Response: {response}", type='info')
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)