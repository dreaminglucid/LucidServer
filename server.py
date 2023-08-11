from flask import Flask, request, jsonify
import jwt
import requests
import json
from webargs import fields
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
from agentlogger import log, print_header
import traceback


app = Flask(__name__)

print_header("LUCID JOURNAL", font="slant", color="cyan")

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


# Placeholder for user's image style preferences
user_style_preferences = {}


def get_apple_public_key(kid):
    keys = requests.get("https://appleid.apple.com/auth/keys").json()["keys"]
    for key_dict in keys:
        if key_dict["kid"] == kid:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_dict))
            return public_key
    raise Exception(f"No matching key found for kid {kid}")


@app.route("/api/dreams", methods=["POST"])
@use_args(dream_args)
def create_dream_endpoint(args):
    try:
        log(
            f"Received POST request at /api/dreams with data {args}", type="info")
        
        # Decode and verify JWT
        id_token = args.get("id_token")
        if not id_token:
            log(f"No ID token provided", type="error")
            return jsonify({"error": "No ID token provided"}), 400

        header = jwt.get_unverified_header(id_token)
        public_key = get_apple_public_key(header["kid"])
        decoded_token = jwt.decode(id_token, public_key, audience="com.jamesfeura.lucidjournal", algorithms=['RS256'])
        
        # Extract the user's email from the decoded token
        userEmail = decoded_token.get("email")
        
        dream = create_dream(args["title"], args["date"], args["entry"], userEmail)
        if dream is None:
            log(f"Dream creation failed with data {args}", type="error")
            return jsonify({"error": "Dream creation failed"}), 500
        if "id" not in dream:
            log(f"Dream ID not generated for data {args}", type="error")
            return jsonify({"error": "Dream ID not generated"}), 500
        log(f"Successfully created dream with data {dream}", type="info")
        return jsonify(dream), 200
    except jwt.InvalidTokenError:
        log(f"Invalid ID token", type="error")
        return jsonify({"error": "Invalid ID token"}), 401
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
        id_token = request.headers.get("Authorization").split(" ")[1]  # Extract the token from the header
        header = jwt.get_unverified_header(id_token)
        public_key = get_apple_public_key(header["kid"])
        decoded_token = jwt.decode(id_token, public_key, audience="com.jamesfeura.lucidjournal", algorithms=['RS256'])
        userEmail = decoded_token.get("email")
        dreams = get_dreams(userEmail)
        return jsonify(dreams), 200
    except jwt.InvalidTokenError:
        log(f"Invalid ID token", type="error")
        return jsonify({"error": "Invalid ID token"}), 401
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/dreams/<dream_id>", methods=["GET"])
def get_dream_endpoint(dream_id):
    try:
        log(f"Received GET request at /api/dreams/{dream_id}", type="info")

        # Decode and verify JWT
        id_token = request.headers.get("Authorization")
        if not id_token:
            raise Exception("No authorization token provided")
        id_token = id_token.split(" ")[1]  # Add this line
        header = jwt.get_unverified_header(id_token)
        public_key = get_apple_public_key(header["kid"])
        decoded_token = jwt.decode(id_token, public_key, audience="com.jamesfeura.lucidjournal", algorithms=['RS256'])
        
        # Extract the user's email from the decoded token
        userEmail = decoded_token.get("email")

        dream = get_dream(dream_id)
        if dream is None:
            log(f"Dream with id {dream_id} not found.", type="error")
            return jsonify({"error": f"Dream with id {dream_id} not found."}), 404
        if dream["metadata"]["useremail"] != userEmail:
            log(f"Unauthorized access attempt to dream with id {dream_id} by user {userEmail}.", type="error")
            return jsonify({"error": "Unauthorized access."}), 401
        log(f"Successfully fetched dream with id {dream_id}", type="info")
        return jsonify(dream), 200
    except jwt.InvalidTokenError:
        log(f"Invalid ID token", type="error")
        return jsonify({"error": "Invalid ID token"}), 401
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/dreams/<string:dream_id>/analysis", methods=["GET"])
def get_dream_analysis_endpoint(dream_id):
    try:
        # Decode and verify JWT
        id_token = request.headers.get("Authorization")
        if not id_token:
            raise Exception("No authorization token provided")
        id_token = id_token.split(" ")[1]  # Add this line
        header = jwt.get_unverified_header(id_token)
        public_key = get_apple_public_key(header["kid"])
        decoded_token = jwt.decode(id_token, public_key, audience="com.jamesfeura.lucidjournal", algorithms=['RS256'])

        # Extract the user's email from the decoded token
        userEmail = decoded_token.get("email")

        # Get the dream
        dream = get_dream(dream_id)
        if dream is None or dream["metadata"]["useremail"] != userEmail:
            raise ValueError(f"Dream with id {dream_id} not found.")
        
        log(f"Received GET request at /api/dreams/{dream_id}/analysis", type="info")
        analysis = get_dream_analysis(dream_id)
        log(f"Successfully retrieved analysis for dream_id {dream_id}: {analysis}", type="info")
        return jsonify(analysis)
    except jwt.InvalidTokenError:
        log(f"Invalid ID token", type="error")
        return jsonify({"error": "Invalid ID token"}), 401
    except ValueError as e:
        log(f"Error occurred: {str(e)}", type="error", color="red")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/dreams/<string:dream_id>/image", methods=["GET"])
