from Start import StartGame
from pygame import mixer

g = StartGame()
mixer.music.load('background.mp3')

while g.running:
    g.curr_menu.display_menu()
    g.game_loop()

