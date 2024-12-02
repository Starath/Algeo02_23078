# File path: audio_processing/query_by_humming.py

import mido
import numpy as np
from typing import List, Tuple

def read_midi_file(file_path: str) -> List[Tuple[int, int]]:
    """
    Reads a MIDI file and extracts note events from the main melody (Channel 1).
    """
    midi = mido.MidiFile(file_path)
    notes = []

    for track in midi.tracks:
        for msg in track:
            if msg.type == 'note_on' and msg.channel == 0 :  # Channel 1 in MIDI
                notes.append((msg.note, msg.time))  # Note and its timestamp

    if not notes:
        print("Warning: No notes found on Channel 1 (MIDI Channel 0).")
    return notes

def windowing(notes: List[Tuple[int, int]], window_size: int, slide: int) -> List[List[Tuple[int, int]]]:
    """
    Splits notes into windows with a sliding window mechanism.
    """
    if not notes:
        print("Warning: Notes list is empty, skipping windowing.")
        return []
    windows = []
    for i in range(0, len(notes) - window_size + 1, slide):
        windows.append(notes[i:i + window_size])
    return windows

def normalize_pitch(notes: List[Tuple[int, int]]) -> List[float]:
    """
    Normalizes the pitch of notes using the formula NP(note) = (note - μ) / σ.
    """
    pitches = [note[0] for note in notes]
    mean_pitch = np.mean(pitches)
    std_pitch = np.std(pitches)
    
    if std_pitch == 0:  # Avoid division by zero
        std_pitch = 1
    
    normalized = [(note[0] - mean_pitch) / std_pitch for note in notes]
    return normalized

def process_midi_file(file_path: str, window_size: int = 20, slide: int = 4) -> List[List[float]]:
    """
    Main function to process the MIDI file for query by humming.
    """
    notes = read_midi_file(file_path)
    if not notes:
        print("Error: No notes to process. Exiting.")
        return []
    windows = windowing(notes, window_size, slide)
    if not windows:
        print("Error: No windows created. Exiting.")
        return []
    normalized_windows = [normalize_pitch(window) for window in windows]
    return normalized_windows

# Example usage
if __name__ == "__main__":
    midi_file_path = "x (24).mid"  # Replace with your MIDI file path
    processed_data = process_midi_file(midi_file_path, window_size=20, slide=4)
    print("Processed Melodic Windows (Normalized):")
    for window in processed_data:
        print(window)