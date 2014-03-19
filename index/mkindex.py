# -*- coding: utf-8 -*-

import sys
import re


def average_len_tuple(lst, ind):
    lengths = [len(i[ind]) for i in lst]
    return 0 if len(lengths) == 0 else (float(sum(lengths)) / len(lengths))


def average_len(lst):
    lengths = [len(i) for i in lst]
    return 0 if len(lengths) == 0 else (float(sum(lengths)) / len(lengths))


def compressed_index_to_file_elias_gamma(index, out_file_name):

    print "Compressing with elias gamma..."
    from kbp.univ import elias
    import struct
    file_name = out_file_name + "_elias_gamma"
    f = open(file_name, 'wb')
    for k, v in index.items():
        word_len = len(k.encode("utf-8"))
        f.write(struct.pack('I', word_len))
        f.write(k.encode("utf-8"))
        f.write(struct.pack('I', v[0]))

        entries = ""
        for i in v[1]:
            entries += elias.gamma_encode(i + 1)
        if len(entries) % 32 != 0:
            zeroes = 32 - len(entries) % 32
            for i in range(zeroes):
                entries += "0"

        numbers = []
        count = len(entries) / 32

        for idx in range(0, count):
            numbers.append(int(entries[idx * 32: (idx + 1) * 32], 2))

        f.write(struct.pack('I', count))
        for number in numbers:
            f.write(struct.pack('I', number))
    f.close()
    return


def compressed_index_to_file_fibonacci(index, out_file_name):

    print "Compressing with fibonacci..."
    from kbp.univ import fibonacci
    import struct
    file_name = out_file_name + "_fibonacci"
    f = open(file_name, 'wb')
    for k, v in index.items():
        word_len = len(k.encode("utf-8"))
        f.write(struct.pack('I', word_len))
        f.write(k.encode("utf-8"))
        f.write(struct.pack('I', v[0]))

        entries = ""
        for i in v[1]:
            entries += fibonacci.encode(i + 1)
        if len(entries) % 32 != 0:
            zeroes = 32 - len(entries) % 32
            for i in range(zeroes):
                entries += "0"
        numbers = []
        count = len(entries) / 32

        for idx in range(0, count):
            numbers.append(int(entries[idx * 32: (idx + 1) * 32], 2))

        f.write(struct.pack('I', count))
        for number in numbers:
            f.write(struct.pack('I', number))
    f.close()
    return


def main():

    args_count = len(sys.argv)

    if args_count < 3:
        print "First command line argument must be input file name"
        print "Second command line argument must be output file name"
        return 0

    in_file_name = sys.argv[1]
    out_file_name = sys.argv[2]

    print "Input file name: " + in_file_name
    print "Output file name: " + out_file_name

    print "Getting words..."

    f = open(in_file_name, 'r')
    file_text = f.read()
    f.close()

    words = []
    words_set = set()

    delimiter = "<dd>"
    paragraphs = file_text.split(delimiter)
    pattern = re.compile("(([\w]+[-'])*[\w']+'?)", re.U)

    for idx, paragraph in enumerate(paragraphs):
        paragraph = unicode(paragraph, 'utf8')
        paragraph = paragraph.replace('--', ' -- ')
        for token in paragraph.split():
            m = pattern.match(token)
            if m:
                t = m.group(), idx
                words_set.add(t[0])
                words.append(t)

    print ""
    print "Total words count (with duplicates):"
    print len(words)
    print "Average word length (with duplicates): "
    print average_len_tuple(words, 0)
    print ""
    print "Total words count (no duplicates):"
    print len(words_set)
    print "Average word length (no duplicates):"
    print average_len(words_set)
    print ""

    print "Building index..."

    words = list(set(words))
    words.sort(key=lambda tup: (tup[0], tup[1]))

    words_before = set()

    import Stemmer

    stemmer = Stemmer.Stemmer('russian')

    index = dict()
    for word_to_paragraph in words:
        words_before.add(word_to_paragraph[0].lower())
        word = stemmer.stemWord(word_to_paragraph[0].lower())
        par = word_to_paragraph[1]
        if word in index:
            if not par in index[word][1]:
                index[word][1].append(par)
                index[word] = (index[word][0] + 1, index[word][1])
        else:
            l = list()
            l.append(par)
            t = 1, l
            index[word] = t

    length = float(0)

    for k, v in index.items():
        v[1].sort()
        length += len(k)
    length /= len(index)

    # prepare for compressing
    for k, v in index.items():
        prev1 = v[1][0]
        for idx in range(1, len(v[1])):
            prev2 = v[1][idx]
            v[1][idx] -= prev1
            prev1 = prev2

    print "Writing index to file..."

    compressed_index_to_file_elias_gamma(index, out_file_name)
    compressed_index_to_file_fibonacci(index, out_file_name)

    print "Transformed words count (lowercase, no stemming):"
    print len(words_before)
    print "Average transformed word length (lowercase, no stemming):"
    print average_len(words_before)
    print ""

    print "Transformed words count (stemming):"
    print len(index)
    print "Average transformed word length (stemming):"
    print length
    print ""


main()