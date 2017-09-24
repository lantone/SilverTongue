import subtitleprocessing
import numpy as np


def get_avg_wpm(srt_file):
    subs = subtitleprocessing.srt_to_sub(srt_file)
    wpms = []
    start_time = subs[0].start
    n_words = 0
    for sub in subs:
        n_words += len(sub.content.split())
        time = (sub.end - start_time).total_seconds()
        if time > 5:
            wpm = n_words/time*60
            wpms.append(wpm)
            n_words = 0
            start_time = sub.end
    mean = np.mean(wpms)

    if np.isnan(mean):
        return 0
    else:
        return mean


def get_wpm_variation(srt_file):
    subs = subtitleprocessing.srt_to_sub(srt_file)
    wpms = []
    start_time = subs[0].start
    n_words = 0
    for sub in subs:
        n_words += len(sub.content.split())
        time = (sub.end - start_time).total_seconds()
        if time > 5:
            wpm = n_words/time*60
            wpms.append(wpm)
            n_words = 0
            start_time = sub.end
    rms = np.std(wpms)
    mean = np.mean(wpms)
    if np.isnan(rms) or np.isnan(mean) or mean == 0:
        return 0
    else:
        return rms/mean*100


def get_filler_word_rate(srt_file, txt_file):
    words_to_check = ['so','like','um','okay','just']

    subs = subtitleprocessing.srt_to_sub(srt_file)
    total_time = (subs[-1].end - subs[0].start).total_seconds()
    with open(txt_file, 'r') as myfile:
        txt=myfile.read()
    txt_words = txt.split()
    num_fillers = 0
    for word in words_to_check:
        num_fillers += txt_words.count(word)

    return num_fillers/(total_time/60.)


def get_repeated_word_rate(srt_file, txt_file):

    subs = subtitleprocessing.srt_to_sub(srt_file)
    total_time = (subs[-1].end - subs[0].start).total_seconds()
    with open(txt_file, 'r') as myfile:
        txt=myfile.read()
    txt_words = txt.split()
    num_repeats = 0
    for j,word in enumerate(txt_words[:-1]):
        if word == txt_words[j+1]:
            num_repeats += 1

    return num_repeats/(total_time/60.)


