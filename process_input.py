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
base_path =  os.environ['BASE_PATH']

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
#indices_to_split = subtitleprocessing.get_splitting_indices(subtitles, target_length = 10)
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

audioprocessing.remove_speechace_audio(audio_for_speechace)

# extract metrics from speechace results
avg_word_score = audiometrics.get_avg_word_score(json_file)
pitch_variation = audiometrics.get_pitch_variation(json_file)

# extract metrics from subtitles and plain text
avg_wpm = textmetrics.get_avg_wpm(srt_file)
wpm_variation = textmetrics.get_wpm_variation(srt_file)
filler_word_rate = textmetrics.get_filler_word_rate(srt_file, txt_file)
repeated_word_rate = textmetrics.get_repeated_word_rate(srt_file, txt_file)

visualizations.create_image(avg_word_score, 'avg_wpm', args.timestamp)
visualizations.create_image(wpm_variation, 'wpm_variation', args.timestamp, percentage = True)
visualizations.create_image(pitch_variation, 'pitch_variation', args.timestamp, percentage = True)
visualizations.create_image(avg_word_score, 'average_word_score', args.timestamp, percentage = True)
visualizations.create_image(filler_word_rate, 'filler_word_rate', args.timestamp, round = False)
visualizations.create_image(repeated_word_rate, 'repeated_word_rate', args.timestamp, round = False, zero_is_good = True)
