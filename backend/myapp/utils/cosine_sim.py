import json
import numpy as np
from scipy.spatial.distance import cosine  # Import the cosine function from scipy
from backend.myapp.utils.ExtractFitur import extract_features
from backend.myapp.utils.Process import process_midi_file
from backend.myapp.utils.prototype import vectorize_features

def load_feature_database(database_path):
    """
    Loads the feature database from a JSON file.
    """
    with open(database_path, "r") as f:
        feature_database = json.load(f)
    return feature_database


def compare_query_to_database(query_file_path, database_path, window_size=20, slide=4):
    """
    Compares a query MIDI file to the feature database and returns the best match based on cosine similarity.
    """
    # Load the feature database
    feature_database = load_feature_database(database_path)

    # Process the query MIDI file and extract features
    normalized_windows = process_midi_file(query_file_path, window_size, slide)
    # if not normalized_windows:
    #     print(f"Error: No valid features found for the query file {query_file_path}.")
    #     return None
    
    # Extract features for the query
    query_features = extract_features(normalized_windows)
    
    # Combine the feature vectors for the query (mean of ATB, RTB, FTB)
    query_feature_vector = vectorize_features(query_features)

    # Compare the query feature vector to the database using cosine similarity
    similarities = {}
    for midi_file, db_vector in feature_database.items():
        # Compute cosine similarity using scipy's cosine function
        similarity_score = 1 - cosine(query_feature_vector, np.array(db_vector))  # Cosine similarity = 1 - cosine distance
        if similarity_score > 0.55:  # Filter similarities higher than 0.55
            similarities[midi_file] = similarity_score
    
    # Sort the results by similarity score (highest first)
    sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    print(sorted_similarities)

    # Return the best match (highest similarity)
    best_match_file = sorted_similarities[0]
    return best_match_file, sorted_similarities[0][1]  


# Example usage
if __name__ == "__main__":
    query_file_path = "x (24).mid"  # Replace with the path to the query MIDI file
    database_path = "midi_feature_database.json"  # Path to the stored feature database

    best_match_file, similarity_score = compare_query_to_database(query_file_path, database_path)
    
    

    # if best_match_file:
    #     print(f"Best match found: {best_match_file} with similarity score: {similarity_score:.4f}")
 