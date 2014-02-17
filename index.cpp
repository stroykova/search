#include <iostream>
#include <fstream>
#include <string.h>
#include <vector>
#include <set>
#include <locale.h>
#include <sstream>
#include <algorithm>
#include <map>

std::vector<std::string>* get_paragraphs(std::ifstream &file, const std::string &delimeter);
std::vector<std::string>* get_tokens_by_delimeter(std::string &text, const std::string &delimeter);
std::vector<std::string>* get_tokens_by_delimeters(const std::string &text, const char *delimeters);

int read_paragraphs_from_file(char *filename, std::vector<std::string> **paragraphs);

int write_index_to_file(const char *out_filename, std::map<std::string, std::pair<int, std::vector<int> > > &index);

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
    
    int result = read_paragraphs_from_file(argv[in_arg_index], &paragraphs);
    if (result){
        std::cout << "Error occured" << std::endl;
        return 0;
    }
    
    const char *delimeters = " \t\n\r,.:;[]()!?\"'<>=&%$-/\\";
    
    //statistics
    std::vector<std::string> all_words;
    std::set<std::string> all_words_unique;
    
    std::vector<std::pair<std::string, size_t> > term_to_doc_index;
    
    //TODO solve encoding problems
    setlocale(LC_ALL,"ru_RU.koi8r");
    size_t paragraphs_size = paragraphs->size();
    
    for (size_t i = 0; i < paragraphs_size; ++i){
        std::vector<std::string> *words = get_tokens_by_delimeters((*paragraphs)[i], delimeters);
        all_words.insert(all_words.end(), words->begin(), words->end());
        
        size_t words_size = words->size();    
        for( size_t j = 0; j < words_size; ++j) 
            all_words_unique.insert( (*words)[j] );
        
        for (size_t j = 0; j < words_size; ++j){
            //TODO call function to transform word to normalized state
            for (size_t k = 0; k < (*words)[j].length(); ++k)
                (*words)[j][k] = std::tolower((*words)[j][k]);
               
            term_to_doc_index.push_back(std::pair<std::string, size_t>((*words)[j], i));
        }
        
        delete words;
    }
    
    delete paragraphs;
    
    std::sort(term_to_doc_index.begin(), term_to_doc_index.end());
    
    size_t total_words_count = all_words.size();
    size_t total_words_unique_count = all_words_unique.size();
    std::cout << "Total words count (with repetitions): " << total_words_count << " words" << std::endl;
    
    size_t average_length = 0;
    for (size_t i = 0; i < total_words_count; ++i){
        average_length += all_words[i].length();
    }
    std::cout << "Average word length (with repetitions): " << (double)average_length / total_words_count << " characters" << std::endl;
    
    std::cout << "Total words count (with no repetitions): " << total_words_unique_count << " words" << std::endl;
    
    average_length = 0;
    std::set<std::string>::iterator it;
    for (it = all_words_unique.begin(); it != all_words_unique.end(); ++it){
        average_length += (*it).length(); // Note the "*" here
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
        average_length += (*it_index).first.length();
    }
    std::cout << "Average transformed word length (with no repetitions): " << (double)average_length / transformed_words_unique_count << " characters" << std::endl;
        
    result = write_index_to_file(argv[out_arg_index], index);
    if (result)
        std::cout << "Error occured" << std::endl;
    
      
    return 0;
}

int read_paragraphs_from_file(char *filename, std::vector<std::string> **paragraphs){
    std::ifstream file(filename);
    if (!file) {
        std::cout << "Error occured while opening file: " << filename << std::endl;
        return -1;
    }
    const std::string delimeter = "<dd>";
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
    
    std::string text(binaryData);
    delete[] binaryData;    
    return get_tokens_by_delimeter(text, delimeter);
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

std::vector<std::string>* get_tokens_by_delimeters(const std::string &text, const char *delimeters){
    std::vector<std::string> *tokens = new std::vector<std::string>();
    char const* p = text.c_str();
    char const* q = strpbrk(p, delimeters);
    
    for( ; q != NULL; q = strpbrk(p, delimeters) ){
       std::string word(p,q);
       if (!word.empty())
           tokens->push_back(word);
       p = q + 1;
    }
    return tokens;
}