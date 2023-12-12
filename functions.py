import os
import string
from clean_functions import clean_lower_case, clean_punctuation
from math import *

lnames = {"Chirac": "Jacques", "Giscard dEstaing": "Valéry", "Hollande": "François", "Macron": "Emmanuel",
          "Mitterand": "François", "Sarkozy": "Nicolas"}

def list_of_files(directory, extension):
    files_names = []
    for filename in os.listdir(directory):
        if filename.endswith(extension):
                files_names.append(filename)
    return files_names

def names_extract_titles(file):
    file = file[11:][:-4] # Remove the first 11 characters and the last 4 characters from the file name

    if 48 <= ord(file[-1]) <= 57: # Check if the last character of the file name is a digit
        file = file[:-1] # If true, remove the last character from the file name

    return file


def presidents_first_name(lname):
    for k, v in lnames.items():
        if k == lname: # Check if the current key (last name) matches the provided last name
            return v + " " + k # If there's a match, concatenate the corresponding value (first name) and the last name
    
    return None # If no match is found, return None


def display_names_list():
    '''Return in a list all the names of the Presidents'''
    L = []
    global lnames
    for k, v in lnames.items():
        L.append(v + " " + k)
    return L

#TF (Term Frequency)
def tf(input_str):
    word_list = input_str.split(' ')
    
    word_freq_dict = {}
    
    for word in word_list:
        if word in word_freq_dict: # Check if the word is already in the dictionary
            word_freq_dict[word] += 1 # If yes, increment its frequency
        else:
            word_freq_dict[word] = 1 # If no, add the word to the dictionary with a frequency of 1
    
    return word_freq_dict


def idf(directory):
    doc_freq = {}
    
    files_names = list_of_files(directory, "txt")
    
    for i in files_names:
        with open(directory + i, "r") as f: # Open the cleaned file for reading
            unique_words = []
            
            content = f.readlines() # Read the content of the file line by line
            
            for line in content:
                line_tf = tf(line[:-1]) # Calculate the term frequency for each line
                
                # Add unique words to the list
                for word in line_tf.keys():
                    if word not in unique_words:
                        unique_words.append(word)
            
            # Update document frequency for each unique word
            for unique_word in set(unique_words):
                if unique_word not in doc_freq.keys():
                    doc_freq[unique_word] = 1
                else:
                    doc_freq[unique_word] += 1
    
    # Calculate the inverse document frequency for each word
    for word, freq in doc_freq.items():
        doc_freq[word] = log10(len(files_names) / freq)
    
    return doc_freq


def transpose_matrix(matrix):
    '''Take a matrix and invert the columns with rows'''
    nbRow = len(matrix)
    nbCol = len(matrix[0])
    transposed_matrix = []
    for j in range(nbCol):
        M = []
        for i in range(nbRow):
            M.append(matrix[i][j])
        transposed_matrix.append(M)
    return transposed_matrix


def tf_idf(directory):
    tf_idf_matrix = []

    didf = idf(directory)

    files_names = list_of_files(directory, "txt")

    for i in files_names:
        fl = ""

        with open(directory + i, "r") as f: # Open the cleaned file for reading
            tf_idf_doc = []

            ls = f.readlines() # Read the content of the file line by line

            for l in ls: # Concatenate lines into a single string
                fl += l[:-1] + " "

            dtf = tf(fl) # Calculate the term frequency for the document

            # Calculate the TF-IDF score for each word in the document
            for k, v in didf.items():
                if k not in dtf.keys():
                    dtf[k] = 0
                tf_idf_doc.append(dtf[k] * didf[k])

            tf_idf_matrix.append(tf_idf_doc) # Append the TF-IDF vector to the matrix

    return transpose_matrix(tf_idf_matrix) # Transpose the TF-IDF matrix


def tf_idf_dico(matrix_tfidf, directory):
    tf_idf_dico = {"files": list_of_files(directory, "txt")} # Initialize the TF-IDF dictionary

    i = 0
    
    for k in idf(directory).keys(): # For each word in the IDF dictionary
        tf_idf_dico[k] = matrix_tfidf[i] # Add the word and its corresponding TF-IDF vector to the dictionary
        i += 1

    del tf_idf_dico['']
    return tf_idf_dico

def question_tf_idf(s, dicoform=False):
    tfidfd = tf_idf_dico(tf_idf("./cleaned/"), "./cleaned/")
    tf_idf_v = []
    tf_idf_d = {}
    s = clean_punctuation(clean_lower_case(s))
    tfd = tf(s)
    idfd = idf("./cleaned/")
    q = []
    for j in tfd.keys():
        q.append(j)
    for k in tfidfd.keys():
        if k not in q:
            tfd[k] = 0
    for k, v in idfd.items():
        tf_idf_v.append(v*tfd[k])
        tf_idf_d[k] = v*tfd[k]
    if dicoform:
        return tf_idf_d
    return tf_idf_v

def norm(a):
    s = 0
    for i in a:
        s += i**2
    return sqrt(s)

def cosine_similiraty(a, b):
    scalar_p = 0
    for i in range(len(a)):
            scalar_p += a[i]*b[i]
    return (scalar_p / norm(a)*norm(b))

def most_significant_document(tfidf_question, tfidf_matrix):
    lf = list_of_files("./cleaned", "txt")
    tfidf_matrix = transpose_matrix(tfidf_matrix)
    k = 0
    maxk = 0
    max = 0
    for i in tfidf_matrix:
        cverif = cosine_similiraty(tfidf_question, i)
        if max <= cverif:
            max = cverif
            maxk = k
        k += 1
    return lf[maxk]

def most_important_question_term(s):
    tfidf_question = question_tf_idf(s, True)
    maxk = ""
    maxv = 0.0
    for k, v in tfidf_question.items():
        if maxv < v:
            maxv = v
            maxk = k
    return maxk

def auto_response(most_imp_term, most_sin_doc):
    with open("./speeches/" + most_sin_doc, "r", encoding="utf-8") as f:
        content = f.readlines()
        L = []
        for l in content:
            content = l[:-1] + " "
            L.append(content)
        for i in L:
            if most_imp_term in i:
                return i