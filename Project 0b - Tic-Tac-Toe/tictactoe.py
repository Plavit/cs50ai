"""
Tic Tac Toe Player
"""

from copy import deepcopy

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

    x_count = 0
    o_count = 0

    for row in board:
        for state in row:
            if state == X:
                x_count += 1
            elif state == O:
                o_count += 1

    if x_count <= o_count:
        return X
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    action_set = set()
    y_coordinate = 0
    x_coordinate = 0

    for row in board:
        y_coordinate = 0
        for state in row:
            if state == EMPTY:
                action_set.add((x_coordinate, y_coordinate))
            y_coordinate += 1
        x_coordinate += 1

    return action_set


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = deepcopy(board)

    if not (0 <= action[0] < 3) and (0 <= action[0] < 3):
        raise Exception("Invalid move - out of bounds")

    if new_board[action[0]][action[1]] is not EMPTY:
        raise Exception("Invalid move - field already filled")

    new_board[action[0]][action[1]] = player(board)

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # check rows
    x = 0
    y = 0

    win_counter = 0
    while x < 3 and y < 3:
        state = board[y][x]
        if state == X:
            win_counter += 1
        elif state == O:
            win_counter -= 1
        if win_counter == 3:
            return X
        elif win_counter == -3:
            return O
        x += 1
        if x == 3:
            x = 0
            y += 1
            win_counter = 0

    # check columns
    x = 0
    y = 0

    win_counter = 0
    while x < 3 and y < 3:
        state = board[x][y]
        if state == X:
            win_counter += 1
        elif state == O:
            win_counter -= 1
        if win_counter == 3:
            return X
        elif win_counter == -3:
            return O
        x += 1
        if x == 3:
            x = 0
            y += 1
            win_counter = 0

    # check diagonals
    x = 0
    y = 0
    win_counter = 0
    while x < 3 and y < 3:
        state = board[x][y]
        if state == X:
            win_counter += 1
        elif state == O:
            win_counter -= 1
        if win_counter == 3:
            return X
        elif win_counter == -3:
            return O
        x += 1
        y += 1

    x = 0
    y = 2
    win_counter = 0
    while x < 3 and y >= 0:
        state = board[x][y]
        if state == X:
            win_counter += 1
        elif state == O:
            win_counter -= 1
        if win_counter == 3:
            return X
        elif win_counter == -3:
            return O
        x += 1
        y -= 1

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    for x in range(3):
        for y in range(3):
            if board[x][y] == EMPTY:
                return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board. TODO
    """
    current_player = player(board)

    next_action = None
    if terminal(board):
        return next_action

    # If X, maximize
    if current_player == X:
        value = -10
        for action in actions(board):
            option = min_value(result(board, action))
            if option > value:
                value = option
                next_action = action

    # If O, minimize
    elif player(board) == O:
        value = 10
        for action in actions(board):
            option = max_value(result(board, action))
            if option < value:
                value = option
                next_action = action
    return next_action


def min_value(board):
    if terminal(board):
        return utility(board)
    else:
        value = 10
        for action in actions(board):
            option = max_value(result(board, action))
            if option < value:
                value = option

    return value


def max_value(board):
    if terminal(board):
        return utility(board)
    else:
        value = -10
        for action in actions(board):
            option = min_value(result(board, action))
            if option > value:
                value = option

    return value
