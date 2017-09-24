#!/usr/bin/env python
import json
import argparse
import sys
import os

import youtube
import subtitleprocessing
import audioprocessing
import speechace
import audiometrics
import textmetrics
import visualizations

# set to something small for short testing
#max_calls = 1
max_calls = 999

parser = argparse.ArgumentParser()
parser.add_argument("url")
parser.add_argument("timestamp")
args = parser.parse_args()


# set up output directory
base_path = '/Users/lantonel/SilverTongue/'
output_dir = base_path + '/app/static/' + args.timestamp + '/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
filename_base = output_dir + args.url

# get audio and subtitles from youtube
youtube.extractFromYoutube(args.url, output_dir)
m4a_file = filename_base + '.m4a'
vtt_file = filename_base + '.en.vtt'

# convert subtitles to srt and plain text
srt_file = subtitleprocessing.vtt_to_srt(vtt_file)
subtitles = subtitleprocessing.srt_to_sub(srt_file)
txt_file = subtitleprocessing.sub_to_txt(srt_file, subtitles)

# split up subtitles and audio for submitting to speechace
indices_to_split = subtitleprocessing.get_splitting_indices(subtitles, target_length = 30)
subs_for_speechace = subtitleprocessing.get_speechace_sub_list(subtitles, indices_to_split)
audio_for_speechace = audioprocessing.get_speechace_audio_list(m4a_file, 
                                                               subtitles, 
                                                               indices_to_split, 
                                                               output_dir)
# call speechace API
word_list, bad_chunks, unknown_word_list = speechace.activate_speechace(subs_for_speechace, 
                                                                        audio_for_speechace, 
                                                                        max_calls = max_calls, 
                                                                        verbose = True)

# write output of speechace processing
json_file = filename_base+'.json'
with open(json_file, mode='w') as outputFile:
    json.dump(word_list, outputFile, indent=4)


# extract metrics from speechace results
avg_word_score = audiometrics.get_avg_word_score(json_file)
visualizations.make_avg_word_score_plot(avg_word_score, args.timestamp)

pitch_variation = audiometrics.get_pitch_variation(json_file)
visualizations.make_pitch_variation_plot(pitch_variation, args.timestamp)


# extract metrics from subtitles and plain text
avg_wpm = textmetrics.get_avg_wpm(srt_file)
visualizations.make_avg_wpm_plot(avg_wpm, args.timestamp)

wpm_variation = textmetrics.get_wpm_variation(srt_file)
visualizations.make_wpm_variation_plot(wpm_variation, args.timestamp)

filler_word_rate = textmetrics.get_filler_word_rate(srt_file, txt_file)
visualizations.make_filler_word_rate_plot(filler_word_rate, args.timestamp)

repeated_word_rate = textmetrics.get_repeated_word_rate(srt_file, txt_file)
visualizations.make_repeated_word_rate_plot(repeated_word_rate, args.timestamp)
