import json
from ExtractFitur import *
from Process import *

# Example features list
midi_file_path = "x (24).mid"  # Replace with your MIDI file path
windows = process_midi_file(midi_file_path)
features = extract_features(windows)
# Save to a JSON file
with open("midi_features.json", "w") as outfile:
    json.dump(features, outfile)