def get_dream_image_endpoint(dream_id):
    try:
        # Decode and verify JWT
        id_token = request.headers.get("Authorization")
        if not id_token:
            raise Exception("No authorization token provided")
        id_token = id_token.split(" ")[1]  # Extract token from Bearer
        header = jwt.get_unverified_header(id_token)
        public_key = get_apple_public_key(header["kid"])
        decoded_token = jwt.decode(id_token, public_key, audience="com.jamesfeura.lucidjournal", algorithms=['RS256'])

        # Extract the user's email from the decoded token
        userEmail = decoded_token.get("email")

        # Get the dream
        dream = get_dream(dream_id)
        if dream is None or dream["metadata"]["useremail"] != userEmail:
            raise ValueError(f"Dream with id {dream_id} not found.")

        log(f"Received GET request at /api/dreams/{dream_id}/image", type="info")

        # Here, you'll retrieve the user's preferred style. For now, this is a placeholder:
        # In a real-world scenario, you would fetch this from the database or user settings.
        # Inside get_dream_image_endpoint
        userPreferredStyle = user_style_preferences.get(userEmail, "renaissance")

        # Fetch the user's preferred style and quality
        userPreferredStyle = user_style_preferences.get(userEmail, {}).get("style", "renaissance")
        userPreferredQuality = user_style_preferences.get(userEmail, {}).get("quality", "low")

        image = get_dream_image(dream_id, userPreferredStyle, userPreferredQuality)

        log(f"Successfully retrieved image for dream_id {dream_id}", type="info")
        return jsonify({"image": image})

    except jwt.InvalidTokenError:
        log(f"Invalid ID token", type="error")
        return jsonify({"error": "Invalid ID token"}), 401
    except ValueError as e:
        log(f"Error occurred: {str(e)}", type="error", color="red")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500
    
    
@app.route("/api/user/image-style", methods=["POST"])
def update_image_style():
    try:
        # Decode and verify JWT
        id_token = request.headers.get("Authorization")
        if not id_token:
            raise Exception("No authorization token provided")
        id_token = id_token.split(" ")[1]
        header = jwt.get_unverified_header(id_token)
        public_key = get_apple_public_key(header["kid"])
        decoded_token = jwt.decode(id_token, public_key, audience="com.jamesfeura.lucidjournal", algorithms=['RS256'])

        # Extract the user's email from the decoded token
        userEmail = decoded_token.get("email")

        # Update the user's image style preference
        style = request.json.get("style")
        if userEmail not in user_style_preferences or type(user_style_preferences[userEmail]) is not dict:
            user_style_preferences[userEmail] = {}
        user_style_preferences[userEmail]["style"] = style  # Store the style inside a dictionary for the user

        return jsonify({"status": "success", "message": "Image style updated!"})

    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"status": "error", "message": str(e)}), 500
    
    
