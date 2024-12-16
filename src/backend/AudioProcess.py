import mido
import numpy as np
from typing import List, Tuple

def read_midi_file(file_path: str) -> List[Tuple[int, int]]:
    """
    Reads a MIDI file and extracts notes from the main channel (Channel 1).
    """
    midi = mido.MidiFile(file_path)
    notes = []

    for track in midi.tracks:
        for msg in track:
            if msg.type == 'note_on': 
                notes.append((msg.note, msg.time)) 

    if not notes:
        print("Warning: No notes found on Channel 1 (MIDI Channel 0).")
    return notes

def windowing(notes: np.ndarray, window_size: int, slide: int) -> np.ndarray:
    """
    Splits notes into overlapping windows with a sliding window mechanism.
    """
    if notes.size == 0:
        print("Warning: Notes array is empty, skipping windowing.")
        return np.array([]) 

    # NumPy stride tricks for efficient windowing
    num_windows = (len(notes) - window_size) // slide + 1
    if num_windows <= 0:
        print("Error: Not enough notes for even one window. Exiting.")
        return np.array([])

    windows = np.lib.stride_tricks.sliding_window_view(notes, (window_size, 2))[::slide]
    return windows.reshape(num_windows, window_size, 2)

def normalize_pitch(notes: np.ndarray) -> np.ndarray:
    """
    Normalizes the pitch of notes
    """
    pitches = notes[:, 0]  # Extract pitch column
    mean_pitch = np.mean(pitches)
    std_pitch = np.std(pitches)
    if std_pitch == 0:  # Avoid division by zero
        std_pitch = 1
    normalized = (pitches - mean_pitch) / std_pitch
    return normalized

def process_midi_file(file_path: str, window_size: int = 20, slide: int = 4) -> List[np.ndarray]:
    """
    Main function to process the MIDI file for query by humming.
    """
    notes = read_midi_file(file_path)
    if not notes:
        print("Error: No notes to process. Exiting.")
        return []

    notes_array = np.array(notes)  # Convert to NumPy array for optimized processing
    windows = windowing(notes_array, window_size, slide)
    if windows.size == 0:
        print("Error: No windows created. Exiting.")
        return []

    normalized_windows = np.array([normalize_pitch(window) for window in windows])
    return normalized_windows


# Example usage
if __name__ == "__main__":
    midi_file_path = "x (24).mid"  # Replace with your MIDI file path
    windows = process_midi_file(midi_file_path)
    print(windows)
