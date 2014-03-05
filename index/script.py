# -*- coding: utf-8 -*-

import sys
import re


def average_len_tuple(lst, ind):
    lengths = [len(i[ind]) for i in lst]
    return 0 if len(lengths) == 0 else (float(sum(lengths)) / len(lengths)) 


def average_len(lst):
    lengths = [len(i) for i in lst]
    return 0 if len(lengths) == 0 else (float(sum(lengths)) / len(lengths))


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
    
    #--------------------------------------------------------------------------------------------
    
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
            index[word][1].append(par)
            index[word] = (index[word][0] + 1, index[word][1])            
        else:
            l = list()
            l.append(par)
            t = 1, l
            index[word] = t
    
    length = float(0)
    
    for k, v in index.items():
        length += len(k)
    length /= len(index)
        
    print "Writing index to file..."    
    
    f = open(out_file_name, 'w')
    for k, v in index.items():
        f.write(k.encode("utf8") + "  " + str(v[0]) + "\n")
        for par in v[1]:
            f.write(str(par) + "  ")
        f.write("\n")

    f.close()
        
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

        query = query_with_synonyms

        if syns:
            for syn in syns:
                query.append("OR")
                query.append(syn)
             
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
           
            start = len(paragraphs[par])
            end = 0
            
            for part in query:
                found = found_paragraph.find(part)
           
                while found != -1:
                    
                    if start > found:
                        start = found
                    if end < found:
                        end = found + len(part)
                    found = found_paragraph.find(part, end)
           
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
