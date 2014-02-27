#include <iostream>
#include <fstream>
#include <string.h>
#include <vector>
#include <set>
#include <locale>
#include <sstream>
#include <algorithm>
#include <map>
#include <stack>
#include <utility> 


#define AND "AND"
#define OR "OR"
#define NOT "NOT"
#define OPEN_BRACKET "("
#define CLOSE_BRACKET ")"

#define BINARY_PRIORITY 1
#define UNARY_PRIORITY 2
#define BRACKET_PRIORITY 0
#define BAD_PRIORITY -1

std::vector<std::string>* get_paragraphs(std::ifstream &file, const std::string &delimeter);
std::vector<std::string>* get_tokens_by_delimeter(std::string &text, const std::string &delimeter);
std::vector<std::string> get_tokens_by_delimeters(const std::string &text, const char *delimeters);

int read_paragraphs_from_file(char *filename, std::vector<std::string> **paragraphs, const std::string delimeter);
int write_index_to_file(const char *out_filename, std::map<std::string, std::pair<int, std::vector<int> > > &index);

std::vector<std::string> get_query_parts(std::string &query);
bool is_operation(std::string input);
bool convert_to_postfix(std::vector<std::string> &query_parts, std::vector<std::string> **postfix);
int get_priority(std::string operation);

bool get_query_result(
    std::vector<std::string> &query, 
    const std::map<std::string, std::pair<int, std::vector<int> > > &index, 
    const int paragraphs_count,
    std::vector<int> **query_result);

std::vector<int> and_operation(std::vector<int> &operand1, std::vector<int> &operand2);
std::vector<int> or_operation(std::vector<int> &operand1, std::vector<int> &operand2);
std::vector<int> not_operation(std::vector<int> &operand, int super_set_count);

int my_strlen_utf8_c(const char *s) {
   int i = 0, j = 0;
   while (s[i]) {
     if ((s[i] & 0xc0) != 0x80) j++;
     i++;
   }
   return j;
}

