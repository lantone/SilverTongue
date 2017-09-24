import string
import re

# adapted from: https://www.daniweb.com/programming/software-development/code/216839/number-to-word-converter-python

############# globals ################
ones = ["", "one ","two ","three ","four ", "five ",
        "six ","seven ","eight ","nine "]
tens = ["ten ","eleven ","twelve ","thirteen ", "fourteen ",
        "fifteen ","sixteen ","seventeen ","eighteen ","nineteen "]
twenties = ["","","twenty ","thirty ","forty ",
            "fifty ","sixty ","seventy ","eighty ","ninety "]
thousands = ["","thousand ","million ", "billion ", "trillion ",
             "quadrillion ", "quintillion ", "sextillion ", "septillion ","octillion ",
             "nonillion ", "decillion ", "undecillion ", "duodecillion ", "tredecillion ",
             "quattuordecillion ", "quindecillion", "sexdecillion ", "septendecillion ",
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

    #print n3  # test

    # break each group of 3 digits into
    # ones, tens/twenties, hundreds
    # and form a string
    nw = ""
    for i, x in enumerate(n3):
        b1 = x % 10
        b2 = (x % 100)//10
        b3 = (x % 1000)//100
        #print b1, b2, b3  # test
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
    words = input.split()
    output_words = []
    for word in words:
        has_number = any(c.isdigit() for c in word)
        if has_number:
            subword_list = word.split('-')
            for subword in subword_list:
                output_words.append(int2word(subword.translate(None, string.punctuation)))
        else:
            output_words.append(word)
    return ' '.join(word for word in output_words)

