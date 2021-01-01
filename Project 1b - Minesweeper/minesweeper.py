import copy
import itertools
import random
from typing import Set, Callable, Tuple


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == 0:
            return set()
        elif len(self.cells) == self.count:
            return self.cells
        # raise ValueError("Untracked mine cell detected") # This caused unintended behaviour
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            # remove cell from set of possibilities and subtracts the number of  expected mines to be found
            self.cells.remove(cell)
            self.count -= 1
        return

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        return


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # The algorithm shall be implemented step by step:

        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)

        # 3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        cells = []

        # Iterate over the surrounding cells
        for row in range(cell[0] - 1, cell[0] + 2):
            for column in range(cell[1] - 1, cell[1] + 2):
                # Do not analyse cell itself
                if (row, column) != cell:
                    # If cell in border is mine, update number
                    if 0 <= row < self.height and 0 <= column < self.width:
                        if (row, column) in self.mines:
                            count -= 1
                        elif (row, column) not in self.safes:
                            cells.append((row, column))
        self.knowledge.append(Sentence(cells, count))

        # 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        for sentence in self.knowledge:
            safe = sentence.known_safes()
            mine = sentence.known_mines()
            if mine:
                self.mines = self.mines.union(mine)
            if safe:
                self.safes = self.safes.union(safe)

        # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        for row in range(len(self.knowledge)):
            for column in range(row + 1, len(self.knowledge)):

                #Create sentence boilerplates
                sentence_row = self.knowledge[row]
                sentence_column = self.knowledge[column]

                # If row sentence is subset of columns, add difference to knowledge base if not there yet
                if sentence_row.cells.issubset(sentence_column.cells):
                    new = Sentence(sentence_column.cells - sentence_row.cells, sentence_column.count - sentence_row.count)
                    if new not in self.knowledge:
                        self.knowledge.append(new)

                # Same for column sentence
                elif sentence_column.cells.issubset(sentence_row.cells):
                    new = Sentence(sentence_row.cells - sentence_column.cells, sentence_row.count - sentence_column.count)
                    if new not in self.knowledge:
                        self.knowledge.append(new)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell

        print("No moves possible for Safe Move")
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Get the possible moves
        possibilities: list = self.possible_moves()

        # Shuffle possible moves and choose the first random one
        random.shuffle(possibilities)
        if 0 < len(possibilities):
            return possibilities[0]

        print("No moves possible for Random Move")
        return None

    def possible_moves(self):
        # Create an empty set to store possible moves
        possibilities = []

        # For each field in the game...
        for row in range(self.height):
            for column in range(self.width):
                # ...Add it to possible moves if it is new and not a known mine
                if (row, column) not in self.moves_made:
                    if (row, column) not in self.mines:
                        possibilities.append((row, column))
        return possibilities
