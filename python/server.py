from flask import Flask, request, jsonify
from webargs import fields, validate
from webargs.flaskparser import use_args
from database import (
    create_dream,
    get_dreams,
    get_dream,
    update_dream_analysis_and_image,
    get_dream_analysis,
    get_dream_image,
)
from openai_utils import search_dreams, search_chat_with_dreams, regular_chat
from agentlogger import log, print_header, write_to_file
import traceback


app = Flask(__name__)

print_header("LUCID JOURNAL", font="slant", color="cyan")

# Request schemas
dream_args = {
    "title": fields.Str(required=True),
    "date": fields.Str(required=True),
    "entry": fields.Str(required=True),
}

update_dream_args = {
    "analysis": fields.Str(),
    "image": fields.Str(),
}

search_args = {
    "query": fields.Str(required=True),
}

chat_args = {
    "function_name": fields.Str(required=True),
    "prompt": fields.Str(required=True),
}

regular_chat_args = {
    "message": fields.Str(required=True),
}


@app.route("/api/dreams", methods=["POST"])
@use_args(dream_args)
def create_dream_endpoint(args):
    try:
        log(
            f"Received POST request at /api/dreams with data {args}", type="info")
        dream = create_dream(args["title"], args["date"], args["entry"])
        if dream is None:
            log(f"Dream creation failed with data {args}", type="error")
            return jsonify({"error": "Dream creation failed"}), 500
        if "id" not in dream:
            log(f"Dream ID not generated for data {args}", type="error")
            return jsonify({"error": "Dream ID not generated"}), 500
        log(f"Successfully created dream with data {dream}", type="info")
        return jsonify(dream), 200
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/dreams/<string:dream_id>", methods=["PUT"])
@use_args(update_dream_args)
def update_dream_endpoint(args, dream_id):
    try:
        log(
            f"Received PUT request at /api/dreams/{dream_id} with data {args}",
            type="info",
        )
        dream = update_dream_analysis_and_image(
            dream_id, args.get("analysis", None), args.get("image", None)
        )
        if dream is None:
            log(
                f"Dream update failed for dream_id {dream_id} with data {args}",
                type="error",
            )
            return jsonify({"error": "Dream update failed"}), 500
        log(
            f"Successfully updated dream with dream_id {dream_id} and data {dream}",
            type="info",
        )
        return jsonify(dream), 200
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/dreams", methods=["GET"])
def get_dreams_endpoint():
    try:
        log("Received GET request at /api/dreams", type="info")
        dreams = get_dreams()
        log(f"Successfully retrieved dreams: {dreams}", type="info")
        return jsonify(dreams)
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/dreams/<string:dream_id>", methods=["GET"])
def get_dream_endpoint(dream_id):
    try:
        log(f"Received GET request at /api/dreams/{dream_id}", type="info")
        dream = get_dream(dream_id)
        if dream is None:
            log(f"Dream not found for dream_id {dream_id}", type="error")
            return jsonify({"error": "Dream not found"}), 404
        log(
            f"Successfully retrieved dream with dream_id {dream_id}: {dream}",
            type="info",
        )
        return jsonify(dream)
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/dreams/<string:dream_id>/analysis", methods=["GET"])
def get_dream_analysis_endpoint(dream_id):
    try:
        log(
            f"Received GET request at /api/dreams/{dream_id}/analysis", type="info")
        analysis = get_dream_analysis(dream_id)
        log(
            f"Successfully retrieved analysis for dream_id {dream_id}: {analysis}",
            type="info",
        )
        return jsonify(analysis)
    except ValueError as e:
        log(f"Error occurred: {str(e)}", type="error", color="red")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/dreams/<string:dream_id>/image", methods=["GET"])
def get_dream_image_endpoint(dream_id):
    try:
        log(
            f"Received GET request at /api/dreams/{dream_id}/image", type="info")
        image = get_dream_image(dream_id)
        log(
            f"Successfully retrieved image for dream_id {dream_id}", type="info")
        return jsonify({"image": image})
    except ValueError as e:
        log(f"Error occurred: {str(e)}", type="error", color="red")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/chat", methods=["POST"])
@use_args(regular_chat_args)
def chat_endpoint(args):
    try:
        log(
            f"Received POST request at /api/chat with data {args}",
            type="info",
        )
        response = regular_chat(args["message"])
        log(f"Successfully retrieved chat response: {response}", type="info")

        return jsonify({"response": response})
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/dreams/search", methods=["POST"])
@use_args(search_args)
def search_dreams_endpoint(args):
    try:
        log(
            f"Received POST request at /api/dreams/search with data {args}", type="info"
        )
        dreams = search_dreams(args["query"])
        log(f"Successfully retrieved search results: {dreams}", type="info")
        return jsonify(dreams)
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/dreams/search-chat", methods=["POST"])
@use_args(chat_args)
def search_chat_with_dreams_endpoint(args):
    try:
        log(
            f"Received POST request at /api/dreams/search-chat with data {args}",
            type="info",
        )
        response = search_chat_with_dreams(
            args["function_name"], args["prompt"])
        log(
            f"Successfully retrieved chat search results: {response}", type="info")

        # return the entire response object, not just 'arguments'
        return jsonify(response)
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)
