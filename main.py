import pygame
import sys

MP_SIZE = 15
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOARD_MARGIN = 30
BOX_SIZE = (SCREEN_HEIGHT - 2 * BOARD_MARGIN) / (MP_SIZE - 1)


class ChessBoard:
    def __init__(self, size):
        self.size = size
        self.board = [[0 for x in range(size)] for y in range(size)]
        self.chessList = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        self.blackFirst = 1

    def draw_chess(self, screen, x, y, index):
        center = (int(x * BOX_SIZE + BOARD_MARGIN), int(y * BOX_SIZE + BOARD_MARGIN))
        if (self.blackFirst + index) % 2 == 1:
            color = (18, 23, 27)
        else:
            color = (245, 249, 250)
        pygame.draw.circle(screen, color, center, int(BOX_SIZE * 0.4))

    def initialize(self, screen):
        for x in range(self.size):
            u, v, w, t = (x * BOX_SIZE + BOARD_MARGIN, BOARD_MARGIN), \
                         (x * BOX_SIZE + BOARD_MARGIN, SCREEN_HEIGHT - BOARD_MARGIN), \
                         (BOARD_MARGIN, x * BOX_SIZE + BOARD_MARGIN), \
                         (SCREEN_HEIGHT - BOARD_MARGIN, x * BOX_SIZE + BOARD_MARGIN)
            pygame.draw.line(screen, (0, 0, 0), u, v)
            pygame.draw.line(screen, (0, 0, 0), w, t)
        pos = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        for (x, y) in pos:
            rect = (x * BOX_SIZE + BOARD_MARGIN - 2, y * BOX_SIZE + BOARD_MARGIN - 2, 6, 6)
            pygame.draw.rect(screen, (0, 0, 0), rect)
        for index, (x, y) in enumerate(self.chessList):
            self.draw_chess(screen, x, y, index)


class Button:
    def __init__(self, screen, x, y, text):
        self.screen = screen


class Gobang:
    def __init__(self, caption):
        pygame.init()
        self.screen = pygame.display.set_mode([800, 600])
        pygame.display.set_caption(caption)
        self.chessBoard = ChessBoard(MP_SIZE)

    def refresh(self):
        pygame.draw.rect(self.screen, (202, 152, 99), pygame.Rect(0, 0, 600, 600))
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(600, 0, 800, 600))
        self.chessBoard.initialize(self.screen)


chessGame = Gobang("Gobang")
while True:
    chessGame.refresh()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
