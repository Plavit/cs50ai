import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass



def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # DEBUG: Print source and target
    # print("src: ", source)
    # print("target: ", target)

    # Handle same name entered
    if source == target:
        sys.exit("Same actor entered twice")

    # Define frontier as queue for breadth-first search
    frontier = QueueFrontier()
    # Track degrees of separation
    degree = 0
    # Track explored actors, create empty result queue
    explored = list()
    explored.append(source)

    # Track result and next upper node we know to be on the result path
    result = []
    upper_correct_node = None

    # Add first actor to frontier
    frontier.add(Node((None, source), None, degree))

    # While frontier is not empty or a result is not found, search for result
    while not frontier.empty():
        # Keep track of degrees of separation
        degree += 1

        # # DEBUG - frontier print
        # print("Searching Degree {}, of size {}".format(degree, size))
        # print(frontier)

        # For each degree, search for result in expanded nodes
        size = len(frontier.frontier)
        for i in range(size):
            expanded_node = frontier.remove()
            for movie in people[expanded_node.state[1]]["movies"]:
                # Expand actors and add individual nodes to frontier
                for actor in movies[movie]["stars"]:
                    # Check if actor is target, if yes, add final movie to result and set last correct node
                    if actor == target:
                        result.append((movie, actor))
                        upper_correct_node = expanded_node
                        # Break out of all loops if found result
                        break

                    # Check if already visited actor - add to frontier and explored if not
                    elif actor not in explored:
                        node = Node((movie, actor), expanded_node, degree)
                        frontier.add(node)
                        explored.append(actor)
                if len(result) > 0:
                    break

            if len(result) > 0:
                break

        if len(result) > 0:
            break

    # Finally, if the frontier has nowhere else to look, return no result
    if frontier.empty():
        return None
    # Else, unpack frontier and reverse to get result
    else:
        # While node.parent is not empty (which is at source), go up by parent
        while upper_correct_node.parent is not None:
            # Keep adding path to source
            result.append(upper_correct_node.state)
            # Reverse at the end
            upper_correct_node = upper_correct_node.parent
        result.reverse()
        return result


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
