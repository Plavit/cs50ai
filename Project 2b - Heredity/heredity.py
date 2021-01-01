import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    # Start with probabilities being wrong
    probability = 1
    prob_zero = 1
    prob_one = 1
    prob_two = 1

    # Then, calculate probabilities for every subgroup in set

    # For everyone not in `one_gene` or `two_gene` who do not have the gene
    for i in (people.keys() - (one_gene | two_genes)):
        if people[i]["mother"] is None:
            # Certain not to have 2 genes
            prob_zero = PROBS["gene"][0]
        elif people[i]["mother"] is not None:
            prob_zero = 1
            # Parents
            mother = people[i]["mother"]
            father = people[i]["father"]
            # Case if both do not have genes
            if mother in (people.keys() - (one_gene | two_genes)) and father in (
                    people.keys() - (one_gene | two_genes)):
                # They pass without gene unless mutated
                prob_zero *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"])
            # Case if mother has no gene, father has one gene
            if mother in (people.keys() - (one_gene | two_genes)) and father in one_gene:
                # Mother passes gene only if mutated and father has a 50% chance
                prob_zero *= (1 - PROBS["mutation"]) * 0.5
            # Case if mother has no gene, father has two
            if mother in (people.keys() - (one_gene | two_genes)) and father in two_genes:
                # Mother passes gene only if mutated and father passes gene only if not mutated
                prob_zero *= (1 - PROBS["mutation"]) * PROBS["mutation"]

            # Similar for cases with mother having one gene, father 0-2:
            if mother in one_gene and father in (people.keys() - (one_gene | two_genes)):
                prob_zero *= 0.5 * (1 - PROBS["mutation"])
            if mother in one_gene and father in one_gene:
                prob_zero *= 0.5 * 0.5
            if mother in one_gene and father in two_genes:
                prob_zero *= 0.5 * PROBS["mutation"]

            # Similar for cases with mother having two genes, and father 0-2:
            if mother in two_genes and father in (people.keys() - (one_gene | two_genes)):
                prob_zero *= PROBS["mutation"] * (1 - PROBS["mutation"])
            if mother in two_genes and father in one_gene:
                prob_zero *= PROBS["mutation"] * 0.5
            if mother in two_genes and father in two_genes:
                prob_zero *= PROBS["mutation"] * PROBS["mutation"]

        # Calculate final probability
        prob_zero = prob_zero * PROBS["trait"][0][(i in have_trait)]
        probability = probability * prob_zero

    # For everyone in set `one_gene` has one copy of the gene
    # Same logic as above
    for i in one_gene:
        if people[i]["mother"] is None:
            prob_one = PROBS["gene"][1]
        elif people[i]["mother"] is not None:
            prob_one = 1
            mother = people[i]["mother"]
            father = people[i]["father"]

            # Mother no genes cases
            if mother in (people.keys() - (one_gene | two_genes)) and father in (
                    people.keys() - (one_gene | two_genes)):
                prob_one *= PROBS["mutation"] * (1 - PROBS["mutation"]) + \
                            (1 - PROBS["mutation"]) * PROBS["mutation"]
            if mother in (people.keys() - (one_gene | two_genes)) and father in one_gene:
                prob_one *= PROBS["mutation"] * 0.5 + (1 - PROBS["mutation"]) * 0.5
            if mother in (people.keys() - (one_gene | two_genes)) and father in two_genes:
                prob_one *= PROBS["mutation"] * PROBS["mutation"] + \
                            (1 - PROBS["mutation"]) * (1 - PROBS["mutation"])

            # Mother one gene cases
            if mother in one_gene and father in (people.keys() - (one_gene | two_genes)):
                prob_one *= 0.5 * (1 - PROBS["mutation"]) + 0.5 * PROBS["mutation"]
            if mother in one_gene and father in one_gene:
                prob_one *= 0.5 * 0.5 + 0.5 * 0.5
            if mother in one_gene and father in two_genes:
                prob_one *= 0.5 * PROBS["mutation"] + 0.5 * (1 - PROBS["mutation"])

            # Mother two genes cases
            if mother in two_genes and father in (people.keys() - (one_gene | two_genes)):
                prob_one *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"]
                                                       ) + PROBS["mutation"] * PROBS["mutation"]
            if mother in two_genes and father in one_gene:
                prob_one *= (1 - PROBS["mutation"]) * 0.5 + PROBS["mutation"] * 0.5
            if mother in two_genes and father in two_genes:
                prob_one *= (1 - PROBS["mutation"]) * PROBS["mutation"] + \
                            PROBS["mutation"] * (1 - PROBS["mutation"])

        # Calculate final probability
        prob_one = prob_one * PROBS["trait"][1][(i in have_trait)]
        probability = probability * prob_one

    # For everyone in set `two_genes` has two copies of the gene
    # Same logic as above
    for i in two_genes:
        if people[i]["mother"] is None:
            prob_two = PROBS["gene"][2]
        elif people[i]["mother"] is not None:
            prob_two = 1
            mother = people[i]["mother"]
            father = people[i]["father"]

            # Mother no genes cases
            if mother in (people.keys() - (one_gene | two_genes)) and father in (
                    people.keys() - (one_gene | two_genes)):
                prob_two *= PROBS["mutation"] * PROBS["mutation"]
            if mother in (people.keys() - (one_gene | two_genes)) and father in one_gene:
                prob_two *= PROBS["mutation"] * 0.5
            if mother in (people.keys() - (one_gene | two_genes)) and father in two_genes:
                prob_two *= PROBS["mutation"] * (1 - PROBS["mutation"])

            # Mother one gene cases
            if mother in one_gene and father in (people.keys() - (one_gene | two_genes)):
                prob_two *= 0.5 * PROBS["mutation"]
            if mother in one_gene and father in one_gene:
                prob_two *= 0.5 * 0.5
            if mother in one_gene and father in two_genes:
                prob_two *= 0.5 * (1 - PROBS["mutation"])

            # Mother two genes cases
            if mother in two_genes and father in (people.keys() - (one_gene | two_genes)):
                prob_two *= (1 - PROBS["mutation"]) * PROBS["mutation"]
            if mother in two_genes and father in one_gene:
                prob_two *= (1 - PROBS["mutation"]) * 0.5
            if mother in two_genes and father in two_genes:
                prob_two *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"])

        # Calculate final probability
        prob_two = prob_two * (PROBS["trait"][2][(i in have_trait)])
        probability = probability * prob_two

    # Compute and return a joint probability.
    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    # For each person
    for per in probabilities:
        # Add joint probability to individual gene probabilities:

        # zero genes
        if per not in (one_gene or two_genes):
            probabilities[per]['gene'][0] += p

        # one gene
        elif per in one_gene:
            probabilities[per]['gene'][1] += p

        # two genes
        elif per in two_genes:
            probabilities[per]['gene'][2] += p

        # error if outside of two groups (can only be zero, one and two)
        else:
            raise AttributeError

        # Then, add joint probability to trait subgroups, either with or without trait:
        if per in have_trait:
            probabilities[per]['trait'][True] += p
        else:
            probabilities[per]['trait'][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    # For each person
    for per in probabilities:

        # First, calculate total probability for person irregardless of gene
        total = 0
        for i in range(3):
            total += probabilities[per]["gene"][i]

        # Then, divide individual gene subset probability by total
        for i in range(3):
            probabilities[per]["gene"][i] = probabilities[per]["gene"][i] / total

        # Finally, do a similar operation for the individual trait subsets
        total = probabilities[per]["trait"][True] + probabilities[per]["trait"][False]
        probabilities[per]["trait"][True] = probabilities[per]["trait"][True] / total
        probabilities[per]["trait"][False] = probabilities[per]["trait"][False] / total

        # No return for this function


if __name__ == "__main__":
    main()
