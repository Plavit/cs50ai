import nltk
import sys

# Had to download model package
# nltk.download('punkt')


TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> N V | NP VP | VP NP | S NP | S P NP | S P S | S Conj S | 
AA -> Adj | Adv | Adj AA | Adv AA
VP -> V | V P | V AA | Adv V
NP -> N | P NP | Det N | Det N AA | Det AA N | AA N 
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():
    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # print("input: ", sentence)
    tokens = [word.lower() for word in nltk.word_tokenize(sentence) if word.lower().islower()]
    # print("tokens: ", tokens)

    return tokens


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # Init result
    result = []
    # print("tree",tree)
    for sub in tree.subtrees():

        # A noun phrase chunk is defined as any subtree of the sentence
        #     whose label is "NP" that does not itself contain any other
        #     noun phrases as subtrees.
        # print("sub: ", sub, " label: ", sub.label)
        if sub.label() is 'NP':
            result.append(sub)

    # Return a list of all noun phrase chunks in the sentence tree.
    return result


if __name__ == "__main__":
    main()