int main(int argc, char * argv[]){

    if (argc < 3){
       std::cout << "First command line argument must be input file name" << std::endl;
       std::cout << "Second command line argument must be output file name" << std::endl; 
       return 0;
    }
    
    size_t in_arg_index = 1;
    size_t out_arg_index = 2;
    
    std::cout << "Input file name: " << argv[in_arg_index] << std::endl;
    std::cout << "Output file name: " << argv[out_arg_index] << std::endl;
    
    std::vector<std::string> *paragraphs = NULL;
    const std::string delimeter = "<dd>";
    int result = read_paragraphs_from_file(argv[in_arg_index], &paragraphs, delimeter);
    if (result){
        std::cout << "Error occured" << std::endl;
        return 0;
    }
    
    const char *delimeters = " \t\n\r,.:;[]()!?\"'<>=&%$-/\\";
    
    //statistics
    std::vector<std::string> all_words;
    std::set<std::string> all_words_unique;
    
    std::vector<std::pair<std::string, size_t> > term_to_doc_index;
    
    size_t paragraphs_size = paragraphs->size();
    setlocale(LC_ALL,"ru_RU.utf8");
    for (size_t i = 0; i < paragraphs_size; ++i){
        std::vector<std::string> words = get_tokens_by_delimeters((*paragraphs)[i], delimeters);
        all_words.insert(all_words.end(), words.begin(), words.end());
        
        size_t words_size = words.size();    
        for( size_t j = 0; j < words_size; ++j) 
            all_words_unique.insert( words[j] );
        
        for (size_t j = 0; j < words_size; ++j){
            
            //TODO call function to transform word to normalized state
            for (size_t k = 0; k < words[j].length(); ++k){                
              words[j][k] = std::tolower(words[j][k]);
            }
               
            term_to_doc_index.push_back(std::pair<std::string, size_t>(words[j], i));
        }
    }
    
    
    
    std::sort(term_to_doc_index.begin(), term_to_doc_index.end());
    
    size_t total_words_count = all_words.size();
    size_t total_words_unique_count = all_words_unique.size();
    std::cout << "Total words count (with repetitions): " << total_words_count << " words" << std::endl;
    
    size_t average_length = 0;
    for (size_t i = 0; i < total_words_count; ++i){
        average_length += my_strlen_utf8_c(all_words[i].c_str());
    }
    std::cout << "Average word length (with repetitions): " << (double)average_length / total_words_count << " characters" << std::endl;
    
    std::cout << "Total words count (with no repetitions): " << total_words_unique_count << " words" << std::endl;
    
    average_length = 0;
    std::set<std::string>::iterator it;
    for (it = all_words_unique.begin(); it != all_words_unique.end(); ++it){
        average_length += my_strlen_utf8_c((*it).c_str());
    }
    std::cout << "Average word length (with no repetitions): " << (double)average_length / total_words_unique_count << " characters" << std::endl;
    
    term_to_doc_index.erase( unique( term_to_doc_index.begin(), term_to_doc_index.end() ), term_to_doc_index.end() );
    
    size_t pairs_size = term_to_doc_index.size();
    std::map<std::string, std::pair<int, std::vector<int> > > index;
    
    for (size_t i = 0; i < pairs_size; ++i){
        index[term_to_doc_index[i].first].first++;
        index[term_to_doc_index[i].first].second.push_back(term_to_doc_index[i].second);  
    }
    
    int transformed_words_unique_count = index.size();
    std::cout << "Transformed words count (with no repetitions): " << transformed_words_unique_count << std::endl;
     
    average_length = 0;
    std::map<std::string, std::pair<int, std::vector<int> > >::iterator it_index;
    for (it_index = index.begin(); it_index != index.end(); ++it_index){
        average_length += my_strlen_utf8_c((*it_index).first.c_str());
    }
    std::cout << "Average transformed word length (with no repetitions): " << (double)average_length / transformed_words_unique_count << " characters" << std::endl;
        
    result = write_index_to_file(argv[out_arg_index], index);
    if (result)
        std::cout << "Error occured" << std::endl;
    
    while(1){
    
        std::cout << "Input your query or press enter to quit: " << std::endl;
        
        std::string query;
        getline (std::cin, query);
    
        if (query.empty()){
            std::cout << "Bye!" << std::endl;
            break;
        }
          
        std::cout << query << std::endl;
        
        const size_t default_count = 10;
        size_t result_count = default_count;
        std::cout << "Input result count or press enter to default (" << result_count <<"): " << std::endl;
        
        std::string count;
        getline (std::cin, count);
    
        if (!query.empty()){
            std::stringstream(count) >> result_count;
            if (result_count == 0)
                result_count = default_count;
        }
                
        std::vector<std::string> query_parts = get_query_parts(query);
        std::vector<std::string> *query_postfix = NULL;
        if (!convert_to_postfix(query_parts, &query_postfix)){
            delete query_postfix;
            std::cout << "Syntax error, check your query please" << std::endl;
            continue;
        }
        
        std::vector<int> *query_result = NULL;
        if (!get_query_result(*query_postfix, index, paragraphs_size, &query_result)){
            delete query_result;
            std::cout << "Syntax error, check your query please" << std::endl;
            continue;
        }
        
        std::cout << query_result->size() << std::endl;
        for (size_t i = 0; i < query_result->size() && i < result_count; ++i){
            std::cout << std::endl;
            int paragraph_index = (*query_result)[i];
            std::cout << paragraph_index << std::endl;
            
            std::size_t found;
            std::size_t start = std::string::npos;
            std::size_t end = 0;
            
            for (size_t j = 0; j < query_parts.size(); ++j){
                found = (*paragraphs)[paragraph_index].find(query_parts[j]);
                 if (found != std::string::npos){
                     if (start > found)
                         start = found;
                     if (end < found)
                         end = found + query_parts[j].length();
                 }
            }
            
            if (end - start < 25){
                end += 25;
                start -= 25;
                if (end < 0 || end >= (*paragraphs)[paragraph_index].length())
                    end = (*paragraphs)[paragraph_index].length() - 1;
                if (start < 0 || start >= (*paragraphs)[paragraph_index].length())
                    start = 0;
            }
            
            std::string snippet((*paragraphs)[paragraph_index], start, end - start);
            std::cout << snippet << std::endl;
        }
            
        delete query_postfix;        
    }
    
    
    delete paragraphs;
    
    return 0;
}

std::vector<std::string> get_query_parts(std::string &query){
    
    std::string bracket = OPEN_BRACKET;
    size_t pos = 0;
    while ((pos = query.find(bracket, pos)) != std::string::npos) {
        query.insert(pos, " ");
        pos+=2;
        query.insert(pos, " ");
    }
    
    bracket = CLOSE_BRACKET;
    pos = 0;
    while ((pos = query.find(bracket, pos)) != std::string::npos) {
        query.insert(pos, " ");
        pos+=2;
        query.insert(pos, " ");
    }
    

    return get_tokens_by_delimeters(query, " ");
}

