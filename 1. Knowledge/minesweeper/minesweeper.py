import itertools
import random
import copy

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
        if self.count == len(self.cells):
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
    
    def get_neighbors(self, cell, height, width):
        """
        Simply adds set of all neighboring cells for a given cell to self.cells.
        Does not check if cell is known or played.
        """
        neighbors = set() 
        row = cell[0]
        col = cell[1]
        for i in range(0, height):
            for j in range(0, width):
                if (i == row - 1) or (i == row) or (i == row + 1):
                    if (j == col -1) or (j == col) or (j == col + 1):
                        if (i, j) != (row, col):
                            neighbors.add((i, j))
        self.cells = neighbors

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

    def evaluate_knowledge(self):
        """
        Iterate through knowledge base and clean the data and make further inferences
        """
        while True:
            knowledge_copy = copy.deepcopy(self.knowledge)
            
            # Identify if any new safe moves were found
            for sentence in self.knowledge:
                if sentence.known_safes() != set():
                    new_safes = []
                    for safe_cell in sentence.known_safes():
                        if safe_cell not in self.safes:
                            print("new safe cell", safe_cell)
                            new_safes.append(safe_cell)
                    for cell in new_safes:
                        self.mark_safe(cell)

            # Identify if any new mines were found
            for sentence in self.knowledge:
                if sentence.known_mines() != set():
                    found_mines = []
                    for new_mine in sentence.known_mines():
                        if new_mine not in self.mines:
                            print("new mine found", new_mine)
                            found_mines.append(new_mine)
                    for mine in found_mines:
                        self.mark_mine(mine)

            # Clear out emply sets
            for sentence in self.knowledge:
                if sentence.cells == set():
                    self.knowledge.remove(sentence)

            # Make inferences
            for sentence in self.knowledge:
                for another_sentence in self.knowledge:
                    if sentence != another_sentence:
                        print("checking issubset")
                        # Check to see if sentence is subset of another sentence
                        if sentence.cells.issubset(another_sentence.cells):
                            print("inferred sentence being made")
                            another_sentence.cells.difference_update(sentence.cells)
                            another_sentence.count = another_sentence.count - sentence.count
                            # inferred_sentence = Sentence(cells=inferred_set, count=inferred_count)
                            sentence.cells = set()
                            sentence.count = 0
                            # Apply the inference to knowledge base
                            # if inferred_sentence not in self.knowledge:
                            #     self.knowledge.append(inferred_sentence)
                            
            
            # Break after all inferences are made
            if knowledge_copy == self.knowledge:
                break                    

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

        # Update knowledge to reflect move just made
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Remove cell from all sentences in KB, and remove sentence if empty
        for sentence in self.knowledge:
            if cell in sentence.cells:
                sentence.cells.remove(cell)
            if sentence.cells == set():
                self.knowledge.remove(sentence)

        # Make sentence for new move
        new_sentence = Sentence(cells=set(), count=count)
        new_sentence.get_neighbors(cell, self.height, self.width)

        # Remove any cells found in mines, safes, moves_made
        new_sentence.cells.difference_update(self.mines)
        new_sentence.cells.difference_update(self.safes)
        new_sentence.cells.difference_update(self.moves_made)

        # Give sentence to knowledge base
        self.knowledge.append(new_sentence)

        # Evaluate any updates or changes
        self.evaluate_knowledge()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        print("safe cells: ", self.safes)
        print("mines: ", self.mines)

        # Make new set of safe moves that have not been played
        practice_safe_sets = self.safes.difference(self.moves_made) # ;)

        # Pick random safe cell
        if practice_safe_sets != set():
            return random.sample(practice_safe_sets, 1)[0]
        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Grab all cell locations
        available_cells = set()
        for row in range(0, self.height):
            for col in range(0, self.width):
                available_cells.add((row, col))
        
        # Remove locations with mines and made moves
        available_cells.difference_update(self.mines)
        available_cells.difference_update(self.moves_made)

        # Pick a random cell
        if available_cells != set():
            return random.sample(available_cells, 1)[0]
        else:
            return None