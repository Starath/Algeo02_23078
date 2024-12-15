import json
import numpy as np
from scipy.spatial.distance import cosine
from ExtractFitur import extract_features
from AudioProcess import process_midi_file
from DatabaseProcess import vectorize_features

def load_feature_database(database_path):
    with open(database_path, "r") as f:
        return json.load(f)

def compare_query_to_database(query_file_path, database_path, window_size=20, slide=4, threshold=0.55):
    database = load_feature_database(database_path)

    # Proses query MIDI
    normalized_windows = process_midi_file(query_file_path, window_size, slide)
    query_features = extract_features(normalized_windows)
    query_vector = vectorize_features(query_features)

    # Bandingkan dengan database
    results = []
    for midi_file, db_vector in database.items():
        similarity = 1 - cosine(query_vector, np.array(db_vector))
        if similarity >= threshold:
            results.append({"filename": midi_file, "similarity": round(similarity, 4)})

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results
