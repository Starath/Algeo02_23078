import os
import json
import numpy as np
from ExtractFitur import extract_features
from Process import process_midi_file

def build_feature_database(midi_folder: str, output_file: str, window_size: int = 20, slide: int = 4):
    """
    Constructs a feature database from MIDI files in the given folder and saves it as a JSON file.

    Args:
    - midi_folder (str): Folder containing MIDI files.
    - output_file (str): Path to save the JSON database.
    - window_size (int): Size of the sliding window.
    - slide (int): Sliding step size.
    """
    feature_database = {}

    # Iterate through all MIDI files in the folder
    for midi_file in os.listdir(midi_folder):
        if midi_file.endswith(".mid"):  # Only process MIDI files
            midi_path = os.path.join(midi_folder, midi_file)

            print(f"Processing {midi_file}...")

            # Process the MIDI file and extract normalized windows
            normalized_windows = process_midi_file(midi_path, window_size, slide)
            
            # if not normalized_windows:
            #     print(f"Skipping {midi_file}: No valid features found.")
            #     continue

            # Extract features (ATB, RTB, FTB)
            features = extract_features(normalized_windows)

            # Combine the feature vectors (mean of ATB, RTB, FTB)
            combined_feature_vector = np.concatenate([
                np.mean(features["ATB"], axis=0),
                np.mean(features["RTB"], axis=0),
                np.mean(features["FTB"], axis=0)
            ]).tolist()  # Convert to list for JSON compatibility

            # Add to database
            feature_database[midi_file] = combined_feature_vector

    # Save database to JSON
    with open(output_file, "w") as outfile:
        json.dump(feature_database, outfile, indent=4)

    print(f"Feature database saved to {output_file}")

# Example usage
if __name__ == "__main__":
    midi_folder = "C:\Coding\Algeo02_23078\AudioDataset"  # Replace with the path to your MIDI folder
    output_file = "midi_feature_database.json"  # File to store the database
    build_feature_database(midi_folder, output_file)
