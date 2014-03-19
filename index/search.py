# -*- coding: utf-8 -*-

import sys
import re


def read_compressed_index_from_file_fibonacci(out_file_name):
    print "Reading compressed index with fibonacci..."
    from kbp.univ import fibonacci
    import struct
    index = dict()

    file_name = out_file_name + "_fibonacci"
    f = open(file_name, 'rb')

    word_len_bytes = f.read(4)
    idx1 = 0
    while word_len_bytes:
        word_len = struct.unpack('I', word_len_bytes)[0]
        word = f.read(word_len).decode("utf8")
        freq_bytes = f.read(4)

        freq = struct.unpack('I', freq_bytes)[0]
        arr_len_bytes = f.read(4)
        arr_len = struct.unpack('I', arr_len_bytes)[0]
        arr = ""
        for i in range(0, arr_len):
            string = f.read(4)

            number = struct.unpack('I', string)[0]

            formated = "{0:b}".format(number)
            if len(formated) % 32 != 0:
                zeroes = 32 - len(formated) % 32
                for i in range(zeroes):
                    formated = "0" + formated
            arr += formated
        array = list()
        idx = 0
        while len(arr) > 0 and "11" in arr:
            var = fibonacci.decode(arr) - 1
            idx += 1

            array.append(var)
            arr = arr[arr.index("11") + 2:]

        index[word] = freq, array
        word_len_bytes = f.read(4)
        idx1 += 1

    f.close()
    return index


def read_compressed_index_from_file_elias_gamma(out_file_name):
    print "Reading compressed index with elias gamma..."
    from kbp.univ import elias
    import struct
    index = dict()

    file_name = out_file_name + "_elias_gamma"
    f = open(file_name, 'rb')

    word_len_bytes = f.read(4)
    idx1 = 0
    while word_len_bytes:
        word_len = struct.unpack('I', word_len_bytes)[0]
        word = f.read(word_len).decode("utf8")
        freq_bytes = f.read(4)

        freq = struct.unpack('I', freq_bytes)[0]
        arr_len_bytes = f.read(4)
        arr_len = struct.unpack('I', arr_len_bytes)[0]
        arr = ""
        for i in range(0, arr_len):
            string = f.read(4)

            number = struct.unpack('I', string)[0]

            formated = "{0:b}".format(number)
            if len(formated) % 32 != 0:
                zeroes = 32 - len(formated) % 32
                for i in range(zeroes):
                    formated = "0" + formated
            arr += formated
        array = list()
        idx = 0
        while len(arr) > 0 and "1" in arr:
            var = elias.gamma_decode(arr)
            idx += 1

            array.append(var[0] - 1)
            arr = arr[var[1]:]

        index[word] = freq, array
        word_len_bytes = f.read(4)
        idx1 += 1

    f.close()
    return index


def is_operation(value):
    return value == "AND" or value == "OR" or value == "NOT"


def get_priority(operation):
    if operation == "AND" or operation == "OR":
        return 1
    if operation == "NOT":
        return 2
    if operation == '(':
        return 0
    return -1


def not_operation(operand, super_set_count):
    result = list()

    set_index = 0
    for value in operand:
        for set_index in range(set_index, super_set_count - 1):
            result.append(set_index)
        set_index = value + 1

    for set_index in range(set_index, super_set_count - 1):
        result.append(set_index)

    return result


def or_operation(operand1, operand2):
    result = list()

    index1 = 0
    index2 = 0

    size1 = len(operand1)
    size2 = len(operand2)

    while index1 < size1 and index2 < size2:
        if operand1[index1] == operand2[index2]:
            result.append(operand1[index1])
            index1 += 1
            index2 += 1
        elif operand1[index1] < operand2[index2]:
            result.append(operand1[index1])
            index1 += 1
        else:
            result.append(operand2[index2])
            index2 += 1

    while index1 < size1:
        result.append(operand1[index1])
        index1 += 1

    while index2 < size2:
        result.append(operand2[index2])
        index2 += 1

    return result


def and_operation(operand1, operand2):
    result = list()

    index1 = 0
    index2 = 0

    size1 = len(operand1)
    size2 = len(operand2)

    while index1 < size1 and index2 < size2:
        if operand1[index1] == operand2[index2]:
            result.append(operand1[index1])
            index1 += 1
            index2 += 1
        elif operand1[index1] < operand2[index2]:
            index1 += 1
        else:
            index2 += 1

    return result


def convert_to_postfix(query):
    stack = list()
    result = list()

    for part in query:
        if part == '(':
            stack.append(part)
        elif part == ')':
            if not stack:
                return list()

            top = stack.pop()
            while top != '(':
                result.append(top)
                if not stack:
                    return list()
                top = stack.pop()
        elif is_operation(part):
            new_operation_priority = get_priority(part)
            while stack and get_priority(stack[-1]) >= new_operation_priority:
                top = stack.pop()
                result.append(top)
            stack.append(part)
        else:
            result.append(part)

    while stack:
        top = stack.pop()
        result.append(top)
    return result


