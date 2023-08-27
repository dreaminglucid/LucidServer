import time
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from agentlogger import log
from agentmemory import create_memory, get_memories, update_memory, get_memory, search_memory, delete_memory, export_memory_to_json, get_client
from lucidserver.actions import generate_dream_analysis, generate_dream_image, get_image_summary


def create_dream(title, date, entry, userEmail):
    try:
        # Step 1: Initial log to confirm function entry
        log(f"Entering create_dream function with title: {title}, date: {date}, entry: {entry}, userEmail: {userEmail}", type="debug")

        # Construct metadata
        metadata = {
            "title": title,
            "date": date,
            "entry": entry,
            "useremail": userEmail,
        }
        # Log the constructed metadata
        log(f"Constructed metadata: {metadata}", type="debug")

        # Construct document
        document = f"{title}\n{entry}"
        # Log the constructed document
        log(f"Constructed document: {document}", type="debug")

        # Call create_memory to store the dream and get its generated UUID
        memory_id = create_memory("dreams", document, metadata=metadata)
        
        # Step 2: Log the returned UUID directly
        log(f"Returned memory_id from create_memory: {memory_id}", type="debug")

        # Step 3: Validate the memory ID before proceeding
        if not memory_id or not isinstance(memory_id, str):
            # Log the type of the returned memory_id for debugging
            log(f"Invalid or missing Memory ID: {memory_id}. Type: {type(memory_id)}. Aborting...", type="error")
            return None

        log(f"Generated memory ID: {memory_id}", type="info")

        # Step 4: Fetch the memory to validate it's saved correctly
        dream = get_memory("dreams", memory_id)
        
        if not dream:
            log("Could not fetch dream from memory. Returning None.", type="error")
            return None

        # Log the fetched dream
        log(f"Fetched dream from memory: {dream}", type="info")

        # Additional check to validate that the fetched dream corresponds to the generated UUID
        if dream.get("id", "") != memory_id:
            log(f"Fetched dream ID does not match generated UUID. Fetched: {dream.get('id', '')}, Expected: {memory_id}", type="error")
            return None

        # Step 5: Return a dictionary containing both the dream and the generated UUID
        return {"id": memory_id, "dream": dream}

    except Exception as e:
        log(f"Exception occurred in create_dream: {e}", type="error")
        return None

def get_dream(dream_id):
    """Retrieve a specific dream by ID.

    Args:
        dream_id (str): ID of the dream to retrieve.

    Returns:
        dict: Retrieved dream object or None if not found.
    """
    log(f"Initiating retrieval of dream with id {dream_id}.", type="info")

    # Fetching the dream
    dream = get_memory("dreams", dream_id)
    if dream is None:
        log(f"Dream with id {dream_id} not found.", type="error", color="red")
        return None

    # Constructing the dream data
    dream_data = {
        "id": dream["id"],
        "document": dream["document"],
        "metadata": {
            "title": dream["metadata"]["title"],
            "date": dream["metadata"]["date"],
            "entry": dream["metadata"]["entry"],
            "useremail": dream["metadata"]["useremail"],
        }
    }

    # Optionally, extract analysis and image from metadata if present
    if "analysis" in dream["metadata"]:
        dream_data["analysis"] = dream["metadata"]["analysis"]
    if "image" in dream["metadata"]:
        dream_data["image"] = dream["metadata"]["image"]

    log(
        f"Successfully retrieved dream with id {dream_id}: {dream_data}", type="info")
    return dream_data


def get_dreams(userEmail):
    """Retrieve all dreams for a specific user.

    Args:
        userEmail (str): Email of the user.

    Returns:
        list: List of dreams for the user.
    """
    log("Fetching all dreams.", type="info")
    memories = get_memories("dreams", n_results=2222)
    dreams = []
    for memory in memories:
        if "useremail" in memory["metadata"] and memory["metadata"]["useremail"] == userEmail:
            dream_data = {
                "id": memory["id"],
                "document": memory["document"],
                "metadata": {
                    "title": memory["metadata"]["title"],
                    "date": memory["metadata"]["date"],
                    "entry": memory["metadata"]["entry"],
                    "useremail": memory["metadata"]["useremail"],
                }
            }
            # Optionally, extract analysis and image from metadata if present
            if "analysis" in memory["metadata"]:
                dream_data["analysis"] = memory["metadata"]["analysis"]
            if "image" in memory["metadata"]:
                dream_data["image"] = memory["metadata"]["image"]

            dreams.append(dream_data)

    log(
        f"Debug: Retrieved dreams for userEmail {userEmail}: {dreams}", type="info")
    return dreams


