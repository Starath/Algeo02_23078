import numpy as np

def extract_ATB(pitches):
    histogram = [0] * 128  # Array untuk pitch 0–127
    for pitch in pitches:
        index = int(round(pitch))
        if 0 <= index < 128:
            histogram[index] += 1
    return normalize(histogram) 

def extract_RTB(pitches):
    histogram = [0] * 255  # Array untuk perbedaan -127 hingga +127
    for i in range(len(pitches) - 1):
        diff = pitches[i + 1] - pitches[i]
        index = int(round(diff)) + 127
        if 0 <= index < 255:
            histogram[index] += 1  # Geser indeks ke 0–254
    return normalize(histogram) 

def extract_FTB(pitches):
    histogram = [0] * 255  # Array untuk perbedaan -127 hingga +127
    first_tone = pitches[0]
    for pitch in pitches:
        diff = pitch - first_tone
        index = int(round(diff)) + 127
        if 0 <= index < 255:
            histogram[index] += 1  # Geser indeks ke 0–254
    return normalize(histogram) 

def normalize(histogram):
    total = sum(histogram)
    return [x / total for x in histogram]

def extract_features(pitches):
    """
    Extracts ATB, RTB, and FTB features and combines them into a single feature vector.
    """
    atb = extract_ATB(pitches)
    rtb = extract_RTB(pitches)
    ftb = extract_FTB(pitches)
    combined_features = np.concatenate([atb, rtb, ftb])
    return combined_features
