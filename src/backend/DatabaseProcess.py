import os
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from ExtractFitur import extract_features
from AudioProcess import process_midi_file


def vectorize_features(features: dict[str, list]) -> np.ndarray:
    
    return np.concatenate([
        np.mean(features["ATB"], axis=0),
        np.mean(features["RTB"], axis=0),
        np.mean(features["FTB"], axis=0)
    ])


def process_single_file(midi_file_path: str, window_size: int, slide: int) -> tuple:
    
    from pathlib import Path

    try:
        # Process the MIDI file and extract normalized windows
        normalized_windows = process_midi_file(midi_file_path, window_size, slide)
        
        # Extract features (ATB, RTB, FTB)
        features = extract_features(normalized_windows)
        
        # Combine the feature vectors (mean of ATB, RTB, FTB)
        combined_feature_vector = vectorize_features(features).tolist()
        
        file_name = Path(midi_file_path).name
        return file_name, combined_feature_vector

    except Exception as e:
        print(f"Error processing {midi_file_path}: {e}")
        return None, None


def build_feature_database(midi_folder: str, output_file: str, window_size: int = 20, slide: int = 4, max_workers: int = 4):
   
    from pathlib import Path

    midi_folder_path = Path(midi_folder)
    midi_files = [str(f) for f in midi_folder_path.glob("*.mid")]
    feature_database = {}

    print(f"Found {len(midi_files)} MIDI files. Processing with {max_workers} threads...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_single_file, file, window_size, slide) for file in midi_files]

        for future in as_completed(futures):
            file_name, combined_feature_vector = future.result()
            if file_name and combined_feature_vector:
                feature_database[file_name] = combined_feature_vector

    # save database to JSON file
    with open(output_file, "w") as outfile:
        json.dump(feature_database, outfile, indent=4)

    print(f"Feature database saved to {output_file}")

