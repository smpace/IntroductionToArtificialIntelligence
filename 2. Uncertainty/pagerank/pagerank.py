import os
import random
import re
import sys
import copy

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
    prob_dist = {}
    num_links = len(corpus[page])

    # Check for num of links in page
    if num_links:
        # Apply damping factor across all pages in corpus
        for pg in corpus:
            prob_dist[pg] = (1 - damping_factor) / len(corpus)
        # Add normal probability distribution over all linked pages
        for link in corpus[page]:
            prob_dist[link] += damping_factor / num_links
    else:
        # Condition: no linked pages. Default to apply normal dist over all pages.
        for pg in corpus:
            prob_dist[pg] = (1 / len(corpus))

    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize dict with all pages with count 0
    pr_sample = dict([(page, 0) for page in corpus])
    sample_page = None

    # Iterate over n samples and increment page each time it is selected
    for i in range(n):
        if sample_page:
            transition_dist = transition_model(corpus, sample_page, damping_factor)
            sample_page = random.choices(list(transition_dist.keys()), weights=list(transition_dist.values()), k=1)[0]
        else:
            sample_page = random.choice(list(pr_sample.keys()))
        # Record sample selection for each time it is chosen
        pr_sample[sample_page] += 1

    # Apply overall percentage by dividing each page count by n
    for page in pr_sample:
        pr_sample[page] /= n
    
    return pr_sample


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize a dict with {"page": 1/n} for all pages in corpus
    new_dist = dict([(page, 1 / len(corpus)) for page in corpus])
    finished = False

    while not finished:
        # Make copy before changing
        prev_dist = copy.deepcopy(new_dist)
        for page in corpus:
            # Run the iterative algorithm on each page
            new_dist[page] = iter_algorithm(damping_factor, len(corpus), page, corpus, new_dist)
        # If any page has a difference over .001 from the previous run, the while loop will continue
        for pg in new_dist:
            finished = True
            if abs(prev_dist[pg] - new_dist[pg]) > 0.001:
                finished = False
                break

    return new_dist


def iter_algorithm(d, n, p, corpus, pr):
    """
    PR(p) = ( (1-d) / n ) + ( d * sum( PR(i) / NumLinks(i) ) )
                                   i
    d = dampening number; n = # of possible pages; p = page; i = incoming pages                                  
    """
    page_sum = 0
    # This for loop will calculate the sum portion of the equation
    for i in corpus:
        # Find all incoming pages. p = pg and i = i
        if p in corpus[i]:
            # Update the sum to include each instance for the probablity of page i divided by NumLinks on page i
            page_sum += pr[i] / len(corpus[i])

    # Insert sum into rest of iterative algorithm
    return ((1 - d) / n) + (d * page_sum)


if __name__ == "__main__":
    main()
