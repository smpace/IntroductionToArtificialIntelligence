"""
Tic Tac Toe Player

Steven Pace Project 0 CSCI E80

"""
import math, random

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Function counts filled spaces and returns X if even spaces filled, or O if odd spaces filled
    count = 0
    for row in board:
        for elem in row:
            if elem != EMPTY:
                count += 1
    if count % 2 != 0:
        return O
    else:
        return X

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Returns a set of indices for all elements that are EMPTY   
    moves = set()
    for rowIndex, row in enumerate(board):
        for colIndex, element in enumerate(row):
            if element == EMPTY:
                moves.add((rowIndex, colIndex))
    return moves

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Places next players' symbol in action location on board
    possible_actions = actions(board)
    if action not in possible_actions:
        raise Exception("Invalid move")
    # Make new copy of board
    new_board = []
    for row in board:
        new_board.append(list(row))
    # Place player symbol in action location of new board
    new_board[action[0]][action[1]] = player(board)
    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    win = False
    # Check cols and rows
    for i in range(3):
        if (board[i][0] == board[i][1] == board[i][2] != EMPTY) or (board[0][i] == board[1][i] == board[2][i] != EMPTY):
            win = True
    # Check diagonals
    if (board[0][0] == board[1][1] == board[2][2] != EMPTY) or (board[0][2] == board[1][1] == board [2][0] != EMPTY):
        win = True
    # Return the winner
    if win:
        loser = player(board)
        if loser == O:
            return X
        else:
            return O
    else:
        return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Keeps game going only if more cells are EMPTY and there is not a winner
    if (EMPTY in [elem for row in board for elem in row]) and (winner(board) == None):
        return False
    else:
        return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # Given a terminal board, returns a end of game value
    if terminal(board):
        game_winner = winner(board)
        if game_winner == X:
            return 1
        elif game_winner == O:
            return -1
        else:
            return 0
    else:
        return None

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    
    # Given a board, find max value
    def max_value(a_board):
        if terminal(a_board):
            return utility(a_board)
        v = -math.inf
        # Call min_value on all actions that are not terminal
        for action in actions(a_board):
            # Choose the max value out of all returned min values
            v = max(v, min_value(result(a_board, action)))
        return v
    
    # Given a board, find min value
    def min_value(a_board):
        if terminal(a_board):
            return utility(a_board)
        v = math.inf
        # Call max_value on all actions that are not terminal
        for action in actions(a_board):
            # Choose the min value out of all returned max values
            v = min(v, max_value(result(a_board, action)))
        return v
    
    # See if X or O has next turn
    this_player = player(board)
    # Find all possible moves
    possible_actions = actions(board)
    moves = []
    for action in possible_actions:
        # For each action, find the optimal value for the move and appends (v, move) to list
        if this_player == X:
            best_value = min_value(result(board, action))
            moves.append((best_value, action))
        else:
            best_value = max_value(result(board, action))
            moves.append((best_value, action))
    # Depending on the player, returns a move with their optimal outcome
    if this_player == X:
        # Finds max value available in moves list
        max_v = max(moves, key = lambda high_score: high_score[0])[0]
        # Keeps only tuples that have the max value
        moves = [move for move in moves if move[0] == max_v]
        # Picks random move from optimal choices
        best_max_move = random.choice(moves)
        return best_max_move[1]
    else:
        # Finds min value available in moves list
        min_v = min(moves, key = lambda low_score: low_score[0])[0]
        # Keeps only tuples that have the min value
        moves = [move for move in moves if move[0] == min_v]
        # Picks random move from optimal choices
        best_min_move = random.choice(moves)
        return best_min_move[1]