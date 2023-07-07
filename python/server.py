from flask import Flask, request, jsonify
from database import create_dream, get_dreams, get_dream, update_dream_analysis_and_image, get_dream_analysis

app = Flask(__name__)

@app.route('/api/dreams', methods=['POST'])
def create_dream_endpoint():
    data = request.json
    dream = create_dream(data['title'], data['date'], data['entry'])
    return jsonify(dream)

@app.route('/api/dreams', methods=['GET'])
def get_dreams_endpoint():
    dreams = get_dreams()
    return jsonify(dreams)

@app.route('/api/dreams/<int:dream_id>', methods=['GET'])
def get_dream_endpoint(dream_id):
    dream = get_dream(dream_id)
    if dream is None:
        return jsonify({'error': 'Dream not found'}), 404
    return jsonify(dream)

@app.route('/api/dreams/<int:dream_id>/analysis', methods=['GET'])
def get_dream_analysis_endpoint(dream_id):
    analysis = get_dream_analysis(dream_id)
    if analysis is None:
        return jsonify({'error': 'Dream not found'}), 404
    return jsonify(analysis)

if __name__ == '__main__':
    app.run(debug=True)