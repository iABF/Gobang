import pygame
import sys

MP_SIZE = 15
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOARD_MARGIN = 30
BOX_SIZE = (SCREEN_HEIGHT - 2 * BOARD_MARGIN) / (MP_SIZE - 1)


def get_pos(x):
    return x * BOX_SIZE + BOARD_MARGIN


class ChessBoard:
    def __init__(self, size, black=1):
        self.size = size
        self.board = [[0 for x in range(size)] for y in range(size)]
        self.chessList = []
        self.blackFirst = black  # default: Black chess first according to human rules

    def draw_chess(self, screen, x, y, index):
        center = (int(get_pos(x)), int(get_pos(y)))
        if (self.blackFirst + index) % 2 == 1:
            color = (18, 23, 27)
        else:
            color = (245, 249, 250)
        pygame.draw.circle(screen, color, center, int(BOX_SIZE * 0.4))

    def initialize(self, screen):
        for x in range(self.size):
            u, v, w, t = (get_pos(x), BOARD_MARGIN), \
                         (get_pos(x), SCREEN_HEIGHT - BOARD_MARGIN), \
                         (BOARD_MARGIN, get_pos(x)), \
                         (SCREEN_HEIGHT - BOARD_MARGIN, get_pos(x))
            pygame.draw.line(screen, (0, 0, 0), u, v)
            pygame.draw.line(screen, (0, 0, 0), w, t)
        pos = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        for (x, y) in pos:
            rect = (get_pos(x) - 2, get_pos(y) - 2, 6, 6)
            pygame.draw.rect(screen, (0, 0, 0), rect)
        for index, (x, y) in enumerate(self.chessList):
            self.draw_chess(screen, x, y, index)
            if index == len(self.chessList) - 1:
                pygame.draw.circle(screen, (255, 0, 0), (int(get_pos(x)), int(get_pos(y))), int(BOX_SIZE * 0.1))

    def get_chess_pos(self, mse_x, mse_y):
        for x in range(self.size):
            for y in range(self.size):
                if (get_pos(x) - mse_x) ** 2 + (get_pos(y) - mse_y) ** 2 <= (BOX_SIZE * 0.4) ** 2:
                    return x, y
        return -1, -1

    def put_chess(self, x, y):
        if len(self.chessList) > 0:
            u, v = self.chessList[len(self.chessList) - 1]
            self.board[x][y] = 1 - self.board[u][v]
        else:
            self.board[x][y] = self.blackFirst
        self.chessList.append((x, y))


class Button:
    def __init__(self, screen, x, y, text):
        self.screen = screen


def is_chessboard(mse_x, mse_y):
    if BOARD_MARGIN - BOX_SIZE * 0.4 <= mse_x <= SCREEN_HEIGHT - BOARD_MARGIN + BOX_SIZE * 0.4 and \
            BOARD_MARGIN - BOX_SIZE * 0.4 <= mse_y <= SCREEN_HEIGHT - BOARD_MARGIN + BOX_SIZE * 0.4:
        return True
    else:
        return False


class Gobang:
    def __init__(self, caption):
        pygame.init()
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption(caption)
        self.chessBoard = ChessBoard(MP_SIZE)
        self.turn = True  # default: Player first

    def refresh(self):
        pygame.draw.rect(self.screen, (202, 152, 99), pygame.Rect(0, 0, SCREEN_HEIGHT, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(SCREEN_HEIGHT, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.chessBoard.initialize(self.screen)

    def mouse_action(self, mse_x, mse_y):
        if is_chessboard(mse_x, mse_y):
            if self.turn:
                x, y = self.chessBoard.get_chess_pos(mse_x, mse_y)
                if x >= 0:
                    self.chessBoard.put_chess(x, y)


chessGame = Gobang("Gobang")
while True:
    chessGame.refresh()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            chessGame.mouse_action(mouse_x, mouse_y)
