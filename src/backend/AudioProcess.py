import mido
import numpy as np
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

def read_midi_file(file_path: str) -> List[Tuple[int, int]]:

    try:
        midi = mido.MidiFile(file_path)
    except Exception as e:
        logging.error(f"Unable to read MIDI file '{file_path}'. Reason: {e}")
        return [(60, 0)] * 20  # dummy notes to prevent failure

    notes = []
    fallback_notes = []

    for track in midi.tracks:
        for msg in track:
            if msg.type == 'note_on':
                note_data = (msg.note, msg.time)
                if msg.channel == 1:
                    notes.append(note_data)
                fallback_notes.append(note_data)

    # prioritize Channel 1, fallback to all channels if empty
    if notes:
        return notes
    elif fallback_notes:
        logging.warning(f"No notes on Channel 1 in '{file_path}'. Using fallback (all channels).")
        return fallback_notes
    else:
        logging.warning(f"No notes found in '{file_path}'. Using dummy data.")
        return [(60, 0)] * 20  # dummy notes

def windowing(notes: np.ndarray, window_size: int, slide: int) -> np.ndarray:
    
    if len(notes) < window_size:
        logging.warning("Not enough notes for one window. Returning dummy windows.")
        dummy_window = np.array([(60, 0)] * window_size)
        return np.array([dummy_window])

    # Optimized windowing using stride_tricks
    num_windows = (len(notes) - window_size) // slide + 1
    windows = np.lib.stride_tricks.sliding_window_view(notes, (window_size, 2))[::slide]
    return windows.reshape(num_windows, window_size, 2)

def normalize_pitch(notes: np.ndarray) -> np.ndarray:
    
    pitches = notes[:, 0]  # extract pitch column
    if pitches.size == 0:
        logging.warning("Empty pitches array encountered during normalization.")
        return np.zeros_like(pitches)
    
    mean_pitch = np.mean(pitches)
    std_pitch = np.std(pitches) or 1  # avoid division by zero
    return (pitches - mean_pitch) / std_pitch

def process_midi_file(file_path: str, window_size: int = 20, slide: int = 4) -> List[np.ndarray]:
    
    notes = read_midi_file(file_path)
    notes_array = np.array(notes)

    # handle empty notes
    if notes_array.size == 0:
        logging.error("No notes to process. Exiting.")
        return []

    windows = windowing(notes_array, window_size, slide)
    normalized_windows = np.array([normalize_pitch(window) for window in windows])
    return normalized_windows

