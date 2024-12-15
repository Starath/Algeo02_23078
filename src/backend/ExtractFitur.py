import numpy as np

def extract_ATB(pitches):
    # histogram = [0] * 128  # Array untuk pitch 0–127
    # for pitch in pitches:
    #     index = int(round(pitch))
    #     if 0 <= index < 128:
    #         histogram[index] += 1
    histogram, _ = np.histogram(pitches * 127, bins=128, range=(0,127))
    return normalize(histogram) 

def extract_RTB(pitches):
    # histogram = [0] * 255  # Array untuk perbedaan -127 hingga +127
    # for i in range(len(pitches) - 1):
    #     diff = pitches[i + 1] - pitches[i]
    differ = np.diff(pitches) * 127
    #     index = int(round(diff)) + 127
    #     if 0 <= index < 255:
    #         histogram[index] += 1  # Geser indeks ke 0–254
    histogram, _ = np.histogram(differ, bins=255, range=(-127,127))
    return normalize(histogram) 

def extract_FTB(pitches):
    # histogram = [0] * 255  # Array untuk perbedaan -127 hingga +127
    # first_tone = pitches[0] 
    # for pitch in pitches:
    #     diff = pitch - first_tone
    differ = (pitches - pitches[0]) * 127
    #     index = int(round(diff)) + 127
    #     if 0 <= index < 255:
    #         histogram[index] += 1  # Geser indeks ke 0–254
    histogram, _ = np.histogram(differ, bins=255,range=(-127,127))
    return normalize(histogram) 

def normalize(histogram):
    hist_sum = np.sum(histogram)
    if hist_sum == 0:  # Check if the sum of the histogram is zero
        return histogram  # If sum is zero, return the original histogram
    return histogram / hist_sum  # Otherwise, normalize as usual


def extract_features(normalized_windows):
    """
    Extracts ATB, RTB, and FTB features and combines them into a single feature vector.
    """
    features = {
        "ATB": [],
        "RTB": [],
        "FTB": []
    }
    for window in normalized_windows:
        atb = extract_ATB(window)
        rtb = extract_RTB(window)
        ftb = extract_FTB(window)
        features["ATB"].append(atb.tolist())
        features["RTB"].append(rtb.tolist())
        features["FTB"].append(ftb.tolist())
    return features
