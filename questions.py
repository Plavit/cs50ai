import math
import os

import nltk
import sys

nltk.download('stopwords')

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
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    # init result
    result = {}

    # Get files like in project 5
    for file_name in os.listdir(directory):
        # assign key (name excl. filetype) with contents to dictionary
        result[file_name[:-4]] = open(os.path.join(directory, file_name), mode="r", encoding="utf8").read()

    # print(result)
    return result


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    # Tokenize as in project 6a
    tokens = [word.lower() for word in nltk.word_tokenize(document)]  # if word.lower().islower()]

    # Define punctuation and stopwords
    punctuation = [',', '.', '"', ';', '(', ')', ':', '``', '`', "''", "'", '=', '%']
    stopwords = nltk.corpus.stopwords.words("english")

    # Remove punctuation and stopwords through list comprehension
    tokens = [tok for tok in tokens if (tok not in stopwords and tok not in punctuation)]

    # print("Cleaned: ", tokens)

    return tokens


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    # init dicts
    freq_dict = {}
    result = {}

    # for each unique word in each document
    for doc in documents:
        # For each word
        for word in set(documents[doc]):
            # Add frequency 1 for new words, add one for known words
            if word not in freq_dict.keys():
                freq_dict[word] = 1
            else:
                freq_dict[word] += 1

    for word in freq_dict:
        result[word] = 1 + (math.log(len(documents) / freq_dict[word]))  # 1 as lucky num for smoothing

    return result


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    # init result
    result = {}

    # For each file
    for file in files:
        result[file] = 0
        # For each word in file
        for word in query:
            # If the word is contained in file, add frequency in file
            if word in files[file]:
                freq = files[file].count(word)
            # Else, set frequency to 1 to smooth
            else:
                freq = 1
            # Norm frequencies
            norm = freq / len(files[file])
            # Assign smooth idf
            if word not in idfs.keys():
                idf = 1
            else:
                idf = idfs[word]
            # Calculate tf-idf
            result[file] = idf * norm

    # Return a sorted list of n top results found by slicing
    return sorted(result, key=result.get, reverse=True)[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # init result
    result = {}

    # For each sentence
    for sentence in sentences:
        result[sentence] = {}
        result[sentence]['idf'] = 0
        result[sentence]['wc'] = 0
        # And each word within
        for word in query:
            # If word is in sentence, add to wordcount and idf
            if word in sentences[sentence]:
                result[sentence]['idf'] += idfs[word]
                result[sentence]['wc'] += 1
        # Add normed term density
        result[sentence]['dens'] = float(result[sentence]['wc'] / len(sentences[sentence]))

    # Return a sorted list of n top results found by slicing
    return sorted(result.keys(),
                  key=lambda s: (result[s]['idf'], result[s]['dens']),
                  reverse=True)[:n]


if __name__ == "__main__":
    main()