int read_paragraphs_from_file(char *filename, std::vector<std::string> **paragraphs, const std::string delimeter){
    
    std::ifstream file(filename);
    if (!file) {
        std::cout << "Error occured while opening file: " << filename << std::endl;
        return -1;
    }
    
    *paragraphs = get_paragraphs(file, delimeter);
    std::cout << "Got " << (*paragraphs)->size() << " paragraphs" << std::endl;
    file.close();
    return 0;
}

int write_index_to_file(const char *out_filename, std::map<std::string, std::pair<int, std::vector<int> > > &index){
    std::ofstream out_file(out_filename, std::ofstream::out);
    if (!out_file) {
        std::cout << "Error occured while opening file: " << out_filename << std::endl;
        return -1;
    }
    
    std::map<std::string, std::pair<int, std::vector<int> > >::iterator it;
    for (it = index.begin(); it != index.end(); ++it){
        
        //std::string ws((*it).first.size(), ' '); // Overestimate number of code points.
        //wcstombs(&ws[0], (*it).first.c_str(), (*it).first.size());
        
        out_file << (*it).first << " " << (*it).second.first << std::endl;
        for (size_t i = 0; i < (*it).second.second.size(); ++i){
            out_file << (*it).second.second[i] << " ";
        }
        out_file << std::endl;
    }
    
    out_file.close();
    return 0;
}

std::vector<std::string>* get_paragraphs(std::ifstream &file, const std::string &delimeter){
    
    if (!file)
        return new std::vector<std::string>();

    file.seekg(0, std::ios::end);
    size_t size = file.tellg();
            
    char *binaryData = new char[size + 1];
    file.seekg(0, std::ios::beg);
    file.read(binaryData, size);
    binaryData[size] = '\0';
    
    std::string s(binaryData);
    
    delete[] binaryData;    
    return get_tokens_by_delimeter(s, delimeter);
}

std::vector<std::string>* get_tokens_by_delimeter(std::string &text, const std::string &delimeter){
    std::vector<std::string> *tokens = new std::vector<std::string>();
    size_t pos = 0;
    std::string token;
    while ((pos = text.find(delimeter)) != std::string::npos) {
        token = text.substr(0, pos);
        tokens->push_back(token);
        text.erase(0, pos + delimeter.length());
    }
    tokens->push_back(text);
    return tokens;
}

std::vector<std::string> get_tokens_by_delimeters(const std::string &text, const char *delimeters){  
    std::vector<std::string> tokens;
    char const* p = text.c_str();
    char const* q = strpbrk(p, delimeters);
    
    for( ; q != NULL; q = strpbrk(p, delimeters) ){
        std::string word(p,q);
        
        if (!word.empty())
            tokens.push_back(word);
        p = q + 1;
    }
    
    std::string last_word(p,&text[text.length()]);
    if (!last_word.empty())
           tokens.push_back(last_word);
    
    return tokens;
}

bool convert_to_postfix(std::vector<std::string> &query_parts, std::vector<std::string> **postfix){
    std::vector<std::string> *result = new std::vector<std::string>();
    size_t query_parts_size = query_parts.size();
    std::stack<std::string> stack;
    for (size_t i = 0; i < query_parts_size; ++i){
        std::string part = query_parts[i];
        if(part == OPEN_BRACKET){
            stack.push(part);
        }
        else if(part == CLOSE_BRACKET){
            if (stack.empty())
                return false;
            
            std::string top = stack.top();
            stack.pop();
            while (top != OPEN_BRACKET){
                result->push_back(top);
                if (stack.empty())
                    return false;
                top = stack.top();
                stack.pop();
            }
        }
        else if(is_operation(part)){
            int new_operation_priority = get_priority(part);  
            while (!stack.empty() && get_priority(stack.top()) >= new_operation_priority){
                std::string top = stack.top();
                stack.pop();
                result->push_back(top);        
            }
            stack.push(part);
        }
        else{
            result->push_back(part);
        }
    }
    
    while(!stack.empty()){
        std::string top = stack.top();
        stack.pop();
        result->push_back(top); 
    }
    
    *postfix = result;
    return true;
}

