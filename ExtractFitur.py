def extract_ATB(pitches):
    histogram = [0] * 128 
    for pitch in pitches:
        histogram[pitch] += 1
    return normalize(histogram) 

def extract_RTB(pitches):
    histogram = [0] * 255 
    for i in range(len(pitches) - 1):
        diff = pitches[i + 1] - pitches[i]
        histogram[diff + 127] += 1 
    return normalize(histogram) 

def extract_FTB(pitches):
    histogram = [0] * 255 
    first_tone = pitches[0]
    for pitch in pitches:
        diff = pitch - first_tone
        histogram[diff + 127] += 1 
    return normalize(histogram) 

def normalize(histogram):
    total = sum(histogram)
    return [x / total for x in histogram]
