HUMAN = 'X'
AI = 'O'
EMPTY = ' '


def initial_board():
    return [EMPTY] * 9


def print_board(board):
    for i in range(0, 9, 3):
        print(f" {board[i]} | {board[i+1]} | {board[i+2]} ")
        if i < 6:
            print("---+---+---")


def available_moves(board):
    return [i for i, v in enumerate(board) if v == EMPTY]


def check_winner(board, player):
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    return any(board[a] == board[b] == board[c] == player for a, b, c in wins)


def is_terminal(board):
    return check_winner(board, HUMAN) or check_winner(board, AI) or not available_moves(board)


def minimax(board, is_maximizing, alpha, beta):
    if check_winner(board, AI):
        return 1
    if check_winner(board, HUMAN):
        return -1
    if not available_moves(board):
        return 0

    if is_maximizing:
        best = -2
        for move in available_moves(board):
            board[move] = AI
            best = max(best, minimax(board, False, alpha, beta))
            board[move] = EMPTY
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = 2
        for move in available_moves(board):
            board[move] = HUMAN
            best = min(best, minimax(board, True, alpha, beta))
            board[move] = EMPTY
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best


def best_move(board):
    best_score, move = -2, None
    for m in available_moves(board):
        board[m] = AI
        score = minimax(board, False, -2, 2)
        board[m] = EMPTY
        if score > best_score:
            best_score, move = score, m
    return move
