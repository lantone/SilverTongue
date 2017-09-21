import codecs
import re
import srt
import string


def vtt_to_srt(input):
    output = input.replace('.vtt','.srt')
    outlines= []
    with codecs.open(input,'r', 'utf-8') as f:
        lines = f.readlines()
    index = 0
    things_to_skip = ['WEBVTT',
                      'Kind:',
                      'Language:',
                      'Style:',
#                      'Translator:',
#                      'Reviewer:',
#                      '00:00:00.000',
                      '::',
                      ' }',
                      '##']

    for line in lines[:-1]:
        if any(thing_to_skip in line for thing_to_skip in things_to_skip):
            continue
        altered_line = re.sub(r'([\d]+)\.([\d]+)', r'\1,\2', line)
        altered_line = re.sub('<[^<]+?>', '', altered_line)
        if altered_line[0] == '0':
            altered_line = altered_line[:29]+'\n'
        outlines.append(altered_line)
        if line == "\n":
            outlines.append(str(index)+'\n')
            index += 1

    outfile = codecs.open(output, "w", "utf-8")
    for line in outlines[1:]:
        outfile.write(line)
    outfile.close()

    return output


# FIX OVERLAPPING SUBTITLES!!
def fix_srt_overlap(subtitles):
    if subtitles[0].end > subtitles[1].start:
        for i in range(len(subtitles)-1):
            subtitles[i].end = subtitles[i+1].start

    return subtitles


def get_subtitle_splitting(subtitles, target_length = 30):
    # split files into chunks for use with speechace API
    indices_to_split = []
    running_length = 0
    for i,subtitle in enumerate(subtitles):
        sub_length = subtitle.end - subtitle.start
        running_length += sub_length.total_seconds()
        if running_length >= target_length:
            indices_to_split.append(i)
            running_length = 0
    # add final index
    indices_to_split.append(len(subtitles))

    return indices_to_split

# adapted from: https://www.daniweb.com/programming/software-development/code/216839/number-to-word-converter-python

############# globals ################
ones = ["", "one ","two ","three ","four ", "five ",
        "six ","seven ","eight ","nine "]
tens = ["ten ","eleven ","twelve ","thirteen ", "fourteen ",
        "fifteen ","sixteen ","seventeen ","eighteen ","nineteen "]
twenties = ["","","twenty ","thirty ","forty ",
            "fifty ","sixty ","seventy ","eighty ","ninety "]
thousands = ["","thousand ","million ", "billion ", "trillion ",
             "quadrillion ", "quintillion ", "sextillion ", "septillion ",
             "octillion ", "nonillion ", "decillion ", "undecillion ",
             "duodecillion ", "tredecillion ", "quattuordecillion ",
             "quindecillion", "sexdecillion ", "septendecillion ",
             "octodecillion ", "novemdecillion ", "vigintillion "]

# integer number to english word conversion
# can be used for numbers as large as 999 vigintillion
# (vigintillion --> 10 to the power 60)
# tested with Python24      vegaseat      07dec2006
def int2word(n):
    if not any(c.isdigit() for c in n):
        return n
    #remove non digits
    n = ''.join(c for c in n if c.isdigit())
    """
    convert an integer number n into a string of english words
    """


    # break the number into groups of 3 digits using slicing
    # each group representing hundred, thousand, million, billion, ...
    n3 = []
    r1 = ""
    # create numeric string
    ns = str(n)

    #special case of zero
    if ns == '0':
        return 'zero'

    for k in range(3, 33, 3):
        r = ns[-k:]
        q = len(ns) - k
        # break if end of ns has been reached
        if q < -2:
            break
        else:
            if  q >= 0:
                n3.append(int(r[:3]))
            elif q >= -1:
                n3.append(int(r[:2]))
            elif q >= -2:
                n3.append(int(r[:1]))
        r1 = r

    # break each group of 3 digits into
    # ones, tens/twenties, hundreds
    # and form a string
    nw = ""
    for i, x in enumerate(n3):
        b1 = x % 10
        b2 = (x % 100)//10
        b3 = (x % 1000)//100
        if x == 0:
            continue  # skip
        else:
            t = thousands[i]
        if b2 == 0:
            nw = ones[b1] + t + nw
        elif b2 == 1:
            nw = tens[b1] + t + nw
        elif b2 > 1:
            nw = twenties[b2] + ones[b1] + t + nw
        if b3 > 0:
            nw = ones[b3] + "hundred " + nw

    return nw.strip()


def replace_numbers(input):
    for i,line in enumerate(input):
        text = line.content.encode('utf-8')
        words = text.split()
        output_words = []
        for word in words:
            has_number = any(c.isdigit() for c in word)
            if has_number:
                subword_list = word.split('-')
                for subword in subword_list:
                    output_words.append(int2word(subword.translate(None, string.punctuation)))
            else:
                output_words.append(word)
        input[i].content = ' '.join(word for word in output_words)

    return input


# process subtitle file into list
def srt_to_sub(srt_file):
    with codecs.open(srt_file,'r', 'utf-8') as myfile:
        data = myfile.read()
    subtitle_generator = srt.parse(data)
    subtitles = list(subtitle_generator)
    # account for youtube's 'scrolling' subtitles
    subtitles = fix_srt_overlap(subtitles)
    # replace digits with numbers
    subtitles = replace_numbers(subtitles)

    return subtitles


# find points to split files into chunks for use with speechace API
def get_splitting_indices(subtitles, target_length = 30):
    indices_to_split = []
    running_length = 0
    for i,subtitle in enumerate(subtitles):
        sub_length = subtitle.end - subtitle.start
        running_length += sub_length.total_seconds()
        if running_length >= target_length:
            indices_to_split.append(i)
            running_length = 0
    # add final index
    indices_to_split.append(len(subtitles))

    return indices_to_split


# takes Subtitle list and splitting points, returns list of formatted text chunks
def get_speechace_sub_list(subtitles, indices_to_split):
    start_chunk = 0
    subs_for_speechace = []
    for i in indices_to_split:
        # get text and remove newline characters
#        text = ' '.join(str(i.content.encode('utf-8').replace('\n',' ')) for i in subtitles[start_chunk:i])
        text = ' '.join(str(i.content.replace('\n',' ')) for i in subtitles[start_chunk:i])
        # remove punctuation
        text = ' '.join(word.strip(string.punctuation) for word in text.split())
        start_chunk = i
        subs_for_speechace.append(text)

    return subs_for_speechace


# takes Subtitle list and saves a text file with the transcript
def sub_to_txt(input, subtitles):
    output = input.replace('.srt','.txt')
    # get text and remove newline characters
#    text = ' '.join(str(i.content.encode('utf-8').replace('\n',' ')) for i in subtitles)
    text = ' '.join(str(i.content.replace('\n',' ')) for i in subtitles)
#    with codecs.open(output,'w', 'utf-8') as f:
    with codecs.open(output,'w') as f:
        f.write(text)

    return output