def get_query_result(query, index, paragraphs_count):
    stack = list()

    for part in query:
        if is_operation(part):
            if not stack:
                return list()

            if part == "NOT":
                operand1 = stack.pop()
                stack.append(not_operation(operand1, paragraphs_count))
            elif part == "AND":
                if len(stack) < 2:
                    return list()

                operand1 = stack.pop()
                operand2 = stack.pop()

                if len(operand1) < len(operand2):
                    stack.append(and_operation(operand1, operand2))
                else:
                    stack.append(and_operation(operand2, operand1))

            elif part == "OR":
                if len(stack) < 2:
                    return list()

                operand1 = stack.pop()
                operand2 = stack.pop()

                if len(operand1) < len(operand2):
                    stack.append(or_operation(operand1, operand2))
                else:
                    stack.append(or_operation(operand2, operand1))
        else:
            if part in index:
                stack.append(list(index[part][1]))
            else:
                operand_result = list()
                stack.append(operand_result)

    if len(stack) != 1:
        return list()

    return stack.pop()


def main():

    args_count = len(sys.argv)

    if args_count < 4:
        print "First command line argument must be input file name"
        print "Second command line argument must be output file name"
        print "Third command line argument must be synonyms file name"
        return 0

    in_file_name = sys.argv[1]
    out_file_name = sys.argv[2]
    syn_file_name = sys.argv[3]

    print "Input file name: " + in_file_name
    print "Output file name: " + out_file_name

    f = open(in_file_name, 'r')
    file_text = f.read()
    f.close()

    delimiter = "<dd>"
    paragraphs = file_text.split(delimiter)

    import Stemmer
    stemmer = Stemmer.Stemmer('russian')

    print "Reading index..."

    index = read_compressed_index_from_file_elias_gamma(out_file_name)
    index = read_compressed_index_from_file_fibonacci(out_file_name)

    #prepare for work
    for k, v in index.items():
        prev1 = v[1][0]
        for idx in range(1, len(v[1])):
            v[1][idx] += prev1
            prev2 = v[1][idx]
            prev1 = prev2

    pattern = re.compile("(([\w]+[-'])*[\w']+'?)", re.U)

    print "Reading synonyms..."

    synonyms = dict()
    f = open(syn_file_name, 'r')
    file_text = f.read().decode("utf8")
    f.close()
    lines = file_text.split('\n')
    for line in lines:
        parts = line.split('|')
        if len(parts) < 2:
            continue

        key = stemmer.stemWord(parts[0])
        syns = set()
        tokens = parts[1].split(',')
        for token in tokens:
            if pattern.match(token):
                syns.add(stemmer.stemWord(token.lower()))

        if not syns:
            continue

        if key in synonyms:
            synonyms[key] |= syns
        else:
            synonyms[key] = syns

    while 1:
        query = raw_input("Input your query or press enter to quit: ").decode("utf8")
        if not query:
            print "Bye!"
            return

        default_count = 10
        count = default_count

        count_str = raw_input("Input result count or press enter to default (" + str(count) + "): ")
        if count_str:
            try:
                count = int(count_str)
            except ValueError:
                count = default_count
            if count == 0:
                count = default_count

        bracket = '('
        pos = 0
        pos = query.find(bracket, pos)
        while pos >= 0:
            query = query[:pos] + ' ' + query[pos:]
            pos += 2
            query = query[:pos] + ' ' + query[pos:]
            pos = query.find(bracket, pos)

        bracket = ')'
        pos = 0
        pos = query.find(bracket, pos)
        while pos >= 0:
            query = query[:pos] + ' ' + query[pos:]
            pos += 2
            query = query[:pos] + ' ' + query[pos:]
            pos = query.find(bracket, pos)

        query = query.split()

        query_with_synonyms = []

        for i, val in enumerate(query):
            if not is_operation(val) and val != '(' and val != ')':
                query[i] = stemmer.stemWord(val.lower())
                if query[i] in synonyms:
                    query_with_synonyms.append("(")
                    query_with_synonyms.append(query[i])

                    syns = synonyms[query[i]]
                    for syn in syns:
                        query_with_synonyms.append("OR")
                        query_with_synonyms.append(syn)

                    query_with_synonyms.append(")")
                else:
                    query_with_synonyms.append(query[i])
            else:
                query_with_synonyms.append(query[i])

        query = query_with_synonyms

        query = convert_to_postfix(query)
        if not query:
            print "Check your query please"
            continue

        result = get_query_result(query, index, len(paragraphs))

        print ""
        print "Found " + str(len(result)) + " paragraphs"

        cnt = 0
        for par in result:
            cnt += 1

            if cnt > count:
                break
            print ""
            print str(par)

            found_paragraph = paragraphs[par].decode("utf8").lower()

            start = len(found_paragraph)
            end = 0

            for part in query:
                start_snippet = found_paragraph.find(part)
                end_snippet = found_paragraph.rfind(part)
                if start_snippet < start:
                    start = start_snippet
                if end_snippet > end:
                    end = end_snippet + len(part)

            if end - start < 25:
                end += 25
                start -= 25
            if end < 0 or end >= len(found_paragraph):
                end = len(paragraphs[par]) - 1
            if start < 0 or start >= len(found_paragraph):
                start = 0

            snippet = found_paragraph[start:end]
            print snippet


main()
