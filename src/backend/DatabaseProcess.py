import os
import json
import numpy as np
from multiprocessing import Pool, cpu_count
import logging
from ExtractFitur import extract_features
from AudioProcess import process_midi_file

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def vectorize_features(features: dict[str, list]) -> np.ndarray:
    """
    Combines feature vectors by taking the mean of ATB, RTB, and FTB.
    """
    if not features or any(key not in features for key in ["ATB", "RTB", "FTB"]):
        logging.warning("Invalid features input. Returning zero vector.")
        return np.zeros(128 + 255 + 255)  # Dummy zero vector of combined dimensions
    
    combined_feature_vector = np.concatenate([
        np.mean(features["ATB"], axis=0),
        np.mean(features["RTB"], axis=0),
        np.mean(features["FTB"], axis=0)
    ])
    return combined_feature_vector


def process_single_midi_file(args):
    """
    Processes a single MIDI file to extract features.
    """
    midi_file, midi_folder, window_size, slide = args
    midi_path = os.path.join(midi_folder, midi_file)
    
    try:
        # Process the MIDI file and extract normalized windows
        normalized_windows = process_midi_file(midi_path, window_size, slide)
        
        if not normalized_windows or len(normalized_windows) == 0:
            logging.warning(f"No valid windows for {midi_file}. Skipping...")
            return None, None

        # Extract features (ATB, RTB, FTB)
        features = extract_features(normalized_windows)
        combined_feature_vector = vectorize_features(features).tolist()

        return midi_file, combined_feature_vector

    except Exception as e:
        logging.error(f"Error processing {midi_file}: {e}")
        return None, None


def build_feature_database(midi_folder: str, output_file: str, window_size: int = 20, slide: int = 4):
    """
    Constructs a feature database from MIDI files in the given folder and saves it as a JSON file.
    """
    feature_database = {}
    midi_files = [f for f in os.listdir(midi_folder) if f.endswith(".mid")]

    if not midi_files:
        logging.error("No MIDI files found in the specified folder.")
        return

    logging.info(f"Found {len(midi_files)} MIDI files. Processing...")

    # Parallel processing using multiprocessing
    with Pool(cpu_count()) as pool:
        args = [(midi_file, midi_folder, window_size, slide) for midi_file in midi_files]
        results = pool.map(process_single_midi_file, args)

    # Save valid results to the database
    for midi_file, combined_vector in results:
        if midi_file and combined_vector:
            feature_database[midi_file] = combined_vector

    # Save database to JSON
    with open(output_file, "w") as outfile:
        json.dump(feature_database, outfile, indent=4)

    logging.info(f"Feature database saved to {output_file}")


# Example usage
if __name__ == "__main__":
    midi_folder = "C:/Coding/Algeo02_23078/AudioDataset"  # Replace with the path to your MIDI folder
    output_file = "midi_feature_database.json"  # File to store the database
    build_feature_database(midi_folder, output_file)
