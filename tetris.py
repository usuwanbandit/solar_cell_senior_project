import random
import time
import os

# Constants
WIDTH = 10
HEIGHT = 20
EMPTY = ' '
BLOCK = '#'

# Tetromino shapes
SHAPES = [
    [(0, 0), (1, 0), (0, 1), (1, 1)],  # Square
    [(0, 0), (1, 0), (2, 0), (3, 0)],  # Line
    [(1, 0), (0, 1), (1, 1), (2, 1)],  # L-shape
    [(0, 0), (0, 1), (1, 1), (2, 1)],  # Reverse L-shape
    [(1, 0), (2, 0), (0, 1), (1, 1)],  # S-shape
    [(0, 0), (1, 0), (1, 1), (2, 1)],  # Reverse S-shape
    [(0, 0), (1, 0), (2, 0), (1, 1)]   # T-shape
]

# Function to create a new Tetromino


# Function to check if a position is valid for a Tetromino
def is_valid_position(tetromino):
    return all(0 <= x < WIDTH and 0 <= y < HEIGHT for x, y in tetromino)

# Function to draw the game board
def draw_board(board, tetromino):
    os.system('cls' if os.name == 'nt' else 'clear')
    print('-' * (WIDTH + 2))
    for y in range(HEIGHT):
        line = '|'
        for x in range(WIDTH):
            line += BLOCK if (x, y) in tetromino or board[y][x] == BLOCK else EMPTY
        line += '|'
        print(line)
    print('-' * (WIDTH + 2))

# Function to update the game board with the current Tetromino
def update_board(board, tetromino):
    for x, y in tetromino:
        board[y][x] = BLOCK

# Function to check for completed rows and clear them
def clear_rows(board):
    completed_rows = [row for row in board if all(cell == BLOCK for cell in row)]
    for row in completed_rows:
        board.remove(row)
        board.insert(0, [EMPTY] * WIDTH)

# Function to move the Tetromino down
def move_down(tetromino):
    return [(x, y + 1) for x, y in tetromino]

# Function to move the Tetromino left
def move_left(tetromino):
    return [(x - 1, y) for x, y in tetromino]

# Function to move the Tetromino right
def move_right(tetromino):
    return [(x + 1, y) for x, y in tetromino]

# Function to rotate the Tetromino
def rotate(tetromino):
    cx, cy = sum(x for x, _ in tetromino) / len(tetromino), sum(y for _, y in tetromino) / len(tetromino)
    return [(int(cx + cy - y), int(cy - cx + x)) for x, y in tetromino]

# Main function to run the game
def main():
    def new_tetromino():
        shape = random.choice(SHAPES)
        return [(x + WIDTH // 2 - 1, y) for x, y in shape]
    board = [[EMPTY] * WIDTH for _ in range(HEIGHT)]
    tetromino = new_tetromino()
    while True:
        draw_board(board, tetromino)
        time.sleep(0.5)
        new_tetromino = move_down(tetromino)
        if is_valid_position(new_tetromino):
            tetromino = new_tetromino
        else:
            update_board(board, tetromino)
            clear_rows(board)
            tetromino = new_tetromino()

if __name__ == "__main__":
    main()
