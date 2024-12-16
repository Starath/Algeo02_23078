import json
import numpy as np
from scipy.spatial.distance import cdist
import logging
from ExtractFitur import extract_features
from AudioProcess import process_midi_file
from DatabaseProcess import vectorize_features

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def load_feature_database(database_path):
    """
    Loads the feature database from a JSON file.
    """
    try:
        with open(database_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Unable to load database '{database_path}'. Reason: {e}")
        return {}


def compare_query_to_database(query_file_path, database_path, window_size=20, slide=4, threshold=0.55):
    """
    Compares a query MIDI file to a feature database using cosine similarity.

    Args:
    - query_file_path (str): Path to the query MIDI file.
    - database_path (str): Path to the feature database (JSON).
    - window_size (int): Window size for sliding window processing.
    - slide (int): Step size for the sliding window.
    - threshold (float): Similarity threshold to filter results.

    Returns:
    - List[dict]: Sorted list of matching files with similarity scores.
    """
    # Load feature database
    database = load_feature_database(database_path)
    if not database:
        logging.error("Feature database is empty or invalid. Exiting.")
        return []

    # Process query MIDI file
    logging.info(f"Processing query file: {query_file_path}")
    normalized_windows = process_midi_file(query_file_path, window_size, slide)
    if not normalized_windows:
        logging.error("No valid windows generated from the query MIDI file.")
        return []

    query_features = extract_features(normalized_windows)
    query_vector = vectorize_features(query_features)

    if query_vector is None or np.all(query_vector == 0):
        logging.error("Query feature vector is invalid or empty.")
        return []

    # Convert database vectors to NumPy array for faster computation
    db_files = list(database.keys())
    db_vectors = np.array([database[midi_file] for midi_file in db_files])

    # Calculate cosine distances in bulk
    logging.info("Calculating cosine similarity...")
    distances = cdist([query_vector], db_vectors, metric='cosine')[0]
    similarities = 1 - distances  # Convert distances to cosine similarities

    # Filter results above threshold
    results = [
        {"filename": db_files[i], "similarity": round(similarities[i], 4)}
        for i in range(len(similarities)) if similarities[i] >= threshold
    ]

    # Sort results by similarity in descending order
    results.sort(key=lambda x: x["similarity"], reverse=True)
    logging.info(f"Found {len(results)} matching files.")
    return results


# Example usage
if __name__ == "__main__":
    # Paths for example usage
    query_file_path = "x (24).mid"  # Replace with your query MIDI file path
    database_path = "midi_feature_database.json"  # Path to the feature database JSON file
    window_size = 20
    slide = 4
    threshold = 0.55

    # Run the comparison
    matches = compare_query_to_database(query_file_path, database_path, window_size, slide, threshold)

    # Display the results
    if matches:
        print("\nMatching Files:")
        for match in matches:
            print(f"File: {match['filename']}, Similarity: {match['similarity']}")
    else:
        print("\nNo matching files found.")