@app.route("/api/user/image-quality", methods=["POST"])
def set_user_image_quality():
    try:
        # Decode and verify JWT
        id_token = request.headers.get("Authorization")
        if not id_token:
            raise Exception("No authorization token provided")
        id_token = id_token.split(" ")[1]  # Extract token from Bearer
        header = jwt.get_unverified_header(id_token)
        public_key = get_apple_public_key(header["kid"])
        decoded_token = jwt.decode(id_token, public_key, audience="com.jamesfeura.lucidjournal", algorithms=['RS256'])

        # Extract the user's email from the decoded token
        userEmail = decoded_token.get("email")

        # Extract the quality from the request body
        data = request.get_json()
        quality = data.get("quality")

        # Validate quality
        if quality not in ["low", "medium", "high"]:
            return jsonify({"error": "Invalid image quality value"}), 400

        # Set the quality in the user_style_preferences dictionary
        if userEmail not in user_style_preferences or type(user_style_preferences[userEmail]) is not dict:
            user_style_preferences[userEmail] = {}
        user_style_preferences[userEmail]["quality"] = quality

        return jsonify({"message": "Image quality preference updated successfully."})

    except jwt.InvalidTokenError:
        log(f"Invalid ID token", type="error")
        return jsonify({"error": "Invalid ID token"}), 401
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

        # Decode and verify JWT
        id_token = request.headers.get("Authorization")
        if not id_token:
            raise Exception("No authorization token provided")
        id_token = id_token.split(" ")[1]  # Extract the token from the header
        header = jwt.get_unverified_header(id_token)
        public_key = get_apple_public_key(header["kid"])
        decoded_token = jwt.decode(id_token, public_key, audience="com.jamesfeura.lucidjournal", algorithms=['RS256'])

        # Extract the user's email from the decoded token
        userEmail = decoded_token.get("email")

        # You might want to modify the search_dreams function to limit search results to the authenticated user
        dreams = search_dreams(args["query"], userEmail)
        log(f"Successfully retrieved search results: {dreams}", type="info")
        return jsonify(dreams)
    except jwt.InvalidTokenError:
        log(f"Invalid ID token", type="error")
        return jsonify({"error": "Invalid ID token"}), 401
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

        # Decode and verify JWT
        id_token = request.headers.get("Authorization")
        if not id_token:
            raise Exception("No authorization token provided")
        id_token = id_token.split(" ")[1]  # Extract the token from the header
        header = jwt.get_unverified_header(id_token)
        public_key = get_apple_public_key(header["kid"])
        decoded_token = jwt.decode(id_token, public_key, audience="com.jamesfeura.lucidjournal", algorithms=['RS256'])

        # Extract the user's email from the decoded token
        userEmail = decoded_token.get("email")

        response = regular_chat(args["message"], userEmail)  # Pass userEmail as an argument
        log(f"Successfully retrieved chat response: {response}", type="info")

        return jsonify({"response": response})
    except jwt.InvalidTokenError:
        log(f"Invalid ID token", type="error")
        return jsonify({"error": "Invalid ID token"}), 401
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

        # Decode and verify JWT
        id_token = request.headers.get("Authorization")
        if not id_token:
            raise Exception("No authorization token provided")
        id_token = id_token.split(" ")[1]  # Extract the token from the header
        header = jwt.get_unverified_header(id_token)
        public_key = get_apple_public_key(header["kid"])
        decoded_token = jwt.decode(id_token, public_key, audience="com.jamesfeura.lucidjournal", algorithms=['RS256'])

        # Extract the user's email from the decoded token
        userEmail = decoded_token.get("email")

        # Here, you can check if the user has premium membership before proceeding
        # ...

        response = search_chat_with_dreams(
            args["function_name"], args["prompt"], userEmail)  # Pass userEmail as an argument
        log(
            f"Successfully retrieved chat search results: {response}", type="info")

        # return the entire response object, not just 'arguments'
        return jsonify(response)
    except jwt.InvalidTokenError:
        log(f"Invalid ID token", type="error")
        return jsonify({"error": "Invalid ID token"}), 401
    except Exception as e:
        log(f"Unhandled exception occurred: {traceback.format_exc()}", type="error")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)