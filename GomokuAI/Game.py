import GameMap
from Button import *
import Menu
from pygame import mixer
import sys

bg_game = pygame.image.load("gmbg.png")


class StartButton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(26, 173, 25), (158, 217, 157)], True)

    def click(self, game):
        if self.enable:
            game.start()
            game.winner = None
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False

    def unclick(self):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True


class GiveupButton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(230, 67, 64), (236, 139, 137)], False)

    def click(self, game):
        if self.enable:
            game.is_play = False
            if game.winner is None:
                game.winner = game.map.reverseTurn(game.player)
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False

    def unclick(self):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True


class SoundButton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(33, 97, 140), (93, 173, 226)], False)

    def click(self, game):
        if self.enable:
            mixer.music.unpause()
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False

    def unclick(self):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True


class SoundButton1(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(33, 97, 140), (93, 173, 226)], True)

    def click(self, game):
        if self.enable:
            mixer.music.pause()
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False

    def unclick(self):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True


class Game:

    def __init__(self, caption):
        pygame.init()
        mixer.music.play(-1)
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.buttons = []
        self.buttons.append(StartButton(self.screen, 'Start', MAP_WIDTH + 30, 15))
        self.buttons.append(GiveupButton(self.screen, 'Giveup', MAP_WIDTH + 30, BUTTON_HEIGHT + 45))
        self.buttons.append(SoundButton(self.screen, 'Play', MAP_WIDTH + 30, BUTTON_HEIGHT + 125))
        self.buttons.append(SoundButton1(self.screen, 'Pause', MAP_WIDTH + 30, BUTTON_HEIGHT + 205))
        self.is_play = False

        self.map = Map(CHESS_LEN, CHESS_LEN)
        self.player = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
        self.action = None
        self.AI = ChessAI(CHESS_LEN)
        self.winner = None
        # part one
        self.DISPLAY_W, self.DISPLAY_H = GameMap.SCREEN_WIDTH, GameMap.SCREEN_HEIGHT
        self.display = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
        self.window = pygame.display.set_mode((self.DISPLAY_W, self.DISPLAY_H))
        self.font_name = '8-BIT WONDER.TTF'
        self.BLACK, self.WHITE = (0, 0, 0), (255, 255, 255)

    def start(self):
        self.is_play = True
        Color1 = Menu.checkcolor()
        self.player = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
        self.player = MAP_ENTRY_TYPE.MAP_PLAYER_TWO
        if Color1 == "Black":
            self.useAI = False
        else:
            self.useAI = True

        self.map.reset()

    def play(self):
        self.clock.tick(60)

        light_yellow = (247, 238, 214)
        pygame.draw.rect(self.screen, light_yellow, pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(MAP_WIDTH, 0, INFO_WIDTH, SCREEN_HEIGHT))
        self.map.drawBackground(self.screen)

        for button in self.buttons:
            button.draw()
        if self.is_play and not self.isOver():
            if self.useAI:
                x, y = self.AI.findBestChess(self.map.map, self.player)
                effectSound = mixer.Sound('drop.wav')
                effectSound.play()
                self.checkClick(x, y, True)
                self.useAI = False

            if self.action is not None:
                self.checkClick(self.action[0], self.action[1])
                self.action = None

            if not self.isOver():
                self.changeMouseShow()

        if self.isOver():
            self.showWinner()

        self.map.drawChess(self.screen)

    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.BLACK)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display.blit(text_surface, text_rect)

    def changeMouseShow(self):
        map_x, map_y = pygame.mouse.get_pos()
        x, y = self.map.MapPosToIndex(map_x, map_y)
        if self.map.isInMap(map_x, map_y) and self.map.isEmpty(x, y):
            pygame.mouse.set_visible(False)
            light_red = (213, 90, 107)
            pos, radius = (map_x, map_y), CHESS_RADIUS
            pygame.draw.circle(self.screen, light_red, pos, radius)
        else:
            pygame.mouse.set_visible(True)

    def checkClick(self, x, y, isAI=False):
        self.map.click(x, y, self.player)
        if self.AI.isWin(self.map.map, self.player):
            self.winner = self.player
            self.click_button(self.buttons[1])
        else:
            self.player = self.map.reverseTurn(self.player)
            if not isAI:
                self.useAI = True

    def mouseClick(self, map_x, map_y):
        if self.is_play and self.map.isInMap(map_x, map_y) and not self.isOver():
            x, y = self.map.MapPosToIndex(map_x, map_y)
            if self.map.isEmpty(x, y):
                effectSound = mixer.Sound('drop.wav')
                effectSound.play()
                self.action = (x, y)

    def isOver(self):
        return self.winner is not None

    def showWinner(self):
        Color1 = Menu.checkcolor()
        if Color1 == "White":
            if self.winner == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
                self.map.reset()
                self.display.fill(self.BLACK)
                self.display.blit(bg_game, (0, 0))
                self.draw_text('Thanks for Playing', 20, self.DISPLAY_W / 2, self.DISPLAY_H / 2)
                self.draw_text('Winner is White', 20, self.DISPLAY_W / 2, self.DISPLAY_H / 2 + 30)
                self.window.blit(self.display, (0, 0))
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            sys.exit(0)
            else:
                self.map.reset()
                self.display.fill(self.BLACK)
                self.display.blit(bg_game, (0, 0))
                self.draw_text('Thanks for Playing', 20, self.DISPLAY_W / 2, self.DISPLAY_H / 2)
                self.draw_text('Winner is Black', 20, self.DISPLAY_W / 2, self.DISPLAY_H / 2 + 30)
                self.window.blit(self.display, (0, 0))
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            sys.exit(0)
        else:
            if self.winner == MAP_ENTRY_TYPE.MAP_PLAYER_TWO:
                self.map.reset()
                self.display.fill(self.BLACK)
                self.display.blit(bg_game, (0, 0))
                self.draw_text('Thanks for Playing', 20, self.DISPLAY_W / 2, self.DISPLAY_H / 2)
                self.draw_text('Winner is Black', 20, self.DISPLAY_W / 2, self.DISPLAY_H / 2 + 30)
                self.window.blit(self.display, (0, 0))
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            sys.exit(0)
            else:
                self.map.reset()
                self.display.fill(self.BLACK)
                self.display.blit(bg_game, (0, 0))
                self.draw_text('Thanks for Playing', 20, self.DISPLAY_W / 2, self.DISPLAY_H / 2)
                self.draw_text('Winner is White', 20, self.DISPLAY_W / 2, self.DISPLAY_H / 2 + 30)
                self.window.blit(self.display, (0, 0))
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            sys.exit(0)
        pygame.mouse.set_visible(True)

    def click_button(self, button):
        if button.click(self):
            for tmp in self.buttons:
                if tmp != button:
                    tmp.unclick()

    def check_buttons(self, mouse_x, mouse_y):
        for button in self.buttons:
            if button.rect.collidepoint(mouse_x, mouse_y):
                self.click_button(button)
                break
