import glob
import json
import colour
import numpy as np
import os
import pickle

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.ticker as mtick

import audiometrics
import textmetrics

fig_size = plt.rcParams["figure.figsize"]
fig_size[0] = 20
#fig_size[0] = 30
fig_size[1] = 0.8
plt.rcParams["figure.figsize"] = fig_size
plt.subplots_adjust(left=0,right=1, top=0.8, bottom=0.1)
plt.rcParams.update({'font.size': 25})
#plt.rcParams.update({'font.size': 20})

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

testing = False

###########################################################################################################

def create_image(user_score, filename, timestamp, percentage = False, round = True, zero_is_good = False):
    output_filename = base_path + '/app/static/' + timestamp + '/'+ filename +'.png'
    ref_filename = base_path + '/app/static/references/'+ filename

    fig = pickle.load(file(ref_filename+'.pickle'))
    bin_edges = pickle.load(file(ref_filename+'_bin_edges.pickle'))

    ax = plt.gca()
    min,max = ax.get_xlim()
    

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
                      xytext=(-40, 0), textcoords='offset points',
                      size=45, va="center",ha="left",
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

    extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    plt.savefig(output_filename, transparent=True,bbox_inches=extent.expanded(1.1, 2.5),dpi=800)
#    plt.savefig(filename, transparent=True,bbox_inches=extent.expanded(1.2, 2.5),dpi=800)

    plt.clf()


###########################################################################################################

def make_ref(values, min, max, filename, percentage = False):
    print "making reference",filename

    fig = plt.figure()

    bin_edges = [np.percentile(values, i) for i in bin_percentiles]
    widths = [bin_edges[0]]
    for i in range(1,len(bin_edges)):
        widths.append(bin_edges[i]-bin_edges[i-1])
    widths.append(max-bin_edges[-1])
    weights = [[width] for width in widths]
    data = [[1] for width in widths]

    print "plotting"
    plt.hist(data, weights = weights, bins=1, color = colors, orientation="horizontal", stacked=True)
    ax = plt.gca()
    ax.set_xlim(min,max)
    ax.set_ylim(0.8,1.2)
    ax.get_yaxis().set_visible(False)

    ax.tick_params(axis='x', which='major', pad=12)
    if percentage:
        fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
        xticks = mtick.FormatStrFormatter(fmt)
        ax.xaxis.set_major_formatter(xticks)

    extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    print "saving files"
    plt.savefig(filename+'.png', transparent=True,bbox_inches=extent.expanded(1.1, 2.5),dpi=800)

    pickle.dump(fig, file(filename+'.pickle', 'w'))
    pickle.dump(bin_edges, file(filename+'_bin_edges.pickle', 'w'))
