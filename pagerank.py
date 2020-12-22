import copy
import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # Variable setup
    target = {}
    links = corpus[page]

    # Without links, each page has same probability
    if not links:
        for x in corpus:
            target[x] = 1.0 / len(corpus)
    else:
        # Otherwise, with probability `1 - damping_factor`, choose
        # a link at random chosen from all pages in the corpus.
        for x in corpus:
            target[x] = (1 - damping_factor) / len(corpus)
        # plus, add another probability per link: with probability `damping_factor`, choose a link at random
        # linked to by `page`
        for x in links:
            target[x] += damping_factor / len(links)

    # Debug - total sum
    # total=0
    # for y in corpus:
    #     total+=target[y]
    # print(total)

    # Return a probability distribution over which page to visit next
    return target


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Variable setup
    page_ranks = {}.fromkeys(corpus.keys(), 0)
    target_page = random.choices(list(corpus.keys()))[0]

    # For n pages as defined by input
    for i in range(1, n):
        # Sample transition model, starting with random target page initialized before
        current_dist = transition_model(corpus, target_page, damping_factor)
        for page in page_ranks:
            # For each page, add pagerank value
            page_ranks[page] = (((i - 1) * page_ranks[page]) + current_dist[page]) / i
        target_page = random.choices(list(page_ranks.keys()), weights=list(page_ranks.values()), k=1)[0]

    # Debug - total sum
    total = 0
    for page in page_ranks:
        total += page_ranks[page]
    print("Debug 1, total sum: ", total)

    #     Return a dictionary where keys are page names, and values are
    #     their estimated PageRank value (a value between 0 and 1). All
    #     PageRank values should sum to 1.
    return page_ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Variable setup
    total_pages = len(corpus)
    page_ranks = {}.fromkeys(corpus.keys(), 1.0 / total_pages)
    too_rough = True

    # Until reaching set precision threshold, iterate
    while too_rough:
        old_distribution = copy.deepcopy(page_ranks)

        # PageRank values for each page by iteratively updating
        # PageRank values until convergence, with same rules as previous function
        for page in corpus:

            # Determine link weight for page
            link_weight = 0
            for p in corpus:
                if page in corpus[p]:
                    link_weight += page_ranks[p] / len(corpus[p])

            # Iteratively add pagerank to pages
            page_ranks[page] = ((1 - damping_factor) / total_pages) + (damping_factor * link_weight)

            # Until estimate is precise enough
            too_rough = (abs(old_distribution[page] - page_ranks[page]) > 0.0001)

    # Debug - total sum
    total = 0
    for page in page_ranks:
        total += page_ranks[page]
    print("Debug 2, total sum: ", total)

    #     Return a dictionary where keys are page names, and values are
    #     their estimated PageRank value (a value between 0 and 1). All
    #     PageRank values should sum to 1. (should be very similar in results to previous function)
    return page_ranks


if __name__ == "__main__":
    main()
