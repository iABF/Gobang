import pygame
import sys
import random

MP_SIZE = 15
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
BOARD_MARGIN = 30
BOX_SIZE = (SCREEN_HEIGHT - 2 * BOARD_MARGIN) / (MP_SIZE - 1)
BUTTON_HEIGHT = 100
BUTTON_WIDTH = 500
SEARCH_DEPTH = 3

assert (MP_SIZE % 2 == 1)


def get_pos(x):
    return x * BOX_SIZE + BOARD_MARGIN


def is_chessboard(mse_x, mse_y):
    if BOARD_MARGIN - BOX_SIZE * 0.4 <= mse_x <= SCREEN_HEIGHT - BOARD_MARGIN + BOX_SIZE * 0.4 and \
            BOARD_MARGIN - BOX_SIZE * 0.4 <= mse_y <= SCREEN_HEIGHT - BOARD_MARGIN + BOX_SIZE * 0.4:
        return True
    else:
        return False


def get_button(mse_x, mse_y):
    if SCREEN_HEIGHT / 2 - BUTTON_WIDTH / 2 <= mse_x <= SCREEN_HEIGHT / 2 + BUTTON_WIDTH / 2 and \
            SCREEN_HEIGHT / 4 - BUTTON_HEIGHT / 2 <= mse_y <= SCREEN_HEIGHT / 4 + BUTTON_HEIGHT / 2:
        return 1
    if SCREEN_HEIGHT / 2 - BUTTON_WIDTH / 2 <= mse_x <= SCREEN_HEIGHT / 2 + BUTTON_WIDTH / 2 and \
            (SCREEN_HEIGHT * 3) / 4 - BUTTON_HEIGHT / 2 <= mse_y <= (SCREEN_HEIGHT * 3) / 4 + BUTTON_HEIGHT / 2:
        return 2
    return 0


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
        self.isStart = False
        self.isEnd = False

    def refresh(self):
        pygame.draw.rect(self.screen, (202, 152, 99), pygame.Rect(0, 0, SCREEN_HEIGHT, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(SCREEN_HEIGHT, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.isStart:
            self.chessBoard.initialize(self.screen)
            pygame.display.update()
        else:
            aiRect = pygame.Rect(SCREEN_HEIGHT / 2 - BUTTON_WIDTH / 2,
                                 SCREEN_HEIGHT / 4 - BUTTON_HEIGHT / 2,
                                 BUTTON_WIDTH,
                                 BUTTON_HEIGHT)
            playerRect = pygame.Rect(SCREEN_HEIGHT / 2 - BUTTON_WIDTH / 2,
                                     (SCREEN_HEIGHT * 3) / 4 - BUTTON_HEIGHT / 2,
                                     BUTTON_WIDTH,
                                     BUTTON_HEIGHT)
            aiText = pygame.font.SysFont("Arial", BUTTON_HEIGHT // 2, True) \
                .render("AI FIRST", True, (255, 255, 255))
            aiTextRect = aiText.get_rect()
            playerText = pygame.font.SysFont("Arial", BUTTON_HEIGHT // 2, True) \
                .render("PLAYER FIRST", True, (255, 255, 255))
            playerTextRect = playerText.get_rect()
            aiTextRect.center = aiRect.center
            playerTextRect.center = playerRect.center
            self.screen.fill((255, 0, 0), aiRect)
            self.screen.fill((255, 0, 0), playerRect)
            self.screen.blit(aiText, aiTextRect)
            self.screen.blit(playerText, playerTextRect)
            pygame.display.update()

    def mouse_action(self, mse_x, mse_y):  # Mouse action IS player action, which has to boot GobangAI in the end
        if self.isStart:
            if is_chessboard(mse_x, mse_y):
                if self.turn:
                    x, y = self.chessBoard.get_chess_pos(mse_x, mse_y)
                    if x >= 0 and self.chessBoard.board[x][y] == 0:
                        self.chessBoard.put_chess(x, y)
                        self.turn = False
                        self.refresh()
                        u, v = self.chessBoard.chessList[len(self.chessBoard.chessList) - 1]
                        chessType = self.chessBoard.board[u][v]
                        if self.AI.compute_chess_combination(chessType, 3 - chessType, True):
                            print("You win.")
                            pygame.display.set_caption("You win. Click to start new game.")
                            self.isEnd = True
                        self.opponent_action()
        else:
            buttonId = get_button(mse_x, mse_y)
            if buttonId == 1:
                pygame.display.set_caption("AI FIRST")
                self.isStart = True
                self.turn = False
                self.refresh()
                self.opponent_action()
            elif buttonId == 2:
                pygame.display.set_caption("PLAYER FIRST")
                self.isStart = True

    def opponent_action(self):
        if not self.turn:
            if len(self.chessBoard.chessList) > 0:
                u, v = self.chessBoard.chessList[len(self.chessBoard.chessList) - 1]
                x, y = self.AI.decide(3 - self.chessBoard.board[u][v])
                chessType = 3 - self.chessBoard.board[u][v]
            else:
                x, y = random.randint(self.chessBoard.size // 2 - 1, self.chessBoard.size // 2 + 1),\
                       random.randint(self.chessBoard.size // 2 - 1, self.chessBoard.size // 2 + 1)
                chessType = 1
            self.chessBoard.put_chess(x, y)
            if self.AI.compute_chess_combination(chessType, 3 - chessType, True):
                print("Computer win.")
                pygame.display.set_caption("Computer win. Click to start new game.")
                self.isEnd = True
            self.turn = True

    def regret(self):
        if self.turn:
            for i in range(2):
                self.chessBoard.undo_chess()


class GobangAI:
    def __init__(self, chessBoard):
        self.chessBoard = chessBoard
        center = chessBoard.size // 2
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
        self.CHESS_FIVE = 1
        self.CHESS_LIVE_FOUR = 2
        self.CHESS_DEATH_FOUR = 3
        self.CHESS_LIVE_THREE = 4
        self.CHESS_DEATH_THREE = 5
        self.CHESS_LIVE_TWO = 6
        self.CHESS_DEATH_TWO = 7
        self.dir = [(0, 1), (1, -1), (1, 0), (1, 1)]
        self.position = None

    # check if position (x, y) is in a game area of radius r
    def in_group(self, x, y, r):
        for i in range(max(x - r, 0), min(x + r, self.chessBoard.size - 1) + 1):
            for j in range(max(y - r, 0), min(y + r, self.chessBoard.size - 1) + 1):
                if self.chessBoard.board[i][j] != 0 and (i, j) != (x, y):
                    return True
        return False

    # if easy position exists, just search these positions
    def get_search_order(self, chessAI, chessPlayer):  # search from center
        orders = []
        greatOrder = [[] for x in range(8)]
        for x in range(self.chessBoard.size):
            for y in range(self.chessBoard.size):
                if self.chessBoard.board[x][y] == 0 and self.in_group(x, y, 2):
                    aiScore, playerScore = self.pre_get_score(x, y, chessAI, chessPlayer)
                    position = (max(aiScore, playerScore), x, y)
                    if aiScore >= 100000 or playerScore >= 100000:
                        greatOrder[0].append(position)
                    elif aiScore >= 10000:
                        greatOrder[1].append(position)
                    elif playerScore >= 10000:
                        greatOrder[2].append(position)
                    elif aiScore >= 1000:
                        greatOrder[3].append(position)
                    orders.append(position)
        for i in range(2):
            if len(greatOrder[i]) > 0:
                return greatOrder[i]
        if len(greatOrder[2]) > 0:
            if len(greatOrder[3]) > 0:
                return greatOrder[2] + greatOrder[3]
            return greatOrder[2]
        orders.sort(reverse=True)
        return orders

    # before AI starts searching, check if easy position exists
    def pre_get_score(self, x, y, chessAI, chessPlayer):
        chessCombination = [[0 for x in range(8)] for y in range(2)]
        self.chessBoard.board[x][y] = chessAI
        self.compute_one_side_combination(chessAI, chessPlayer, chessCombination, x, y)
        self.chessBoard.board[x][y] = chessPlayer
        self.compute_one_side_combination(chessPlayer, chessAI, chessCombination, x, y)
        self.chessBoard.board[x][y] = 0
        aiScore, playerScore =\
            self.compute_simple_score(chessCombination[chessAI - 1]),\
            self.compute_simple_score(chessCombination[chessPlayer - 1])
        return aiScore, playerScore

    # AI decides, posting result to Gobang Game
    def decide(self, chessType):
        score, x, y = self.think(chessType)
        return x, y

    # how AI make its choice
    def think(self, chessType, depth=SEARCH_DEPTH):
        self.position = None
        score = self.max_min_search(chessType, depth, depth)
        x, y = self.position
        return score, x, y

    # max_min search allows multi-depth thinking
    def max_min_search(self, chessAI, depth, maxDepth, alpha=-0x7fffffff, beta=0x7fffffff):
        chessPlayer = 3 - chessAI
        score = self.get_score(chessAI, chessPlayer)
        if depth <= 0 or abs(score) >= 10000:
            return score
        position = None
        orders = self.get_search_order(chessAI, chessPlayer)
        if len(orders) == 0:
            return score
        for weight, x, y in orders:
            self.chessBoard.board[x][y] = chessAI
            score = -self.max_min_search(chessPlayer, depth - 1, maxDepth, -beta, -alpha)
            self.chessBoard.board[x][y] = 0
            if score > alpha:
                alpha = score
                position = (x, y)
                if alpha >= beta:
                    break
        if depth == maxDepth and position:
            self.position = position
        return alpha

    # compute both side chess combination
    def compute_chess_combination(self, chessAI, chessPlayer, checkWin=False):
        chessCombination = [[0 for x in range(8)] for y in range(2)]
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
                if self.chessBoard.board[x][y] == chessAI:
                    self.compute_one_side_combination(chessAI, chessPlayer, chessCombination, x, y)
                elif self.chessBoard.board[x][y] == chessPlayer:
                    self.compute_one_side_combination(chessPlayer, chessAI, chessCombination, x, y)

        if checkWin:
            aiScore, playerScore = self.compute_score(chessCombination[0], chessCombination[1])
            score = aiScore - playerScore
            print('Black side point: ' + str(score))
            return chessCombination[chessAI - 1][self.CHESS_FIVE] > 0
        return chessCombination

    # compute one chess side chess combination
    def compute_one_side_combination(self, chessAI, chessPlayer, chessCombination, x, y):
        def inside_board(xx, yy):
            return 0 <= xx < self.chessBoard.size and 0 <= yy < self.chessBoard.size

        def is_ai(xx, yy):
            return self.chessBoard.board[xx][yy] == chessAI

        def is_player(xx, yy):
            return self.chessBoard.board[xx][yy] == chessPlayer

        def is_empty(xx, yy):
            return self.chessBoard.board[xx][yy] == 0

        def add_live_four():
            chessCombination[chessAI - 1][self.CHESS_LIVE_FOUR] += 1

        def add_death_four():
            chessCombination[chessAI - 1][self.CHESS_DEATH_FOUR] += 1

        def add_live_three():
            chessCombination[chessAI - 1][self.CHESS_LIVE_THREE] += 1

        def add_death_three():
            chessCombination[chessAI - 1][self.CHESS_DEATH_THREE] += 1

        def add_live_two():
            chessCombination[chessAI - 1][self.CHESS_LIVE_TWO] += 1

        def add_death_two():
            chessCombination[chessAI - 1][self.CHESS_DEATH_TWO] += 1

        def add_five():
            chessCombination[chessAI - 1][self.CHESS_FIVE] += 1

        for index, (dir_x, dir_y) in enumerate(self.dir):
            if self.vis[x][y][index]:
                continue
            self.vis[x][y][index] = True
            count, l_max, r_max, enemy = 1, 0, 0, 0
            l_death, r_death = False, False
            for i in range(1, 5):
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
            for i in range(1, 5):
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
                                    add_death_three()
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

    # compute ai score and player score
    def compute_score(self, ai_combination, player_combination):
        ai_score, player_score = 0, 0
        if ai_combination[self.CHESS_FIVE] > 0:
            return 100000, 0
        if player_combination[self.CHESS_FIVE] > 0:
            return 0, 100000
        if ai_combination[self.CHESS_LIVE_FOUR] + ai_combination[self.CHESS_DEATH_FOUR] // 2 > 0:
            return 9050, 0
        if ai_combination[self.CHESS_DEATH_FOUR] > 0:
            return 9040, 0
        if player_combination[self.CHESS_LIVE_FOUR] + player_combination[self.CHESS_DEATH_FOUR] // 2 > 0:
            return 0, 9030
        if player_combination[self.CHESS_DEATH_FOUR] > 0 and player_combination[self.CHESS_LIVE_THREE] > 0:
            return 0, 9020
        if ai_combination[self.CHESS_LIVE_THREE] > 0 and player_combination[self.CHESS_DEATH_FOUR] == 0:
            return 9010, 0
        if player_combination[self.CHESS_LIVE_THREE] > 1 \
                and ai_combination[self.CHESS_LIVE_THREE] == 0 \
                and ai_combination[self.CHESS_DEATH_THREE] == 0:
            return 0, 9000

        if player_combination[self.CHESS_DEATH_FOUR] > 0:
            player_score += 400

        if ai_combination[self.CHESS_LIVE_THREE] > 1:
            ai_score += 500
        elif ai_combination[self.CHESS_LIVE_THREE] > 0:
            ai_score += 100

        if player_combination[self.CHESS_LIVE_THREE] > 1:
            player_score += 2000
        elif player_combination[self.CHESS_LIVE_THREE] > 0:
            player_score += 400

        ai_score += ai_combination[self.CHESS_DEATH_THREE] * 10
        player_score += player_combination[self.CHESS_DEATH_THREE] * 10
        ai_score += ai_combination[self.CHESS_LIVE_TWO] * 6
        player_score += player_combination[self.CHESS_LIVE_TWO] * 6
        ai_score += ai_combination[self.CHESS_DEATH_TWO] * 2
        player_score += player_combination[self.CHESS_DEATH_TWO] * 2

        return ai_score, player_score

    # return a score: aiScore - playerScore
    def get_score(self, chessAI, chessPlayer):
        chessCombination = self.compute_chess_combination(chessAI, chessPlayer)
        ai_combination, player_combination = chessCombination[chessAI - 1], chessCombination[chessPlayer - 1]
        ai_score, player_score = self.compute_score(ai_combination, player_combination)
        score = ai_score - player_score
        return score

    # just compute score for easy position before search
    def compute_simple_score(self, chessCombination):
        score = 0
        if chessCombination[self.CHESS_FIVE] > 0:
            return 100000
        if chessCombination[self.CHESS_LIVE_FOUR] > 0:
            return 10000
        if chessCombination[self.CHESS_DEATH_FOUR] > 1 or \
                (chessCombination[self.CHESS_DEATH_FOUR] == 1 and chessCombination[self.CHESS_LIVE_THREE] > 0):
            score += chessCombination[self.CHESS_DEATH_FOUR] * 1000
        elif chessCombination[self.CHESS_DEATH_FOUR] == 1:
            score += 100
        if chessCombination[self.CHESS_LIVE_THREE] > 1:
            score += 500
        elif chessCombination[self.CHESS_LIVE_THREE] == 1:
            score += 100
        score += chessCombination[self.CHESS_DEATH_THREE] * 10
        score += chessCombination[self.CHESS_LIVE_TWO] * 8
        score += chessCombination[self.CHESS_DEATH_TWO] * 2
        return score


if __name__ == '__main__':
    chessGame = Gobang("Gobang [DIFFICULTY: " + str(SEARCH_DEPTH) + "]")
    while True:
        chessGame.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if chessGame.isEnd:
                    chessGame = Gobang("Gobang [DIFFICULTY: " + str(SEARCH_DEPTH) + "]")
                    chessGame.refresh()
                else:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    chessGame.mouse_action(mouse_x, mouse_y)
            elif event.type == pygame.KEYDOWN:
                if chessGame.isEnd:
                    continue
                if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    chessGame.regret()
                elif event.key == pygame.K_ESCAPE:
                    sys.exit()
