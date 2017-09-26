import glob
import json
import colour
import numpy as np
import os

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.ticker as mtick

import audiometrics
import textmetrics

fig_size = plt.rcParams["figure.figsize"]
fig_size[0] = 16
fig_size[1] = 0.8
plt.rcParams["figure.figsize"] = fig_size
plt.subplots_adjust(left=0,right=1, top=0.8, bottom=0.1)
plt.rcParams.update({'font.size': 21})

base_path =  os.environ['BASE_PATH']
ref_data_dir = base_path + 'training_dataset/'

# set up color scheme
red = colour.Color("#B0413E")
yellow = colour.Color("#F9E884")
green = colour.Color("#709775")
units = 100
red_to_yellow = list(red.range_to(yellow,units))
yellow_to_green = list(yellow.range_to(green,10*units))
colours = red_to_yellow + yellow_to_green
colors = [i.hex for i in colours]
colors.extend(list(reversed(colors)))
included_frac = 99.
bin_percentiles = [(100-included_frac)/2.+i*(included_frac/len(colors)) for i in range(0,len(colors)+1)]
#add red bins for outside included_frac
colors = [red.hex] + colors + [red.hex]

###########################################################################################################

def create_image(user_score, values, min, max, filename, percentage = False, round = True, zero_is_good = False):

    bin_edges = [np.percentile(values, i) for i in bin_percentiles]
    widths = [bin_edges[0]]
    for i in range(1,len(bin_edges)):
        widths.append(bin_edges[i]-bin_edges[i-1])
    widths.append(max-bin_edges[-1])
    weights = [[width] for width in widths]
    data = [[1] for width in widths]

    plt.hist(data, weights = weights, bins=1, color = colors, orientation="horizontal", stacked=True)
    ax = plt.gca()
    ax.set_xlim(min,max)
    ax.set_ylim(0.8,1.2)
    ax.get_yaxis().set_visible(False)

    #handle under/overflow
    if user_score < min + 0.025*(max-min):
        placement = min + 0.025*(max-min)
    elif user_score > max - 0.015*(max-min):
        placement = max- 0.015*(max-min)
    else:
        placement = user_score

    index = 0
    for i,edge in enumerate(bin_edges):
        if edge >= user_score:
            index = i
            break

    if not user_score and zero_is_good:
        display_color = green.hex
    else:
        display_color = colors[index]

    if round:
        display_score = str(int(user_score))
    else:
        display_score = '{0:.1f}'.format(user_score)

    if percentage:
        display_score = display_score + '%'


    el = Ellipse((2, -1), 0.5, 0.5)
    ax.add_patch(el)
    ann = ax.annotate(display_score,
                      xy=(placement, 1), xycoords='data',
                      xytext=(-33, 0), textcoords='offset points',
                      size=35, va="center",ha="left",
                      bbox=dict(boxstyle="round", fc=display_color, ec="k"),
                      arrowprops=dict(arrowstyle="wedge,tail_width=1.",
                                      fc=display_color, ec="k",
                                      patchA=None,
                                      patchB=el,
                                      relpos=(0, 0.5)))
    ax.tick_params(axis='x', which='major', pad=12)

    if percentage:
        fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
        xticks = mtick.FormatStrFormatter(fmt)
        ax.xaxis.set_major_formatter(xticks)

    plt.savefig(filename, transparent=True, bbox_inches='tight',dpi=800)
    plt.clf()


###########################################################################################################

def make_avg_word_score_plot(user_score, timestamp):
    filename = base_path + '/app/static/' + timestamp + '/average_word_score.png'

    reference_inputs = [file for file in glob.glob(ref_data_dir + '*.json') if '_unknown_words' not in file]

    min = 70
    max = 100

    values = []
    # make reference distribution
    for i, ref in enumerate(reference_inputs):
#        if i > 5:
#            break
        values.append(audiometrics.get_avg_word_score(ref))

    create_image(user_score, values, min, max, filename, percentage = True)


###########################################################################################################

def make_pitch_variation_plot(user_score, timestamp):
    filename = base_path + '/app/static/' + timestamp + '/pitch_variation.png'

    reference_inputs = [file for file in glob.glob(ref_data_dir + '*.json') if '_unknown_words' not in file]

    min = 0
    max = 50

    values = []
    # make reference distribution
    for i, ref in enumerate(reference_inputs):
#        if i > 5:
#            break
        values.append(audiometrics.get_pitch_variation(ref))

    create_image(user_score, values, min, max, filename, percentage = True)


###########################################################################################################

def make_avg_wpm_plot(user_score, timestamp):
    filename = base_path + '/app/static/' + timestamp + '/avg_wpm.png'

    reference_inputs = [file for file in glob.glob(ref_data_dir + '*.srt')]

    min = 75
    max = 225

    values = []
    # make reference distribution
    for i, ref in enumerate(reference_inputs):
#        if i > 5:
#            break
        values.append(textmetrics.get_avg_wpm(ref))

    create_image(user_score, values, min, max, filename)


###########################################################################################################

def make_wpm_variation_plot(user_score, timestamp):
    filename = base_path + '/app/static/' + timestamp + '/wpm_variation.png'

    reference_inputs = [file for file in glob.glob(ref_data_dir + '*.srt')]

    min = 0
    max = 50

    values = []
    # make reference distribution
    for i, ref in enumerate(reference_inputs):
#        if i > 5:
#            break
        values.append(textmetrics.get_wpm_variation(ref))

    create_image(user_score, values, min, max, filename, percentage = True)


###########################################################################################################

def make_filler_word_rate_plot(user_score, timestamp):
    filename = base_path + '/app/static/' + timestamp + '/filler_word_rate.png'

    reference_srts = [file for file in glob.glob(ref_data_dir + '*.srt')]
    reference_txts = [file for file in glob.glob(ref_data_dir + '*.txt')]

    min = 0
    max = 5

    values = []
    # make reference distribution
    for i in range(len(reference_srts)):
#        if i > 5:
#            break
        values.append(textmetrics.get_filler_word_rate(reference_srts[i],reference_txts[i]))

    create_image(user_score, values, min, max, filename, round = False)


###########################################################################################################

def make_repeated_word_rate_plot(user_score, timestamp):
    filename = base_path + '/app/static/' + timestamp + '/repeated_word_rate.png'

    reference_srts = [file for file in glob.glob(ref_data_dir + '*.srt')]
    reference_txts = [file for file in glob.glob(ref_data_dir + '*.txt')]

    min = 0
    max = 2

    values = []
    # make reference distribution
    for i in range(len(reference_srts)):
#        if i > 5:
#            break
        values.append(textmetrics.get_repeated_word_rate(reference_srts[i],reference_txts[i]))

    create_image(user_score, values, min, max, filename, round = False, zero_is_good = True)


###########################################################################################################