def get_dream_analysis(dream_id, max_retries=5):
    """Fetch analysis for a dream.

    Args:
        dream_id (str): ID of the dream.
        max_retries (int, optional): Maximum number of retries. Defaults to 5.

    Returns:
        str: Dream analysis or None if not found.
    """
    try:
        log(f"Fetching dream analysis for dream id {dream_id}.", type="info")
        dream = get_dream(dream_id)
        for _ in range(max_retries):
            analysis = generate_dream_analysis(
                dream["metadata"]["entry"], "You are dreaming about"
            )
            if analysis:
                return analysis
            time.sleep(5)
        log(
            f"Failed to get dream analysis after {max_retries} attempts.",
            type="error",
            color="red",
        )
        return None
    except Exception as e:
        log(f"Error in get_dream_analysis: {e}", type="error", color="red")
        return None


def get_dream_image(dream_id, style="renaissance", quality="low", max_retries=5):
    """Fetch an image for a dream.

    Args:
        dream_id (str): ID of the dream.
        style (str, optional): Style for the image. Defaults to "renaissance".
        quality (str, optional): Quality of the image. Defaults to "low".
        max_retries (int, optional): Maximum number of retries. Defaults to 5.

    Returns:
        str: Dream image or None if not found.
    """
    try:
        log(f"Fetching dream image for dream id {dream_id}.", type="info")
        dream = get_dream(dream_id)
        log(f"Debug: Retrieved dream object: {dream}", type="info")

        # Log the style being used
        log(f"Using image style: {style}", type="info")

        # get useremail from dream metadata, updated line
        userEmail = dream["metadata"]["useremail"]
        dreams = get_dreams(userEmail)  # pass userEmail to get_dreams()
        summary = get_image_summary(dream["metadata"]["entry"])
        for _ in range(max_retries):
            image = generate_dream_image(dreams, dream_id, style, quality)
            if image:
                return image
            time.sleep(5)
        log(
            f"Failed to get dream image after {max_retries} attempts.",
            type="error",
            color="red",
        )
        return None
    except Exception as e:
        log(f"Error in get_dream_image: {e}", type="error", color="red")
        return None


def update_dream_analysis_and_image(dream_id, analysis=None, image=None):
    """Update the analysis and image for a dream.

    Args:
        dream_id (str): ID of the dream.
        analysis (str, optional): New analysis. Defaults to None.
        image (str, optional): New image. Defaults to None.

    Returns:
        dict: Updated dream object or None if not found.
    """
    log(
        f"Initiating update for dream analysis and image for dream id {dream_id}.", type="info")

    # Fetching the dream
    dream = get_dream(dream_id)
    if dream is None:
        log(f"Dream with id {dream_id} not found.", type="error", color="red")
        return None

    # Validating metadata
    metadata = dream.get("metadata")
    if metadata is None:
        log(f"Metadata for dream with id {dream_id} not found.",
            type="error", color="red")
        return None

    # Ensuring analysis and image are valid
    if analysis:
        if isinstance(analysis, str):  # Validate the type or content of analysis as needed
            metadata["analysis"] = analysis
        else:
            log(f"Invalid analysis data for dream id {dream_id}.",
                type="error", color="red")
            return None

    if image:
        if isinstance(image, str):  # Validate the type or content of image as needed
            metadata["image"] = image
        else:
            log(f"Invalid image data for dream id {dream_id}.",
                type="error", color="red")
            return None

    # Logging the state before the update
    log(f"Updating dream id {dream_id} with metadata: {metadata}", type="info")

    # Updating the memory
    try:
        update_memory("dreams", dream_id, metadata=metadata)
        log("Dream analysis and image updated successfully.", type="info")
        return dream
    except Exception as e:
        log(f"Failed to update dream id {dream_id}. Error: {str(e)}",
            type="error", color="red")
        return None


