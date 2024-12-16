import numpy as np

def extract_ATB(pitches):
    
    histogram, _ = np.histogram(pitches * 127, bins=128, range=(0,127))
    return normalize(histogram) 

def extract_RTB(pitches):
    
    differ = np.diff(pitches) * 127
  
    histogram, _ = np.histogram(differ, bins=255, range=(-127,127))
    return normalize(histogram) 

def extract_FTB(pitches):
    
    differ = (pitches - pitches[0]) * 127
 
    histogram, _ = np.histogram(differ, bins=255,range=(-127,127))
    return normalize(histogram) 

def normalize(histogram):
    hist_sum = np.sum(histogram)
    if hist_sum == 0:  
        return histogram  
    return histogram / hist_sum  


def extract_features(normalized_windows):
    
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
