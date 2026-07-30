import pygame
from pygame import event


class Game():
    def __init__(self):  #Initializer/constructor in class
        pygame.init()  #Gives access to pygame modules
        self.game_state = 0  #The gamestate will begin in the main menu
        self.running, self.playing, self.ingame = True, False, False  #Self.running is true when window is on. Self.playing is true when you're playing. self.ingame is when you've loaded in game

        self.DISPLAY_W, self.DISPLAY_H = 1280, 720  #canvas size of 1280x720 pixels
        self.display = pygame.Surface(
            (self.DISPLAY_W, self.DISPLAY_H))  #Actually creates the canvas using tuple with DISPLAY_W AND H
        self.window = pygame.display.set_mode((self.DISPLAY_W, self.DISPLAY_H))  #Creates window of same dimensions
        self.font_name = '8-BIT WONDER.TTF'  #Points to font
        self.BLACK, self.WHITE = (0, 0, 0), (255, 255, 255)  #Set these colors

        self.New_Button = self.draw_text('New Game', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .5)  #These will be the rectangle attributes for mouse collision detection
        self.Load_Button = self.draw_text('Load Game', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
        self.Options_Button = self.draw_text('Options', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
        self.Credits_Button = self.draw_text('Credits', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
        self.Menu_Button = self.draw_text('Main Menu', 40, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
        self.Exit_Button = self.draw_text('Exit', 40, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
        self.Back_Button = self.draw_text('BACK', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .95)
        self.Skill_Button = self.draw_text_vertical("Skills", 30, self.DISPLAY_W * .95, self.DISPLAY_H * .5, 90)
        self.Inventory_Button = self.draw_text_vertical("Inventory", 30, self.DISPLAY_W * .05, self.DISPLAY_H * .5, 270)
        self.hovering = False

    def game_loop(self):
        while self.playing:
            self.check_events()  #This will check what the player is touching any keys
            match self.game_state: #main menu
                case 0:
                    if self.hovering != True: #If mouse is not hovering then this can be true
                        self.display.fill(self.BLACK)  #Resets menu screen by filling in black
                        self.draw_text('Yet Unnamed', 30, self.DISPLAY_W * .5, self.DISPLAY_H * .3)
                        self.draw_text('New Game', 20, self.DISPLAY_W*.5, self.DISPLAY_H*.5) #Draws text on the middle of the screen
                        self.draw_text('Load Game', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                        self.draw_text('Options', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                        self.draw_text('Credits', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
                case 1: #overworld
                    self.ingame = True
                    self.display.fill(self.BLACK)
                    self.draw_text('Overworld', 50, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                case 2: #inventory

                    self.display.fill(self.BLACK)  # Resets menu screen by filling in black
                    self.draw_text_vertical("Skills", 30, self.DISPLAY_W * .95, self.DISPLAY_H * .5, 90)

                case 3: #skill menu
                    self.display.fill(self.BLACK)  # Resets menu screen by filling in black
                    self.draw_text_vertical("Inventory", 30, self.DISPLAY_W * .05, self.DISPLAY_H * .5, 270)
                #case 4: #combat

                case 5: #Options
                    if self.hovering != True:
                        self.display.fill(self.BLACK)
                        self.draw_text('Main Menu', 40, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Exit', 40, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                case 6: #Credits
                    if self.hovering != True:
                        self.display.fill(self.BLACK)
                        self.draw_text('Programmers', 40, self.DISPLAY_W * .5, self.DISPLAY_H * .25)
                        self.draw_text('Breck', 30, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Daniel', 30, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                        self.draw_text('Jeremy', 30, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                        self.draw_text('Adam', 30, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
                        self.draw_text("BACK", 20, self.DISPLAY_W * .5, self.DISPLAY_H * .95)
            self.window.blit(self.display, (0, 0))  #Aligning our window and our display
            pygame.display.update()  #Will actually show the image on our monitor

    def check_events(self):
        for event in pygame.event.get():  #Goes through list of everything a player can do in their pc
            if event.type == pygame.QUIT:  #If player presses x at top of window it'll close
                self.running, self.playing = False, False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == 1: #If overworld switch to options
                        self.game_state = 5
                    elif self.game_state == 5: #If options switch back to overworld
                        if self.ingame == True:
                            self.game_state = 1
                if event.key == pygame.K_i:
                    if self.game_state == 1: #If overworld switch to inventory
                        self.game_state = 2
                    elif self.game_state == 2: #If inventory switch back to overworld
                        self.game_state = 1
                    elif self.game_state == 3: #If skill menu switch back to overworld
                        self.game_state = 1
            elif event.type == pygame.MOUSEBUTTONDOWN: #When clicking
                if self.game_state == 0: #If it's the main menu
                    if self.New_Button.collidepoint(event.pos): #NEW GAME
                        self.game_state = 1
                    elif self.Load_Button.collidepoint(event.pos): #LOAD GAME
                        self.game_state = 1
                    elif self.Options_Button.collidepoint(event.pos): #OPTIONS
                        self.game_state = 5
                    elif self.Credits_Button.collidepoint(event.pos):
                        self.game_state = 6
                elif self.game_state == 2:
                    if self.Skill_Button.collidepoint(event.pos):
                        self.game_state = 3 #GOTO SKILLS
                elif self.game_state == 3:
                    if self.Inventory_Button.collidepoint(event.pos):
                        self.game_state = 2 #GOTO INVENTORY
                elif self.game_state == 5: #If it's the options
                    if self.Menu_Button.collidepoint(event.pos): #GO MAIN MENU
                        self.ingame = False
                        self.game_state = 0
                    elif self.Exit_Button.collidepoint(event.pos): #EXIT GAME
                        self.running, self.playing = False, False
                elif self.game_state == 6: #If credits
                    if self.Back_Button.collidepoint(event.pos): #Goto menu
                        self.game_state = 0
            elif event.type == pygame.MOUSEMOTION: #Make button bigger while hovering
                if self.game_state == 0:
                    if self.New_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Yet Unnamed', 30, self.DISPLAY_W * .5, self.DISPLAY_H * .3)
                        self.draw_text('New Game', 25, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Load Game', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                        self.draw_text('Options', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                        self.draw_text('Credits', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
                    elif self.Load_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Yet Unnamed', 30, self.DISPLAY_W * .5, self.DISPLAY_H * .3)
                        self.draw_text('New Game', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Load Game', 25, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                        self.draw_text('Options', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                        self.draw_text('Credits', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
                    elif self.Options_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Yet Unnamed', 30, self.DISPLAY_W * .5, self.DISPLAY_H * .3)
                        self.draw_text('New Game', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Load Game', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                        self.draw_text('Options', 25, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                        self.draw_text('Credits', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
                    elif self.Credits_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Yet Unnamed', 30, self.DISPLAY_W * .5, self.DISPLAY_H * .3)
                        self.draw_text('New Game', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Load Game', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                        self.draw_text('Options', 20, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                        self.draw_text('Credits', 25, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
                    else:
                        self.hovering = False
                elif self.game_state == 2:
                    if self.Skill_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.game_state = 3
                        self.display.fill(self.BLACK)
                        self.draw_text_vertical("Skills", 35, self.DISPLAY_W * .95, self.DISPLAY_H * .5, 90)
                elif self.game_state == 3:
                    if self.Inventory_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.game_state = 2
                        self.display.fill(self.BLACK)
                        self.draw_text_vertical("Inventory", 35, self.DISPLAY_W * .05, self.DISPLAY_H * .5, 270)
                elif self.game_state == 5:
                    if self.Menu_Button.collidepoint(event.pos) and self.game_state == 5:
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Main Menu', 45, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Exit', 40, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                    elif self.Exit_Button.collidepoint(event.pos) and self.game_state == 5:
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Main Menu', 40, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Exit', 45, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                    else:
                        self.hovering = False
                elif self.game_state == 6:
                    if self.Back_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Programmers', 40, self.DISPLAY_W * .5, self.DISPLAY_H * .25)
                        self.draw_text('Breck', 30, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Daniel', 30, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                        self.draw_text('Jeremy', 30, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                        self.draw_text('Adam', 30, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
                        self.draw_text("BACK", 25, self.DISPLAY_W * .5, self.DISPLAY_H * .95)
                    else:
                        self.hovering = False



    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(self.font_name, size) #pygame.font() loads and renders .ttf(TrueType fonts)
        text_surface = font.render(text, True, self.WHITE) #creates the surface for the text to appear
        text_rect = text_surface.get_rect() #Used on the surface to create a Rect object covering it
        text_rect.center = (x, y) #Centers the text/rect at x,y
        self.display.blit(text_surface, text_rect) #Copies text onto the game screen

        return text_rect #Returns the rectangle to allow for mouse collision

    def draw_text_vertical(self, text, size, x, y, angle):
        font = pygame.font.Font(self.font_name, size) #pygame.font() loads and renders .ttf(TrueType fonts)
        text_surface = font.render(text, True, self.WHITE) #creates the surface for the text to appear
        vertical_text = pygame.transform.rotate(text_surface, angle) #Flip the text to be vertical
        text_rect = vertical_text.get_rect() #Used on the surface to create a Rect object covering it
        text_rect.center = (x, y) #Centers the text/rect at x,y
        self.display.blit(vertical_text, text_rect) #Copies text onto the game screen

        return text_rect #Returns the rectangle to allow for mouse collision



g = Game() #Initialize an object with Game()

while g.running: #While the window is running
    g.playing = True #Set this to true so the window doesn't stop working
    g.game_loop()