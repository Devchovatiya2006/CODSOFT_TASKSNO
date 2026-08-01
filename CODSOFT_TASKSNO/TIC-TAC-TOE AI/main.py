from tictactoe import (
    initial_board, print_board, available_moves,
    check_winner, is_terminal, best_move, HUMAN, AI
)


def get_human_move(board):
    while True:
        try:
            move = int(input("Your move (1-9): ")) - 1
            if move in available_moves(board):
                return move
            print("Invalid move. Try again.")
        except ValueError:
            print("Enter a number between 1 and 9.")


def play():
    board = initial_board()
    print("\nTic-Tac-Toe  |  You: X   AI: O")
    print("Positions:   |  1 2 3 / 4 5 6 / 7 8 9\n")

    choice = input("Do you want to go first? (y/n): ").strip().lower()
    human_first = choice != 'n'
    current = HUMAN if human_first else AI

    while not is_terminal(board):
        print_board(board)
        if current == HUMAN:
            move = get_human_move(board)
        else:
            print("AI is thinking...")
            move = best_move(board)
        board[move] = current
        current = AI if current == HUMAN else HUMAN

    print_board(board)
    if check_winner(board, HUMAN):
        print("You win! 🎉")
    elif check_winner(board, AI):
        print("AI wins! 🤖")
    else:
        print("It's a draw! 🤝")


if __name__ == "__main__":
    while True:
        play()
        if input("\nPlay again? (y/n): ").strip().lower() != 'y':
            break
