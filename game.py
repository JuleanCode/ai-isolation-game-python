import pygame
import sys
import copy

pygame.init()

# Constanten aanmaken
WIDTH, HEIGHT = 480, 480
GRID_SIZE = 6
CELL_SIZE = WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
PLAYER_X_COLOR = (255, 0, 0)
PLAYER_O_COLOR = (0, 0, 255)
HIGHLIGHT_COLOR = (0, 255, 0)  # Green for highlighting available moves
PATH_DOT_COLOR_X = (200, 0, 0)  # Red for path dots of player X
PATH_DOT_COLOR_O = (0, 0, 200)  # Blue for path dots of player O

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Isolation Game")

# Initialize the board with starting positions
board = [[" " for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
board[0][0] = "X"
board[GRID_SIZE - 1][GRID_SIZE - 1] = "O"

# opslaan waar de spelers zijn
player_x_pos = [0, 0]
player_o_pos = [GRID_SIZE - 1, GRID_SIZE - 1]

# opslaan waar de spelers zijn geweest
path_x = [(0, 0)]
path_o = [(GRID_SIZE - 1, GRID_SIZE - 1)]

available_moves = []

def draw_grid():
    for row in range(1, GRID_SIZE):
        pygame.draw.line(screen, LINE_COLOR, (0, row * CELL_SIZE), (WIDTH, row * CELL_SIZE))
        pygame.draw.line(screen, LINE_COLOR, (row * CELL_SIZE, 0), (row * CELL_SIZE, HEIGHT))

# x en o op het speelveld zetten
def draw_board():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] == "X":
                pygame.draw.line(screen, PLAYER_X_COLOR, (col * CELL_SIZE, row * CELL_SIZE),
                                 ((col + 1) * CELL_SIZE, (row + 1) * CELL_SIZE), 5)
                pygame.draw.line(screen, PLAYER_X_COLOR, ((col + 1) * CELL_SIZE, row * CELL_SIZE),
                                 (col * CELL_SIZE, (row + 1) * CELL_SIZE), 5)
            elif board[row][col] == "O":
                pygame.draw.circle(screen, PLAYER_O_COLOR, (col * CELL_SIZE + CELL_SIZE // 2,
                                 row * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2 - 5, 5)

    for x, y in path_x:
        pygame.draw.circle(screen, PATH_DOT_COLOR_X, (y * CELL_SIZE + CELL_SIZE // 2,
                            x * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 8)

    for x, y in path_o:
        pygame.draw.circle(screen, PATH_DOT_COLOR_O, (y * CELL_SIZE + CELL_SIZE // 2,
                            x * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 8)

    # aanmaken van de groene stippen van de zetten die gemaakt kunnen worden
    for move in available_moves:
        x, y = move
        pygame.draw.circle(screen, HIGHLIGHT_COLOR, (y * CELL_SIZE + CELL_SIZE // 2,
                            x * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 4)

    if current_player == "X":
        player_color = PLAYER_X_COLOR
        x, y = player_x_pos
    else:
        player_color = PLAYER_O_COLOR
        x, y = player_o_pos

    pygame.draw.circle(screen, player_color, (y * CELL_SIZE + CELL_SIZE // 2,
                        x * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 8)

def is_valid_move(row, col):
    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and board[row][col] == " ":
        return True
    return False

def find_available_moves(player_pos):
    available = []
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            x, y = player_pos[0] + dx, player_pos[1] + dy
            while 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and board[x][y] == " ":
                available.append((x, y))
                x += dx
                y += dy
    return available

def update_available_moves():
    global available_moves
    if current_player == "X":
        available_moves = find_available_moves(player_x_pos)
    else:
        available_moves = find_available_moves(player_o_pos)

def can_make_move(player_pos):
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            x, y = player_pos[0] + dx, player_pos[1] + dy
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and board[x][y] == " ":
                return True
    return False

# Voor de bot
def evaluate_board(board):
    player_x_moves = len(find_available_moves(player_x_pos))
    player_o_moves = len(find_available_moves(player_o_pos))

    return player_x_moves - player_o_moves

# Minimax algoritme
def minimax(board, depth, maximizing_player, alpha, beta):
    if depth == 0 or not can_make_move(player_x_pos) or not can_make_move(player_o_pos):
        return evaluate_board(board)

    if maximizing_player:
        max_eval = float("-inf")
        for move in find_available_moves(player_o_pos):
            new_board = copy.deepcopy(board)
            new_board[move[0]][move[1]] = "O"
            max_eval = max(max_eval, minimax(new_board, depth - 1, False, alpha, beta))
            alpha = max(alpha, max_eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for move in find_available_moves(player_x_pos):
            new_board = copy.deepcopy(board)
            new_board[move[0]][move[1]] = "X"
            min_eval = min(min_eval, minimax(new_board, depth - 1, True, alpha, beta))
            beta = min(beta, min_eval)
            if beta <= alpha:
                break
        return min_eval

# de beste zet vinden voor de bot
def find_best_move(board, depth):
    best_move = None
    best_eval = float("-inf")
    for move in find_available_moves(player_o_pos):
        new_board = copy.deepcopy(board)
        new_board[move[0]][move[1]] = "O"
        eval = minimax(new_board, depth - 1, False, float("-inf"), float("inf"))
        if eval > best_eval:
            best_eval = eval
            best_move = move
    return best_move

def game_over(winner):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Player {winner} wins! Press R to restart.", True, LINE_COLOR)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.update()

def reset_game():
    global board, player_x_pos, player_o_pos, path_x, path_o, current_player, game_over_message_shown
    board = [[" " for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    board[0][0] = "X"
    board[GRID_SIZE - 1][GRID_SIZE - 1] = "O"
    player_x_pos = [0, 0]
    player_o_pos = [GRID_SIZE - 1, GRID_SIZE - 1]
    path_x = [(0, 0)]
    path_o = [(GRID_SIZE - 1, GRID_SIZE - 1)]
    current_player = "X"
    update_available_moves()
    game_over_message_shown = False




# <------------------------Main loop------------------------>
current_player = "X"
running = True
update_available_moves()
game_over_message_shown = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            col = x // CELL_SIZE
            row = y // CELL_SIZE
            if is_valid_move(row, col) and (row, col) in available_moves:
                if current_player == "X":
                    path_x.append((player_x_pos[0], player_x_pos[1]))
                    player_x_pos = [row, col]
                else:
                    path_o.append((player_o_pos[0], player_o_pos[1]))
                    player_o_pos = [row, col]
                board[row][col] = "X" if current_player == "X" else "O"
                current_player = "O" if current_player == "X" else "X"
                update_available_moves()

    if not can_make_move(player_x_pos):
        game_over("O")
        pygame.display.update()
        game_over_message_shown = True

    if not can_make_move(player_o_pos):
        game_over("X")
        pygame.display.update()
        game_over_message_shown = True

    if not game_over_message_shown and not any(can_make_move([r, c]) for r in range(GRID_SIZE) for c in range(GRID_SIZE)):
        game_over("Draw")
        pygame.display.update()
        game_over_message_shown = True

    # Voor de bot
    if current_player == "O" and not game_over_message_shown:
        best_move = find_best_move(board, 5)  # hier kun je de diepte van de min max aanpassen
        if best_move is not None:
            row, col = best_move
            path_o.append((player_o_pos[0], player_o_pos[1]))
            player_o_pos = [row, col]
            board[row][col] = "O"
            current_player = "X"
            update_available_moves()

    #wanneer je op r drukt reset het spel
    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
        reset_game()
        game_over_message_shown = False

    screen.fill(WHITE)
    draw_grid()
    draw_board()
    pygame.display.update()

pygame.quit()
sys.exit()