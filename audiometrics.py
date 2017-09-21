import json
import numpy as np
import codecs

def get_avg_word_score(json_file):
    with open(json_file) as json_data:
        data = json.load(json_data)
    word_scores = [word["quality"] for word in data if word["quality"] > 0]
    mean = np.mean(word_scores)
    if np.isnan(mean):
        return 0
    else:
        return mean

def get_pitch_variation(json_file):
    with open(json_file) as json_data:
        data = json.load(json_data)
        pitches = [(syl["pitch_high"]+syl['pitch_low'])/2. for word in data 
                for syl in word["syllables"] 
                if syl["quality"] > 0
                if syl["pitch_high"]+syl['pitch_low'] > 0]
    rms = np.std(pitches)
    mean = np.mean(pitches)
    if np.isnan(rms) or np.isnan(mean) or mean == 0:
        return 0
    else:
        return rms/mean*100
