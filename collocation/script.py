# -*- coding: utf-8 -*-
import sys
import re
from pymorphy import get_morph
import operator
#import itertools
import math


def get_words(file_name, index):
    
    morph = get_morph('')
    print "Getting words from " + file_name + "..."

    words = []
    pattern = re.compile("(([\w]+[-'])*[\w']+'?)", re.U)

    # try:
    f = open(file_name, 'r')
    file_text = f.read()
    f.close()
    file_text = unicode(file_text, 'utf8').upper()
    file_text = file_text.replace('--', ' -- ')
    tokens = file_text.split()
    previous_percentage = -1
    for idx, token in enumerate(tokens):
        m = pattern.match(token)
        if m:
            word = m.group()
	    info = morph.get_graminfo(word)
	    if len(info) < 2:
		continue
	    if not info[0]['class'] in [u"П", u"С", u"Г"]:
		continue
	    norm = info[0]['norm']
            words.append(norm)
            if norm in index:
                index[norm] += 1
            else:
                index[norm] = 1
        percentage = 100 * idx / len(tokens)
        if percentage != previous_percentage and percentage % 5 == 0:
            print "Getting words: " + str(percentage) + "% done"
            previous_percentage = percentage
    # except:
    #     print "error occured"

    return words


class Bigram:
    def __init__(self):
        self.bigram = None


def bigrams_mean(bigrams_index, text_words, window_size):
    print "Calculating bigrams by mean..."
    words_count = len(text_words)
    if words_count < window_size:
        return bigrams_index

    previous_percentage = -1
    for idx in range(0, words_count - window_size + 1):
        window = text_words[idx:idx+window_size]
        #bigrams = list(itertools.combinations(window, 2))
        for i in range(0, len(window) - 1):
            for j in range(i + 1, len(window)):
                t_value = window[i], window[j]
                if t_value in bigrams_index:
                    bigrams_index[t_value].n += 1
                    bigrams_index[t_value].lengths.append(j - i)
                else:
                    bigram = Bigram()
                    bigram.bigram = t_value
                    bigram.n = 1
                    bigram.lengths = []
                    bigram.lengths.append(j - i)
                    bigrams_index[t_value] = bigram
        percentage = 100 * idx / words_count
        if percentage != previous_percentage and percentage % 5 == 0:
            print "Calculating bigrams by mean: " + str(percentage) + "% done"
            previous_percentage = percentage

    for k, v in bigrams_index.items():
        v.d = sum(v.lengths) / float(v.n)
        summa = 0
        for length in v.lengths:
            summa += (length - v.d) ** 2
        if v.n > 1:
            v.s = summa / float(v.n - 1)
        else:
            v.s = -1

    return


def t(sorted_bigrams, index, out_file_name):
    collocations = dict()
    words_count = len(index)

    print "Calculating t value for bigrams..."
    previous_percentage = -1
    for idx, b in enumerate(sorted_bigrams):
        b1_count = index[b.bigram[0]]
        b2_count = index[b.bigram[1]]

        p1 = b1_count / float(words_count)
        p2 = b2_count / float(words_count)

        mu = p1*p2
        hi = b.n / float(words_count)
        t_value = (hi - mu) / math.sqrt(hi / float(words_count))

        if t_value < 2.576:
            collocations[b.bigram] = t_value

        percentage = 100 * idx / len(sorted_bigrams)
        if percentage != previous_percentage:
            print "Calculating t value for bigrams: " + str(percentage) + "% done"
            previous_percentage = percentage

    sorted_collocations = sorted(collocations.iteritems(), key=operator.itemgetter(1))

    f = open(out_file_name, 'w')
    for sc, w in sorted_collocations:
        f.write(sc[0].encode("utf-8") + " " + sc[1].encode("utf-8") + " " + str(w) + "\n")
    f.close()

    return sorted_collocations


def hi2(sorted_bigrams, index, out_file_name):
    collocations = dict()
    words_count = len(index)
    print "Calculating hi2 value for bigrams..."
    previous_percentage = -1

    bigrams_count = len(sorted_bigrams)
    bigrams_index = dict()
    for idx, b in enumerate(sorted_bigrams):
        b0 = b.bigram[0]
        b1 = b.bigram[1]

        if not (b0 in bigrams_index):
            tup = set(), set(), set(), set()
            bigrams_index[b0] = tup
        if not (b1 in bigrams_index):
            tup = set(), set(), set(), set()
            bigrams_index[b1] = tup

        bigrams_index[b0][0].add(idx)
        bigrams_index[b1][1].add(idx)
        percentage = 100 * idx / len(sorted_bigrams)
        if percentage != previous_percentage:
            print "Calculating hi2 value for bigrams: " + str(percentage) + "% done"
            previous_percentage = percentage


    for idx, b in enumerate(sorted_bigrams):
        b0 = b.bigram[0]
        b1 = b.bigram[1]

        O11 = b.n

        O22 = bigrams_count - len(bigrams_index[b0][0] | bigrams_index[b1][1])
        O21 = len(bigrams_index[b0][0] - bigrams_index[b1][1])
        O12 = len(bigrams_index[b1][1] - bigrams_index[b0][2])

        summa = float((O11 + O12) * (O11 + O21) * (O12 + O22) * (O21 + O22))
        hi2 = words_count * (O11 * O22 - O12 * O21) ** 2 / summa

        if hi2 < 2.576:
            collocations[b.bigram] = hi2

        percentage = 100 * idx / len(sorted_bigrams)
        if percentage != previous_percentage:
            print "Calculating hi2 value for bigrams: " + str(percentage) + "% done"
            previous_percentage = percentage

    sorted_collocations = sorted(collocations.iteritems(), key=operator.itemgetter(1))

    f = open(out_file_name, 'w')
    for sc, w in sorted_collocations:
        f.write(sc[0].encode("utf-8") + " " + sc[1].encode("utf-8") + " " + str(w) + "\n")
    f.close()

    return sorted_collocations


def main():

    args_count = len(sys.argv)
    if args_count < 2:
        print "First command line argument must be directory with input files"
        return 0

    in_dir = sys.argv[1]
    print "Input dir: " + in_dir

    index = dict()
    window_size = 5
    bigrams_index = dict()

    import os
    files = os.listdir(in_dir)
    for idx, file_name in enumerate(files):
	print idx, "/", len(files)
        text_words = get_words(in_dir + '/' + file_name, index)

        f = open("words", 'a')
        for word in text_words:
            f.write(word.encode("utf-8")+"\n")
        f.close()
	print "Got words: ", len(text_words)
        bigrams_mean(bigrams_index, text_words, window_size)

    sorted_bigrams = list(reversed(sorted(bigrams_index.values(), key=operator.attrgetter('n'))))

    f = open("bigrams_mean", 'w')
    for b in sorted_bigrams:
        f.write(b.bigram[0].encode("utf-8") + " " + b.bigram[1].encode("utf-8") + "\n")
        f.write(str(b.n))
        f.write("\n")
        for length in b.lengths:
            f.write(str(length) + " ")
        f.write("\n")
        f.write(str(b.d))
        f.write("\n")
        f.write(str(b.s))
        f.write("\n")

    f.close()

    t_collocations = t(sorted_bigrams, index, "collocations_t")
    hi2_collocations = hi2(sorted_bigrams, index, "collocations_hi2")

main()
