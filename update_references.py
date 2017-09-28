#!/usr/bin/env python
import os
import glob

import visualizations
import textmetrics
import audiometrics

# set up output directory

base_path =  os.environ['BASE_PATH']
ref_input_path = base_path + '/training_dataset/'
ref_output_path = os.environ['BASE_PATH'] + '/app/static/references/'


wpm_vals = []
sig_wpm_vals = []
sig_pitch_vals = []
word_score_vals = []
filler_rate_vals = []
repeated_rate_vals = []

reference_inputs = [file for file in glob.glob(ref_input_path + '*.json') if '_unknown_words' not in file]
reference_srts = [file for file in glob.glob(ref_input_path + '*.srt')]
reference_txts = [file for file in glob.glob(ref_input_path + '*.txt')]

for i, ref in enumerate(reference_inputs):
    print i,
    wpm_vals.append(textmetrics.get_avg_wpm(reference_srts[i]))
    sig_wpm_vals.append(textmetrics.get_wpm_variation(reference_srts[i]))
    sig_pitch_vals.append(audiometrics.get_pitch_variation(ref))
    word_score_vals.append(audiometrics.get_avg_word_score(ref))
    filler_rate_vals.append(textmetrics.get_filler_word_rate(reference_srts[i],reference_txts[i]))
    repeated_rate_vals.append(textmetrics.get_repeated_word_rate(reference_srts[i],reference_txts[i]))
print
visualizations.make_ref(wpm_vals,75,225,ref_output_path+'avg_wpm')
visualizations.make_ref(sig_wpm_vals,0,50,ref_output_path+'wpm_variation', percentage = True)
visualizations.make_ref(sig_pitch_vals,0,50,ref_output_path+'pitch_variation', percentage = True)
visualizations.make_ref(word_score_vals,55,95,ref_output_path+'average_word_score', percentage = True)
visualizations.make_ref(filler_rate_vals,0,5,ref_output_path+'filler_word_rate')
visualizations.make_ref(repeated_rate_vals,0,2,ref_output_path+'repeated_word_rate')
