from flask import Flask, request, jsonify
from functools import wraps
import jwt
import requests
import json
from webargs import fields
from webargs.flaskparser import use_args
from memories import (
    create_dream,
    get_dreams,
    get_dream,
    update_dream_analysis_and_image,
    get_dream_analysis,
    get_dream_image,
    search_dreams,
    delete_dream
)
from actions import search_chat_with_dreams, regular_chat
from agentlogger import log
import traceback

# Define all your endpoints here, and use the app object passed as an argument to bind them
def register_endpoints(app):
    # Placeholder for user's image style preferences
    user_style_preferences = {}
    
    dream_args = {
        "title": fields.Str(required=True),
        "date": fields.Str(required=True),
        "entry": fields.Str(required=True),
        "id_token": fields.Str(required=True),
    }

    update_dream_args = {
        "analysis": fields.Str(),
        "image": fields.Str(),
    }

    chat_args = {
        "function_name": fields.Str(required=True),
        "prompt": fields.Str(required=True),
    }

    regular_chat_args = {
        "message": fields.Str(required=True),
    }

    search_args = {
        "query": fields.Str(required=True),
    }

    # Placeholder for user's image style preferences
    user_style_preferences = {}


    def get_apple_public_key(kid):
        keys = requests.get("https://appleid.apple.com/auth/keys").json()["keys"]
        for key_dict in keys:
            if key_dict["kid"] == kid:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_dict))
                return public_key
        raise Exception(f"No matching key found for kid {kid}")


    def decode_and_verify_token(id_token):
        header = jwt.get_unverified_header(id_token)
        public_key = get_apple_public_key(header["kid"])
        return jwt.decode(id_token, public_key, audience="com.jamesfeura.lucidjournal", algorithms=['RS256'])


    def extract_user_email_from_token(id_token):
        decoded_token = decode_and_verify_token(id_token)
        return decoded_token.get("email")


    def handle_jwt_token(func):
        @wraps(func)  # This line will preserve the original function's name
        def wrapper(*args, **kwargs):
            try:
                id_token = request.headers.get("Authorization").split(" ")[1]
                userEmail = extract_user_email_from_token(id_token)
                return func(*args, **kwargs, userEmail=userEmail)
            except jwt.InvalidTokenError:
                log(f"Invalid ID token", type="error")
                return jsonify({"error": "Invalid ID token"}), 401
            except Exception as e:
                log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
                return jsonify({"error": "Internal server error"}), 500
        return wrapper


    @app.route("/api/dreams", methods=["POST"], endpoint='create_dream_endpoint')
    @use_args(dream_args)
    @handle_jwt_token
    def create_dream_endpoint(args, userEmail):
        dream = create_dream(args["title"], args["date"], args["entry"], userEmail)
        if dream is None or "id" not in dream:
            log(f"Dream creation failed with data {args}", type="error")
            return jsonify({"error": "Dream creation failed"}), 500
        log(f"Successfully created dream with data {dream}", type="info")
        return jsonify(dream), 200


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


    @app.route("/api/dreams", methods=["GET"], endpoint='get_dreams_endpoint')
    @handle_jwt_token
    def get_dreams_endpoint(userEmail):
        dreams = get_dreams(userEmail)
        return jsonify(dreams), 200


    @app.route("/api/dreams/<dream_id>", methods=["GET"])
    @handle_jwt_token
    def get_dream_endpoint(dream_id, userEmail):
        dream = get_dream(dream_id)
        if dream is None or dream["metadata"]["useremail"] != userEmail:
            log(f"Dream with id {dream_id} not found.", type="error")
            return jsonify({"error": f"Dream with id {dream_id} not found."}), 404
        log(f"Successfully fetched dream with id {dream_id}", type="info")
        return jsonify(dream), 200


    @app.route("/api/dreams/<string:dream_id>/analysis", methods=["GET"])
    @handle_jwt_token
    def get_dream_analysis_endpoint(dream_id, userEmail):
        dream = get_dream(dream_id)
        if dream is None or dream["metadata"]["useremail"] != userEmail:
            log(f"Unauthorized access attempt to dream with id {dream_id} by user {userEmail}.", type="error")
            return jsonify({"error": "Unauthorized access."}), 401
        analysis = get_dream_analysis(dream_id)
        log(f"Successfully retrieved analysis for dream_id {dream_id}: {analysis}", type="info")
        return jsonify(analysis)


    @app.route("/api/dreams/<string:dream_id>/image", methods=["GET"])
    @handle_jwt_token
    def get_dream_image_endpoint(dream_id, userEmail):
        dream = get_dream(dream_id)
        if dream is None or dream["metadata"]["useremail"] != userEmail:
            log(f"Error occurred: Dream with id {dream_id} not found.", type="error", color="red")
            return jsonify({"error": f"Dream with id {dream_id} not found."}), 404
        userPreferredStyle = user_style_preferences.get(userEmail, {}).get("style", "renaissance")
        userPreferredQuality = user_style_preferences.get(userEmail, {}).get("quality", "low")
        image = get_dream_image(dream_id, userPreferredStyle, userPreferredQuality)
        log(f"Successfully retrieved image for dream_id {dream_id}", type="info")
        return jsonify({"image": image})


    @app.route("/api/user/image-style", methods=["POST"])
    @handle_jwt_token
    def update_image_style(userEmail):
        style = request.json.get("style")
        user_style_preferences.setdefault(userEmail, {})["style"] = style
        return jsonify({"status": "success", "message": "Image style updated!"})


    @app.route("/api/user/image-quality", methods=["POST"])
    @handle_jwt_token
    def set_user_image_quality(userEmail):
        quality = request.get_json().get("quality")
        if quality not in ["low", "medium", "high"]:
            return jsonify({"error": "Invalid image quality value"}), 400
        user_style_preferences.setdefault(userEmail, {})["quality"] = quality
        return jsonify({"message": "Image quality preference updated successfully."})


    @app.route("/api/dreams/search", methods=["POST"])
    @use_args(search_args)
    @handle_jwt_token
    def search_dreams_endpoint(args, userEmail):
        dreams = search_dreams(args["query"], userEmail)
        log(f"Successfully retrieved search results: {dreams}", type="info")
        return jsonify(dreams)


    @app.route("/api/chat", methods=["POST"])
    @use_args(regular_chat_args)
    @handle_jwt_token
    def chat_endpoint(args, userEmail):
        response = regular_chat(args["message"], userEmail)
        log(f"Successfully retrieved chat response: {response}", type="info")
        return jsonify({"response": response})


    @app.route("/api/dreams/search-chat", methods=["POST"])
    @use_args(chat_args)
    @handle_jwt_token
    def search_chat_with_dreams_endpoint(args, userEmail):
        response = search_chat_with_dreams(args["function_name"], args["prompt"], userEmail)
        log(f"Successfully retrieved chat search results: {response}", type="info")
        return jsonify(response)


    @app.route("/api/dreams/<string:dream_id>", methods=["DELETE"])
    @handle_jwt_token
    def delete_dream_endpoint(dream_id, userEmail):
        # Check if the dream exists and belongs to the user
        dream = get_dream(dream_id)
        if dream is None or dream["metadata"]["useremail"] != userEmail:
            log(f"Unauthorized deletion attempt of dream with id {dream_id} by user {userEmail}.", type="error")
            return jsonify({"error": "Unauthorized access."}), 401
        
        # Call the delete_dream function from your database module
        result = delete_dream(dream_id)
        if result:
            log(f"Successfully deleted dream with id {dream_id}", type="info")
            return jsonify({"message": f"Dream with id {dream_id} successfully deleted."}), 200
        else:
            log(f"Failed to delete dream with id {dream_id}", type="error")
            return jsonify({"error": f"Failed to delete dream with id {dream_id}."}), 500