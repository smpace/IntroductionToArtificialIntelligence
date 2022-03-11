import nltk
from nltk.tokenize import word_tokenize
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n= SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = dict()
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename)) as f:
            if filename[-4:] == ".txt":
                content = str(f.read())
                files[filename] = content
    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    p = string.punctuation
    s = nltk.corpus.stopwords.words("english")
    # Return list of tokens not found in punctuation or stopword
    return [t for t in word_tokenize(document.lower()) if t not in p and t not in s]


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # Slightly modified from lecture 6 code: tfidf.py
    # Create set of all words found in all documents
    words = set()
    for document in documents:
        words.update(documents[document])
    
    idfs = dict()
    for word in words:
        # Find number of docs that each word appears in
        f = sum(word in documents[document] for document in documents)
        # idf formula: log( total documents / # of docs containing word )
        idf = math.log(len(documents) / f)
        idfs[word] = idf
    
    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # Also slightly modified from tfidf.py
    tfidfs = dict()
    ranked = list()
    # Loop through filenames from files
    for filename in list(files.keys()):
        tfidfs[filename] = []
        total = 0
        # Count word occurances in file and multiply by idfs value
        for word in query:
            tf = files[filename].count(word)
            tfidfs[filename].append((word, tf * idfs[word]))
        # Add up the IDFS values for the query words in each file
        for t in list(tfidfs[filename]):
            total += t[1]
        # Each file gets the sum of all the query words IDFS values
        ranked.append((filename, total))

    # Sort the files from highest to lowest based on query word IDFS values
    # Only return the top "n" files
    return [f[0] for f in sorted(ranked, key=lambda x: x[1], reverse=True)][:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    rankings = dict()
    best_sentences = list()
    for sentence in sentences:
        # Initialize an [IDF, QTD] score for each sentence
        rankings[sentence] = [0, 0]
        word_freq = 0
        for word in query:
            if word in sentences[sentence]:
                # Sum together the IDF values of each query word found in sentence
                rankings[sentence][0] += idfs[word]
        # Iterate over sentence and count times query word appears
        for word in sentences[sentence]:
            if word in query:
                word_freq += 1
        # QTD formula is: word frequency / # of words in sentence
        rankings[sentence][1] += word_freq / len(sentences[sentence])
    # Sort rankings on IDF (x[1][0]) then QTD (x[1][1])
    rankings = {
        s: r for s, r in sorted(rankings.items(),
                                key=lambda x: (x[1][0], x[1][1]),
                                reverse=True)
        }
    # Create a list with the ordered sentences
    best_sentences.append(list(rankings.keys())[0])

    # Return the "n" number of matching sentences
    return best_sentences[:n]


if __name__ == "__main__":
    main()
