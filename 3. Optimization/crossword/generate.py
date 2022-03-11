import sys
import random

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Iterate through all the variables in a domain
        for variable in self.domains:
            non_unary = []
            for word in self.domains[variable]:
                # If the word does not fit into the variable, remove it
                if len(word) != variable.length:
                    non_unary.append(word)
            for word in non_unary:
                self.domains[variable].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        changed = False
        non_arc = set()

        # Grab overlap index of each variable
        if self.crossword.overlaps[x, y]:
            x_index, y_index = self.crossword.overlaps[x, y]

            # Compare the letters at the index of each word
            # If y has a possible value that matches x, keep x.
            for x_word in self.domains[x]:
                arc_consistent = False
                for y_word in self.domains[y]:
                    if x_word[x_index] != y_word[y_index]:
                        arc_consistent = True
                        break
                if not arc_consistent:
                    non_arc.add(x_word)
            
            # Remove all words that didn't have a match
            if len(non_arc) > 0:
                for word in non_arc:
                    self.domains[x].remove(word)
                changed = True

        # State whether a change has happened or not
        return changed


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = []
        
        # Initialize queue with either arcs or neighbors
        if arcs:
            queue = arcs
        else:
            for variable1 in self.crossword.variables:
                for variable2 in self.crossword.neighbors(variable1):
                    queue.append((variable1, variable2))
        
        # Check each pair on queue to see if it can be revised
        while queue:
            (x, y) = queue.pop(0)
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                # If a variable gets revised, add the neighbors back to the queue
                for neighbor in self.crossword.neighbors(x) - {y}:
                    queue.append((neighbor, x))

        # Return confirmation that domain is arc consistent after while loop finishes
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False
        
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for variable1 in assignment:
            # Check that length is consistent
            if variable1.length != len(assignment[variable1]):
                return False

            for variable2 in assignment:
                if variable1 == variable2:
                    continue
                # Check that variable is not dupicated
                if assignment[variable1] == assignment[variable2]:
                    return False

                # Check that the overlaps are the same letter
                if self.crossword.overlaps[variable1, variable2]:
                    var1_index, var2_index = self.crossword.overlaps[variable1, variable2]
                    if assignment[variable1][var1_index] != assignment[variable2][var2_index]:
                        return False

        return True


    def order_domain_values(self, var, assignment):                     
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        lst = []

        # For each word in var domain, compare to each word in neighbor
        for word in self.domains[var]:
            count = 0
            # Loop through all neighbors of var
            for neighbor in self.crossword.neighbors(var):
                # Skip if neighbor already has assignment
                if neighbor in assignment:
                    continue
                overlap_index = self.crossword.overlaps[var, neighbor]
                for a_word in self.domains[neighbor]:
                    if word[overlap_index[0]] != a_word[overlap_index[1]]:
                        count += 1
            # Store values for each word
            lst.append([word, count])
        # Sort lst by count
        lst.sort(key=lambda pair: pair[1])
        # Make new list in the same order as lst, but remove the count num
        odv_lst = list(word[0] for word in lst)

        return odv_lst


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        lst = []

        # Loop through variables in crossword
        for variable in self.crossword.variables:
            if variable not in assignment:
                # Add every unassigned variable and the # of words in domain to lst
                lst.append([variable, len(self.domains[variable])])

        # Sort the lst asc on the # of words in domain
        lst.sort(key=lambda pair: pair[1])
        # Only retain the variable/word count pairs that have the lowest count
        # Pair is a [var, word count]
        lst = list(pair for pair in lst if pair[1] == lst[0][1])

        # This drops the word count from pair and replaces it with the # of neighbors
        for pair in lst:
            pair[1] = len(self.crossword.neighbors(pair[0]))
        # Reverse puts the highest # of neighbors at front of lst
        lst.sort(reverse=True, key=lambda pair: pair[1])

        # Create new list with min values and highest # of neighbors
        # Var is a [var, # of neighbors]
        min_lst = list(var[0] for var in lst if var[1] == lst[0][1])

        # Return a random one
        return random.choice(min_lst)


    def backtrack(self, assignment):                               
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Code used from schedule0.py from lecture. I really only changed the 
        # function calls to be on the self obj. Arc consistency is not 
        # implemented.

        # Check if assignment is complete
        if self.assignment_complete(assignment):
            return assignment

        # Try a new variable
        variable = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(variable, assignment):
            new_assignment = assignment.copy()
            new_assignment[variable] = value
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
