# -*- coding: utf-8 -*-
import sys
import re
#from pymorphy import get_morph
import operator
#import itertools
import math


def get_words(in_file_name, index):
    print "Getting words from " + in_file_name + "..."
    f = open(in_file_name, 'r')
    file_text = f.read()
    f.close()

    words = []
    index.clear()
    pattern = re.compile("(([\w]+[-'])*[\w']+'?)", re.U)

    file_text = unicode(file_text, 'utf8').upper()
    file_text = file_text.replace('--', ' -- ')
    tokens = file_text.split()
    previous_percentage = -1
    for idx, token in enumerate(tokens):
        m = pattern.match(token)
        if m:
            word = m.group()
            words.append(word)
            if word in index:
                index[word] += 1
            else:
                index[word] = 1
        percentage = 100 * idx / len(tokens)
        if percentage != previous_percentage and percentage % 5 == 0:
            print "Getting words: " + str(percentage) + "% done"
            previous_percentage = percentage

    return words


# def get_words_nva(words):
#
#     print "Getting N, V, A from words..."
#     words_nva = []
#     morph = get_morph('')
#     previous_percentage = -1
#     for idx, word in enumerate(words):
#         info = morph.get_graminfo(word)
#         if len(info) < 1:
#             continue
#         if info[0]['class'] == u"С" or info[0]['class'] == u"П" or info[0]['class'] == u"Г":
#             #words.append(next(iter(morph.normalize(word))))
#             words_nva.append(word)
#         percentage = 100 * idx / len(words)
#         if percentage != previous_percentage and percentage % 5 == 0:
#             print "Getting N, V, A: " + str(percentage) + "% done"
#             previous_percentage = percentage
#     return words_nva


# def get_bigrams(words):
#     bigrams = []
#     for i in range(len(words) - 1):
#         t = words[i], words[i+1]
#         bigrams.append(t)
#     return bigrams


# def bigrams_frequency(text_words, out_file_name):
#
#     print "Calculating bigrams by frequency..."
#     words = get_words_nva(text_words)
#
#     bigrams = get_bigrams(words)
#     bigrams_index = dict()
#     for bigram in bigrams:
#         if bigram in bigrams_index:
#             bigrams_index[bigram] += 1
#         else:
#             bigrams_index[bigram] = 1
#
#     sorted_bigrams = reversed(sorted(bigrams_index.iteritems(), key=operator.itemgetter(1)))
#
#     f = open(out_file_name, 'w')
#     for bigram in sorted_bigrams:
#         f.write(bigram[0][0].encode("utf-8") + " " + bigram[0][1].encode("utf-8") + " " + str(bigram[1]))
#         f.write("\n")
#     f.close()
#     return sorted_bigrams


class Bigram:
    def __init__(self):
        self.bigram = None


def bigrams_mean(text_words, out_file_name, window_size):
    print "Calculating bigrams by mean..."
    bigrams_index = dict()
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

    sorted_bigrams = list(reversed(sorted(bigrams_index.values(), key=operator.attrgetter('n'))))

    f = open(out_file_name, 'w')
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

    return sorted_bigrams


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

        # O22 = sum(bg.bigram[0] != b0 and bg.bigram[1] != b1 for bg in sorted_bigrams)
        # O12 = sum(bg.bigram[0] != b0 and bg.bigram[1] == b1 for bg in sorted_bigrams)
        # O21 = sum(bg.bigram[0] == b0 and bg.bigram[1] != b1 for bg in sorted_bigrams)

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
    if args_count < 3:
        print "First command line argument must be input file name"
        print "Second command line argument must be output file name"
        return 0

    in_file_name = sys.argv[1]
    print "Input file name: " + in_file_name

    index = dict()
    text_words = get_words(in_file_name, index)
    f = open("words", 'w')
    for word in text_words:
        f.write(word.encode("utf-8")+"\n")
    f.close()

    window_size = 5

    #sorted_bigrams_simple = bigrams_frequency(text_words, "bigrams_freq")
    sorted_bigrams = bigrams_mean(text_words, "bigrams_mean", window_size)

    t_collocations = t(sorted_bigrams, index, "collocations_t")
    hi2_collocations = hi2(sorted_bigrams, index, "collocations_hi2")

main()
