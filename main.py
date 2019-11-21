import pygame
import sys

MP_SIZE = 15
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
BOARD_MARGIN = 30
BOX_SIZE = (SCREEN_HEIGHT - 2 * BOARD_MARGIN) / (MP_SIZE - 1)
BUTTON_WIDTH = 40
BUTTON_HEIGHT = 20

assert (MP_SIZE % 2 == 1)


def get_pos(x):
    return x * BOX_SIZE + BOARD_MARGIN


def is_chessboard(mse_x, mse_y):
    if BOARD_MARGIN - BOX_SIZE * 0.4 <= mse_x <= SCREEN_HEIGHT - BOARD_MARGIN + BOX_SIZE * 0.4 and \
            BOARD_MARGIN - BOX_SIZE * 0.4 <= mse_y <= SCREEN_HEIGHT - BOARD_MARGIN + BOX_SIZE * 0.4:
        return True
    else:
        return False


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
        center = self.size // 2
        pos = [(center // 2, center // 2),
               (center // 2, center * 2 - center // 2),
               (center, center),
               (center * 2 - center // 2, center // 2),
               (center * 2 - center // 2, center * 2 - center // 2)]
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

    def put_chess(self, x, y):  # Just put chess on chessboard
        if len(self.chessList) > 0:
            u, v = self.chessList[len(self.chessList) - 1]
            self.board[x][y] = 3 - self.board[u][v]  # Black: 1; White: 2; Empty: 0
        else:
            self.board[x][y] = self.blackFirst
        self.chessList.append((x, y))

    def undo_chess(self):
        if len(self.chessList) > 0:
            u, v = self.chessList[len(self.chessList) - 1]
            self.chessList.pop(len(self.chessList) - 1)
            self.board[u][v] = 0


class Gobang:
    def __init__(self, caption):
        pygame.init()
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption(caption)
        self.chessBoard = ChessBoard(MP_SIZE)
        self.turn = True  # default: Player first
        self.AI = GobangAI(self.chessBoard)

    def refresh(self):
        pygame.draw.rect(self.screen, (202, 152, 99), pygame.Rect(0, 0, SCREEN_HEIGHT, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(SCREEN_HEIGHT, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.chessBoard.initialize(self.screen)

    def mouse_action(self, mse_x, mse_y):  # Mouse action IS player action, which has to boot GobangAI in the end
        if is_chessboard(mse_x, mse_y):
            if self.turn:
                x, y = self.chessBoard.get_chess_pos(mse_x, mse_y)
                if x >= 0 and self.chessBoard.board[x][y] == 0:
                    self.chessBoard.put_chess(x, y)
                    self.turn = False
                    self.opponent_action()

    def opponent_action(self):
        if not self.turn:
            u, v = self.chessBoard.chessList[len(self.chessBoard.chessList) - 1]
            x, y = self.AI.decide(3 - self.chessBoard.board[u][v])
            self.chessBoard.put_chess(x, y)
            self.turn = True

    def regret(self):
        if self.turn:
            for i in range(2):
                self.chessBoard.undo_chess()


class GobangAI:
    def __init__(self, chessBoard):
        self.chessBoard = chessBoard
        center = chessBoard.size // 2
        self.boxValue = [[(center - max(abs(x - center), abs(y - center)))
                          for x in range(chessBoard.size)]
                         for y in range(chessBoard.size)]  # initial weight, make sure AI searches from center
        self.vis = [[[False, False, False, False]
                     for x in range(chessBoard.size)]
                    for y in range(chessBoard.size)]  # whether visited before
        self.isDoubleTwo = [[[[False,  # **A**
                               False,  # *A*
                               False,  # *AA*
                               False]  # *-A-*
                              for direction in range(4)]
                             for x in range(chessBoard.size)]
                            for y in range(chessBoard.size)]
        self.SCORE_FIVE = 100
        self.SCORE_LIVE_FOUR = 90
        self.SCORE_DOUBLE_DEATH_FOUR = 90
        self.SCORE_DOUBLE_LIVE_THREE = 80
        self.SCORE_DEATH_FOUR_LIVE_THREE = 90
        self.SCORE_DEATH_THREE_LIVE_THREE = 70
        self.SCORE_DEATH_FOUR = 60
        self.SCORE_LIVE_THREE = 50
        self.SCORE_DOUBLE_LIVE_TWO = 40
        self.SCORE_DEATH_THREE = 30
        self.SCORE_LIVE_TWO = 20
        self.SCORE_DEATH_TWO = 10
        self.CHESS_FIVE = 1
        self.CHESS_LIVE_FOUR = 2
        self.CHESS_DEATH_FOUR = 3
        self.CHESS_LIVE_THREE = 4
        self.CHESS_DEATH_THREE = 5
        self.CHESS_LIVE_TWO = 6
        self.CHESS_DEATH_TWO = 7
        self.dir = [(0, 1), (1, -1), (1, 0), (1, 1)]

    def get_search_order(self):  # search from center
        orders = []
        for x in range(self.chessBoard.size):
            for y in range(self.chessBoard.size):
                if self.chessBoard.board[x][y] == 0:
                    orders.append((self.boxValue[x][y], x, y))
        orders.sort(reverse=True)
        return orders

    def decide(self, chessType):
        x, y = self.think(chessType)
        return x, y

    def think(self, chessType):
        chessAI = chessType
        chessPlayer = 3 - chessType
        orders = self.get_search_order()
        return orders[0][1], orders[0][2]

    def compute_chess_combination(self, chessAI, chessPlayer):
        chessCombination = [0 for x in range(8)]

        def inside_board(xx, yy):
            return 0 <= xx < self.chessBoard.size and 0 <= yy < self.chessBoard.size

        def is_ai(xx, yy):
            return self.chessBoard.board[xx][yy] == chessAI

        def is_player(xx, yy):
            return self.chessBoard.board[xx][yy] == chessPlayer

        def is_empty(xx, yy):
            return self.chessBoard.board[xx][yy] == 0

        def add_live_four():
            chessCombination[self.CHESS_LIVE_FOUR] += 1

        def add_death_four():
            chessCombination[self.CHESS_DEATH_FOUR] += 1

        def add_live_three():
            chessCombination[self.CHESS_LIVE_THREE] += 1

        def add_death_three():
            chessCombination[self.CHESS_DEATH_THREE] += 1

        def add_live_two():
            chessCombination[self.CHESS_LIVE_TWO] += 1

        def add_death_two():
            chessCombination[self.CHESS_DEATH_TWO] += 1

        def add_five():
            chessCombination[self.CHESS_FIVE] += 1

        for x in range(self.chessBoard.size):
            for y in range(self.chessBoard.size):
                for direction in range(4):
                    self.vis[x][y][direction] = False
        for x in range(self.chessBoard.size):
            for y in range(self.chessBoard.size):
                for direction in range(4):
                    for chessType in range(4):
                        self.isDoubleTwo[x][y][direction][chessType] = False

        for x in range(self.chessBoard.size):
            for y in range(self.chessBoard.size):
                if self.chessBoard.board[x][y] == 0:
                    continue
                for index, dir_x, dir_y in enumerate(self.dir):
                    if self.vis[x][y][index]:
                        continue
                    self.vis[x][y][index] = True
                    count, l_max, r_max, enemy = 1, 0, 0, 0
                    l_death, r_death = False, False
                    for i in range(4):
                        next_x = x + dir_x * i
                        next_y = y + dir_y * i
                        if inside_board(next_x, next_y):
                            if is_ai(next_x, next_y):
                                count += 1
                                l_max = i
                                self.vis[next_x][next_y][index] = True
                            else:
                                if is_player(next_x, next_y):
                                    enemy += 1
                                    l_death = True
                                break
                        else:
                            enemy += 1
                            l_death = True
                            break
                    for i in range(4):
                        next_x = x - dir_x * i
                        next_y = y - dir_y * i
                        if inside_board(next_x, next_y):
                            if is_ai(next_x, next_y):
                                count += 1
                                r_max = i
                                self.vis[next_x][next_y][index] = True
                            else:
                                if is_player(next_x, next_y):
                                    enemy += 1
                                    r_death = True
                                break
                        else:
                            enemy += 1
                            r_death = True
                            break
                    if count >= 5:  # *****
                        add_five()
                    elif enemy == 2:  # Since then, only one or zero enemies left
                        continue
                    elif count == 4:
                        if enemy == 0:  # -****-
                            add_live_four()
                        else:  # -****^
                            add_death_four()
                    elif count == 3:
                        if enemy == 0:
                            next_x = x + dir_x * (l_max + 2)
                            next_y = y + dir_y * (l_max + 2)
                            enemy_far = 0
                            if inside_board(next_x, next_y):
                                if is_ai(next_x, next_y):  # *-***-
                                    add_death_four()
                                elif is_player(next_x, next_y):  # ^-***-
                                    enemy_far += 1
                            else:  # ^-***-
                                enemy_far += 1
                            next_x = x - dir_x * (r_max + 2)
                            next_y = y - dir_y * (r_max + 2)
                            if inside_board(next_x, next_y):
                                if is_ai(next_x, next_y):  # -***-*
                                    add_death_four()
                                elif is_player(next_x, next_y):  # -***-^
                                    enemy_far += 1
                            else:  # -***-^
                                enemy_far += 1
                            if enemy_far == 2:  # ^-***-^
                                add_death_three()
                            else:  # -***-
                                add_live_three()
                        else:  # enemy is 1
                            if l_death:  # ^***-
                                next_x = x - dir_x * (r_max + 2)
                                next_y = y - dir_y * (r_max + 2)
                                if inside_board(next_x, next_y):
                                    if is_ai(next_x, next_y):  # ^***-*
                                        add_death_four()
                                    elif is_empty(next_x, next_y):  # ^***--
                                        add_death_three()
                            elif r_death:  # -***^
                                next_x = x + dir_x * (l_max + 2)
                                next_y = y + dir_y * (l_max + 2)
                                if inside_board(next_x, next_y):
                                    if is_ai(next_x, next_y):  # *-***^
                                        add_death_four()
                                    elif is_empty(next_x, next_y):  # --***^
                                        add_death_three()
                    elif count == 2:
                        if enemy == 0:  # -**-
                            enemy_far = 0
                            empty = 0
                            next_x = x + dir_x * (l_max + 2)
                            next_y = y + dir_y * (l_max + 2)
                            if inside_board(next_x, next_y):
                                if is_ai(next_x, next_y):  # ?*-**-
                                    next_xx = x + dir_x * (l_max + 3)
                                    next_yy = y + dir_y * (l_max + 3)
                                    if inside_board(next_xx, next_yy):
                                        if is_ai(next_xx, next_yy):  # **-**-
                                            if not self.isDoubleTwo[next_x - dir_x][next_y - dir_y][index][0]:
                                                add_death_four()
                                                self.isDoubleTwo[next_x - dir_x][next_y - dir_y][index][0] = True
                                        elif is_player(next_xx, next_yy):  # ^*-**-
                                            add_death_three()
                                        else:  # -*-**-
                                            add_live_three()
                                    else:  # ^*-**-
                                        add_death_three()
                                elif is_player(next_x, next_y):  # ^-**-
                                    enemy_far += 1
                                else:  # ?--**-
                                    next_xx = x + dir_x * (l_max + 3)
                                    next_yy = y + dir_y * (l_max + 3)
                                    if inside_board(next_xx, next_yy):
                                        if is_ai(next_xx, next_yy):  # *--**-
                                            add_death_three()
                                        else:
                                            empty += 1
                                    else:
                                        empty += 1
                            else:  # ^-**-
                                enemy_far += 1
                            next_x = x - dir_x * (r_max + 2)
                            next_y = y - dir_y * (r_max + 2)
                            if inside_board(next_x, next_y):
                                if is_ai(next_x, next_y):  # -**-*?
                                    next_xx = x - dir_x * (r_max + 3)
                                    next_yy = y - dir_y * (r_max + 3)
                                    if inside_board(next_xx, next_yy):
                                        if is_ai(next_xx, next_yy):  # -**-**
                                            if not self.isDoubleTwo[next_x + dir_x][next_y + dir_y][index][0]:
                                                add_death_four()
                                                self.isDoubleTwo[next_x - dir_x][next_y - dir_y][index][0] = True
                                        elif is_player(next_xx, next_yy):  # -**-*^
                                            add_death_three()
                                        else:  # -**-*-
                                            add_live_three()
                                    else:  # -**-*^
                                        add_death_three()
                                elif is_player(next_x, next_y):  # -**-^
                                    enemy_far += 1
                                else:  # -**--?
                                    next_xx = x - dir_x * (r_max + 3)
                                    next_yy = y - dir_y * (r_max + 3)
                                    if inside_board(next_xx, next_yy):
                                        if is_ai(next_xx, next_yy):  # -**--*
                                            add_death_three()
                                        else:
                                            empty += 1
                                    else:
                                        empty += 1
                            else:  # -**-^
                                enemy_far += 1
                            if enemy_far == 2:  # ^-**-^
                                continue
                            elif empty == 2:  # n--**--n
                                add_live_two()
                        else:
                            if l_death:  # ^**-
                                next_x = x - dir_x * (r_max + 2)
                                next_y = y - dir_y * (r_max + 2)
                                if inside_board(next_x, next_y):
                                    if is_ai(next_x, next_y):  # ^**-*?
                                        next_xx = x - dir_x * (r_max + 3)
                                        next_yy = y - dir_y * (r_max + 3)
                                        if inside_board(next_xx, next_yy):
                                            if is_ai(next_xx, next_yy):  # ^**-**
                                                if not self.isDoubleTwo[next_x + dir_x][next_y + dir_y][index][0]:
                                                    add_death_four()
                                                    self.isDoubleTwo[next_x - dir_x][next_y - dir_y][index][0] = True
                                            elif is_player(next_xx, next_yy):  # ^**-*^
                                                continue
                                            else:  # ^**-*-
                                                add_death_three()
                                        else:  # ^**-*^
                                            continue
                                    elif is_player(next_x, next_y):  # ^**-^
                                        continue
                                    else:  # ^**--?
                                        next_xx = x - dir_x * (r_max + 3)
                                        next_yy = y - dir_y * (r_max + 3)
                                        if inside_board(next_xx, next_yy):
                                            if is_ai(next_xx, next_yy):  # ^**--*
                                                add_death_three()
                                            elif is_player(next_xx, next_yy):  # ^**--^
                                                continue
                                            else:  # ^**---
                                                add_death_two()
                                        else:  # ^**--^
                                            continue
                                else:  # ^**-^
                                    continue
                            elif r_death:  # ?-**^
                                next_x = x + dir_x * (l_max + 2)
                                next_y = y + dir_y * (l_max + 2)
                                if inside_board(next_x, next_y):
                                    if is_ai(next_x, next_y):  # ?*-**^
                                        next_xx = x + dir_x * (l_max + 3)
                                        next_yy = y + dir_y * (l_max + 3)
                                        if inside_board(next_xx, next_yy):
                                            if is_ai(next_xx, next_yy):  # **-**^
                                                if not self.isDoubleTwo[next_x - dir_x][next_y - dir_y][index][0]:
                                                    add_death_four()
                                                    self.isDoubleTwo[next_x - dir_x][next_y - dir_y][index][0] = True
                                            elif is_player(next_xx, next_yy):  # ^*-**^
                                                continue
                                            else:  # -*-**^
                                                add_death_three()
                                        else:  # ^*-**^
                                            continue
                                    elif is_player(next_x, next_y):  # ^-**^
                                        continue
                                    else:  # ?--**^
                                        next_xx = x - dir_x * (r_max + 3)
                                        next_yy = y - dir_y * (r_max + 3)
                                        if inside_board(next_xx, next_yy):
                                            if is_ai(next_xx, next_yy):  # *--**^
                                                add_death_three()
                                            elif is_player(next_xx, next_yy):  # ^--**^
                                                continue
                                            else:  # ---**^
                                                add_death_two()
                                        else:  # ^--**^
                                            continue
                                else:  # ^-**^
                                    continue
                    elif count == 1:
                        if enemy == 0:  # -*-
                            next_x = x + dir_x * (l_max + 2)
                            next_y = y + dir_y * (l_max + 2)
                            if inside_board(next_x, next_y):
                                if is_ai(next_x, next_y):  # ?*-*-
                                    next_xx = x + dir_x * (l_max + 3)
                                    next_yy = y + dir_y * (l_max + 3)
                                    if inside_board(next_xx, next_yy):
                                        if is_empty(next_xx, next_yy):  # -*-*-
                                            if not self.isDoubleTwo[next_x - dir_x][next_y - dir_y][index][1]:
                                                self.isDoubleTwo[next_x - dir_x][next_y - dir_y][index][1] = True
                                                add_live_two()
                                    next_xx = x - dir_x * (r_max + 2)
                                    next_yy = y - dir_y * (r_max + 2)
                                    if inside_board(next_xx, next_yy):
                                        if is_ai(next_xx, next_yy):  # *-*-*
                                            chessCombination[self.CHESS_DEATH_THREE] += 1
                                elif is_empty(next_x, next_y):  # ?--*-
                                    next_xx = x + dir_x * (l_max + 3)
                                    next_yy = y + dir_y * (l_max + 3)
                                    if inside_board(next_xx, next_yy):
                                        if is_ai(next_xx, next_yy):  # ?*--*-
                                            next_xxx = x + dir_x * (l_max + 4)
                                            next_yyy = y + dir_y * (l_max + 4)
                                            if inside_board(next_xxx, next_yyy) and is_empty(next_xxx,
                                                                                             next_yyy):  # -*--*-
                                                if not self.isDoubleTwo[next_x][next_y][index][2]:
                                                    self.isDoubleTwo[next_x][next_y][index][2] = True
                                                    self.isDoubleTwo[next_x - dir_x][next_y - dir_y][index][2] = True
                                                    add_live_two()
                                        elif is_empty(next_xx, next_yy):  # ?---*-
                                            next_xxx = x + dir_x * (l_max + 4)
                                            next_yyy = y + dir_y * (l_max + 4)
                                            if inside_board(next_xxx, next_yyy):
                                                if is_ai(next_xxx, next_yyy):  # *---*-
                                                    if not self.isDoubleTwo[next_x][next_y][index][3]:
                                                        self.isDoubleTwo[next_x][next_y][index][3] = True
                                                        add_death_two()
                            next_x = x - dir_x * (r_max + 2)
                            next_y = y - dir_y * (r_max + 2)
                            if inside_board(next_x, next_y):
                                if is_ai(next_x, next_y):  # -*-*?
                                    next_xx = x - dir_x * (r_max + 3)
                                    next_yy = y - dir_y * (r_max + 3)
                                    if inside_board(next_xx, next_yy):
                                        if is_empty(next_xx, next_yy):  # -*-*-
                                            if not self.isDoubleTwo[next_x + dir_x][next_y + dir_y][index][1]:
                                                self.isDoubleTwo[next_x + dir_x][next_y + dir_y][index][1] = True
                                                add_live_two()
                                elif is_empty(next_x, next_y):  # -*--?
                                    next_xx = x - dir_x * (r_max + 3)
                                    next_yy = y - dir_y * (r_max + 3)
                                    if inside_board(next_xx, next_yy):
                                        if is_ai(next_xx, next_yy):  # -*--*?
                                            next_xxx = x - dir_x * (r_max + 4)
                                            next_yyy = y - dir_y * (r_max + 4)
                                            if inside_board(next_xxx, next_yyy) and is_empty(next_xxx,
                                                                                             next_yyy):  # -*--*-
                                                if not self.isDoubleTwo[next_x][next_y][index][2]:
                                                    self.isDoubleTwo[next_x][next_y][index][2] = True
                                                    self.isDoubleTwo[next_x + dir_x][next_y + dir_y][index][2] = True
                                                    add_live_two()
                                        elif is_empty(next_xx, next_yy):  # -*---?
                                            next_xxx = x - dir_x * (r_max + 4)
                                            next_yyy = y - dir_y * (r_max + 4)
                                            if inside_board(next_xxx, next_yyy):
                                                if is_ai(next_xxx, next_yyy):  # -*---*
                                                    if not self.isDoubleTwo[next_x][next_y][index][3]:
                                                        self.isDoubleTwo[next_x][next_y][index][3] = True
                                                        add_death_two()
                        else:
                            if l_death:  # ^*-?
                                next_x = x - dir_x * (r_max + 2)
                                next_y = y - dir_y * (r_max + 2)
                                next_xx = x - dir_x * (r_max + 3)
                                next_yy = y - dir_y * (r_max + 3)
                                next_xxx = x - dir_x * (r_max + 4)
                                next_yyy = y - dir_y * (r_max + 4)
                                if inside_board(next_xxx, next_yyy):
                                    if is_ai(next_x, next_y) \
                                            and is_empty(next_xx, next_yy) \
                                            and is_empty(next_xxx, next_yyy):  # ^*-*--
                                        if not self.isDoubleTwo[next_x + dir_x][next_y + dir_y][index][1]:
                                            self.isDoubleTwo[next_x + dir_x][next_y + dir_y][index][1] = True
                                            add_death_two()
                                    elif is_empty(next_x, next_y) \
                                            and is_ai(next_xx, next_yy) \
                                            and is_empty(next_xxx, next_yyy):  # ^*--*-
                                        if not self.isDoubleTwo[next_x][next_y][index][2]:
                                            self.isDoubleTwo[next_x][next_y][index][2] = True
                                            self.isDoubleTwo[next_x + dir_x][next_y + dir_y][index][2] = True
                                            add_death_two()
                                    elif is_empty(next_x, next_y) \
                                            and is_empty(next_xx, next_yy) \
                                            and is_ai(next_xxx, next_yyy):  # ^*---*
                                        if not self.isDoubleTwo[next_x][next_y][index][3]:
                                            self.isDoubleTwo[next_x][next_y][index][3] = True
                                            add_death_two()
                            elif r_death:  # ?-*^
                                next_x = x + dir_x * (l_max + 2)
                                next_y = y + dir_y * (l_max + 2)
                                next_xx = x + dir_x * (l_max + 3)
                                next_yy = y + dir_y * (l_max + 3)
                                next_xxx = x + dir_x * (l_max + 4)
                                next_yyy = y + dir_y * (l_max + 4)
                                if inside_board(next_xxx, next_yyy):
                                    if is_ai(next_x, next_y) \
                                            and is_empty(next_xx, next_yy) \
                                            and is_empty(next_xxx, next_yyy):  # --*-*^
                                        if not self.isDoubleTwo[next_x - dir_x][next_y - dir_y][index][1]:
                                            self.isDoubleTwo[next_x - dir_x][next_y - dir_y][index][1] = True
                                            add_death_two()
                                    elif is_empty(next_x, next_y) \
                                            and is_ai(next_xx, next_yy) \
                                            and is_empty(next_xxx, next_yyy):  # -*--*^
                                        if not self.isDoubleTwo[next_x][next_y][index][2]:
                                            self.isDoubleTwo[next_x][next_y][index][2] = True
                                            self.isDoubleTwo[next_x - dir_x][next_y - dir_y][index][2] = True
                                            add_death_two()
                                    elif is_empty(next_x, next_y) \
                                            and is_empty(next_xx, next_yy) \
                                            and is_ai(next_xxx, next_yyy):  # *---*^
                                        if not self.isDoubleTwo[next_x][next_y][index][3]:
                                            self.isDoubleTwo[next_x][next_y][index][3] = True
                                            add_death_two()
        return chessCombination


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
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                chessGame.regret()
            elif event.key == pygame.K_ESCAPE:
                sys.exit()