int get_priority(std::string operation){
    if (operation == AND || operation == OR)
        return BINARY_PRIORITY;
    if (operation == NOT)
        return UNARY_PRIORITY;
    if (operation == OPEN_BRACKET)
        return BRACKET_PRIORITY;
    return BAD_PRIORITY;
}

bool is_operation(std::string input){
    return input == AND || input == OR || input == NOT;
}

bool get_query_result(
    std::vector<std::string> &query, 
    const std::map<std::string, std::pair<int, std::vector<int> > > &index, 
    const int paragraphs_count,
    std::vector<int> **query_result){
    size_t query_size = query.size();
    
    std::stack<std::vector<int> > stack;
    
    for (size_t i = 0; i < query_size; ++i){
        std::string part = query[i];
        if(is_operation(part)){
            if (stack.empty())
                return false;
            
            if (part == NOT){
                std::vector<int> operand1 = stack.top();
                stack.pop();
                
                stack.push(not_operation(operand1, paragraphs_count));
            }
            else if (part == AND){
                if (stack.size() < 2)
                    return false;
                
                std::vector<int> operand1 = stack.top();
                stack.pop();
                std::vector<int> operand2 = stack.top();
                stack.pop();
                
                if (operand1.size() < operand2.size())
                    stack.push(and_operation(operand1, operand2));
                else
                    stack.push(and_operation(operand2, operand1));
            }
            else if (part == OR){
                if (stack.size() < 2)
                    return false;
                
                std::vector<int> operand1 = stack.top();
                stack.pop();
                std::vector<int> operand2 = stack.top();
                stack.pop();
                
                if (operand1.size() < operand2.size())
                    stack.push(or_operation(operand1, operand2));
                else
                    stack.push(or_operation(operand2, operand1));
            }    
        }
        else{
            
            std::cout<< part <<std::endl;
            
            std::map<std::string, std::pair<int, std::vector<int> > >::const_iterator pos = index.find(part);
            if (pos == index.end()) {
                std::vector<int> operand_result;
                stack.push(operand_result);
            } else {              
                std::pair<int, std::vector<int> > value = pos->second;
                std::vector<int> operand_result(value.second);
                stack.push(operand_result);
            }
            
            
        }
    }
    
    if (stack.size() != 1)
        return false;
    
    std::vector<int> *result = new std::vector<int>(stack.top());
    *query_result = result;
    return true;
}


std::vector<int> and_operation(std::vector<int> &operand1, std::vector<int> &operand2){
    std::vector<int> result;
    
    size_t index1 = 0;
    size_t index2 = 0;
    
    size_t size1 = operand1.size();
    size_t size2 = operand2.size();
    
    while (index1 < size1 && index2 < size2){
        if (operand1[index1] == operand2[index2]){
            result.push_back(operand1[index1]);
            ++index1;
            ++index2;
        }
        else if (operand1[index1] < operand2[index2])
            ++index1;
        else
            ++index2;
    }
    
    return result;
}

std::vector<int> or_operation(std::vector<int> &operand1, std::vector<int> &operand2){
    std::vector<int> result;
    
    size_t index1 = 0;
    size_t index2 = 0;
    
    size_t size1 = operand1.size();
    size_t size2 = operand2.size();
    
    while (index1 < size1 && index2 < size2){
        if (operand1[index1] == operand2[index2]){
            result.push_back(operand1[index1]);
            ++index1;
            ++index2;
        }
        else if (operand1[index1] < operand2[index2]){
            result.push_back(operand1[index1]);
            ++index1;
        }
        else{
            result.push_back(operand2[index2]);
            ++index2;
        }
    }
    
    for (; index1 < size1; ++index1)
        result.push_back(operand1[index1]);
    
    for (; index2 < size2; ++index2)
        result.push_back(operand2[index2]);
    
    return result;
}

std::vector<int> not_operation(std::vector<int> &operand, int super_set_count){
    std::vector<int> result;
    
    int set_index = 0;
    size_t operand_size = operand.size();
    for (size_t i = 0; i < operand_size; ++i){
       for (; set_index < super_set_count && set_index < operand[i]; ++set_index)
           result.push_back(set_index);
       set_index = operand[i] + 1;
    }
    
    for (; set_index < super_set_count; ++set_index)
           result.push_back(set_index);
    
    return result;
}