def search_dreams(keyword, user_email):
    log(f"Searching dreams for keyword: {keyword} and user email: {user_email}.", type="info")
    search_results = search_memory("dreams", keyword, n_results=100)
    dreams = [
        {
            "id": memory["id"],
            "document": memory["document"],
            "metadata": {
                key: memory["metadata"][key]
                for key in ["date", "title", "entry", "analysis"]
                if key in memory["metadata"]
            },
        }
        for memory in search_results
        # filter results by user email, using lowercase 'useremail'
        if memory['metadata']['useremail'] == user_email
    ]
    return dreams


def delete_dream(id):
    """
    Delete a dream by ID.

    Arguments:
        id (str/int): The ID of the dream.

    Returns:
        bool: True if the dream was deleted, False otherwise.

    Example:
        >>> delete_dream("1")
    """

    dream_to_delete = get_memory(category="dreams", id=id)

    if dream_to_delete is None:
        log(
            f"WARNING: Tried to delete dream with ID {id}, but it does not exist.", type="warning")
        return False

    # Delete the dream using agentmemory's delete_memory function
    result = delete_memory(category="dreams", id=id)

    if result:
        log(f"Deleted dream with ID {id}")
        return True
    else:
        log(f"Failed to delete dream with ID {id}")
        return False


def export_memory_to_json(include_embeddings=True, userEmail=None):
    collections = get_client().list_collections()
    collections_dict = {}
    for collection in collections:
        collection_name = collection.name
        collections_dict[collection_name] = []
        memories = get_memories(
            collection_name, include_embeddings=include_embeddings)
        for memory in memories:
            if userEmail is None or memory.get('metadata', {}).get('userEmail') == userEmail:
                collections_dict[collection_name].append(memory)
    return collections_dict


def export_dreams_to_json_file(path="./dreams.json", userEmail=None):
    collections_dict = export_memory_to_json(include_embeddings=False, userEmail=userEmail)
    dreams = collections_dict.get('dreams', [])
    with open(path, "w") as outfile:
        json.dump(dreams, outfile)

def export_dreams_to_pdf(path="./dreams.pdf", userEmail=None):
    # Use get_dreams to fetch dreams for the given userEmail
    dreams = get_dreams(userEmail)
    
    # Initialize PDF document and story
    doc = SimpleDocTemplate(path, pagesize=letter)
    Story = []

    # Define some styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    title_style = styles['Heading1']
    entry_style = styles['BodyText']
    analysis_style = styles['Justify']

    # Populate the PDF content
    for dream in dreams:
        metadata = dream.get('metadata', {})
        title = metadata.get('title', 'No title available.')
        entry = metadata.get('entry', 'No entry available.')
        date = metadata.get('date', 'No date available.')  # Inside metadata
        analysis = dream.get('analysis', 'No analysis available.')  # Outside metadata

        # Add title, entry, date, and analysis to PDF as paragraphs
        Story.append(Paragraph(f"<strong>Title:</strong> {title}", title_style))
        Story.append(Spacer(1, 12))
        Story.append(Paragraph(f"<strong>Date:</strong> {date}", title_style))
        Story.append(Spacer(1, 12))
        Story.append(Paragraph(f"<strong>Entry:</strong> {entry}", entry_style))
        Story.append(Spacer(1, 12))
        Story.append(Paragraph(f"<strong>Analysis:</strong> {analysis}", analysis_style))
        Story.append(Spacer(1, 24))

    # Build the PDF
    doc.build(Story)

def export_dreams_to_txt(path="./dreams.txt", userEmail=None):
    collections_dict = export_memory_to_json(include_embeddings=False, userEmail=userEmail)
    dreams = collections_dict.get('dreams', [])
    with open(path, "w") as txtfile:
        for dream in dreams:
            title = dream.get('metadata', {}).get('title', '')
            entry = dream.get('metadata', {}).get('entry', '')
            analysis = dream.get('metadata', {}).get(
                'analysis', 'No analysis available.')  # Get analysis if available
            # Add analysis to TXT
            txtfile.write(
                f"Title: {title}\nEntry: {entry}\nAnalysis: {analysis}\n\n")
