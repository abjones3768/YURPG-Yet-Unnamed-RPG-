import pygame
import constants


class Menu:
    def __init__(self, W, H, game_state, window, sfx, menu_theme):  #Initializer/constructor in class
        
        self.menu_state = constants.MAIN_MENU  #The gamestate will begin in the main menu
        self.playing, self.game_active = True, False
        self.DISPLAY_W = W
        self.DISPLAY_H = H
        self.SFX = sfx
        self.display = pygame.Surface(
            (self.DISPLAY_W, self.DISPLAY_H), pygame.SRCALPHA)  #Actually creates the canvas using tuple with DISPLAY_W AND H
        self.window = window  #Creates window of same dimensions
        self.font_name = '8-BIT WONDER.TTF'  #Points to font
        self.BLACK, self.WHITE = (0, 0, 0, 0), (255, 255, 255)  #Set these colors

        self.New_Button = self.draw_text('New Game', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .5)  #These will be the rectangle attributes for mouse collision detection
        self.Load_Button = self.draw_text('Load Game', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
        self.Options_Button = self.draw_text('Options', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
        self.Credits_Button = self.draw_text('Credits', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
        self.Menu_Button = self.draw_text('Main Menu', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
        self.Exit_Button = self.draw_text('Exit', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
        self.Back_Button = self.draw_text('BACK', self.DISPLAY_W//constants.TILE_SIZE//8, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
        self.Skill_Button = self.draw_text_vertical("Skills", self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .95, self.DISPLAY_H * .5, 90)
        self.Inventory_Button = self.draw_text_vertical("Inventory", self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .05, self.DISPLAY_H * .5, 270)
        self.hovering = False
        self.menu_theme = menu_theme
        self.menu_theme.play(-1)

    def display_menu(self):
        self.check_menu_events()
        match self.menu_state: #main menu

            case constants.MAIN_MENU:
                if self.hovering != True: #If mouse is not hovering then this can be true
                    self.display.fill(self.BLACK)  #Resets menu screen by filling in black
                    self.draw_text('Yet Unnamed', int(self.DISPLAY_W/constants.TILE_SIZE), self.DISPLAY_W * .5, self.DISPLAY_H * .3)
                    self.draw_text('New Game', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W*.5, self.DISPLAY_H*.5) #Draws text on the middle of the screen
                    self.draw_text('Load Game', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                    self.draw_text('Options', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                    self.draw_text('Credits', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
            
            case constants.INVENTORY: #inventory
                self.display.fill(self.BLACK)  # Resets menu screen by filling in black
                self.draw_text_vertical("Inventory", self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .05, self.DISPLAY_H * .5, 270)
            
            case constants.SKILL_MENU: #skill menu

                self.display.fill(self.BLACK)  # Resets menu screen by filling in black
                self.draw_text_vertical("Skills", self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .95, self.DISPLAY_H * .5, 90)
            
            #case constants.COMBAT_MENU: #combat

            case constants.OPTIONS_MENU: #Options
                if self.hovering != True:
                    self.display.fill(self.BLACK)
                    self.draw_text('Main Menu', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                    self.draw_text('Exit', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
            
            case constants.CREDITS: #Credits
                if self.hovering != True:
                    self.display.fill(self.BLACK)
                    self.draw_text('Programmers', self.DISPLAY_W//constants.TILE_SIZE, self.DISPLAY_W * .5, self.DISPLAY_H * .25)
                    self.draw_text('Breck', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .4)
                    self.draw_text('Daniel', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                    self.draw_text('Jeremy', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                    self.draw_text('Adam', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                    self.draw_text("BACK", self.DISPLAY_W//constants.TILE_SIZE//8, self.DISPLAY_W * .5, self.DISPLAY_H * .8)

        self.window.blit(self.display, (0, 0))  #Aligning our window and our display
        pygame.display.update()  #Will actually show the image on our monitor

    def check_menu_events(self):
        for event in pygame.event.get():  #Goes through list of everything a player can do in their pc
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.menu_state == constants.IN_GAME: #If overworld switch to options
                        self.menu_state = constants.OPTIONS_MENU
                    elif self.menu_state == constants.OPTIONS_MENU: #If options switch back to overworld
                        self.menu_state = constants.IN_GAME
                    elif self.menu_state == constants.CREDITS:
                        self.menu_state = constants.MAIN_MENU
                if event.key == pygame.K_i:
                    if self.menu_state == constants.IN_GAME: #If overworld switch to inventory
                        self.menu_state = constants.INVENTORY
                    elif self.menu_state == constants.INVENTORY: #If inventory switch back to overworld
                        self.menu_state = constants.IN_GAME
                    elif self.menu_state == constants.SKILL_MENU: #If skill menu switch back to overworld
                        self.menu_state = constants.IN_GAME
                if event.key == pygame.K_k:
                    if self.menu_state == constants.IN_GAME:
                        self.menu_state = constants.SKILL_MENU
                    elif self.menu_state == constants.SKILL_MENU:
                        self.menu_state = constants.IN_GAME

            elif event.type == pygame.MOUSEBUTTONDOWN: #When clicking
                if self.menu_state == constants.MAIN_MENU: #If it's the main menu
                    if self.New_Button.collidepoint(event.pos): #NEW GAME
                        self.menu_theme.stop()
                        self.SFX[constants.BUTTON_CLICK].play()
                        self.game_active = True
                        self.menu_state = constants.NEW_GAME
                    elif self.Load_Button.collidepoint(event.pos): #LOAD GAME - not implemented yet
                        #self.menu_theme.stop()
                        self.SFX[constants.ILLEGAL_MOVE].play()
                        #self.menu_state = constants.IN_GAME
                        self.game_active = True
                    elif self.Options_Button.collidepoint(event.pos): #OPTIONS
                        self.SFX[constants.BUTTON_CLICK].play()
                        self.menu_state = constants.OPTIONS_MENU
                    elif self.Credits_Button.collidepoint(event.pos):
                        self.SFX[constants.BUTTON_CLICK].play()
                        self.menu_state = constants.CREDITS
    
                elif self.menu_state == constants.INVENTORY:
                    if self.Skill_Button.collidepoint(event.pos):
                        self.menu_state = constants.SKILL_MENU #GOTO SKILLS

                elif self.menu_state == constants.SKILL_MENU:
                    if self.Inventory_Button.collidepoint(event.pos):
                        self.menu_state = constants.INVENTORY #GOTO INVENTORY

                elif self.menu_state == constants.OPTIONS_MENU: #If it's the options
                    if self.Menu_Button.collidepoint(event.pos): #GO MAIN MENU
                        self.SFX[constants.BUTTON_CLICK].play()
                        if self.game_active:
                            self.menu_theme.play(-1)
                            self.game_active = False
                        self.menu_state = constants.MAIN_MENU
                    elif self.Exit_Button.collidepoint(event.pos): #EXIT GAME
                        self.playing = False

                elif self.menu_state == constants.CREDITS: #If credits
                    if self.Back_Button.collidepoint(event.pos): #Goto menu
                        self.SFX[constants.BUTTON_CLICK].play()
                        self.menu_state = constants.MAIN_MENU
                self.hovering = False

            elif event.type == pygame.MOUSEMOTION: #Make button bigger while hovering
                if self.menu_state == constants.MAIN_MENU:
                    if self.New_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Yet Unnamed', self.DISPLAY_W//constants.TILE_SIZE, self.DISPLAY_W * .5, self.DISPLAY_H * .3)
                        self.draw_text('New Game', self.DISPLAY_W//constants.TILE_SIZE//2, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Load Game', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                        self.draw_text('Options', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                        self.draw_text('Credits', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
                    elif self.Load_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Yet Unnamed', self.DISPLAY_W//constants.TILE_SIZE, self.DISPLAY_W * .5, self.DISPLAY_H * .3)
                        self.draw_text('New Game', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Load Game', self.DISPLAY_W//constants.TILE_SIZE//2, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                        self.draw_text('Options', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                        self.draw_text('Credits', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
                    elif self.Options_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Yet Unnamed', self.DISPLAY_W//constants.TILE_SIZE, self.DISPLAY_W * .5, self.DISPLAY_H * .3)
                        self.draw_text('New Game', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Load Game', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                        self.draw_text('Options', self.DISPLAY_W//constants.TILE_SIZE//2, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                        self.draw_text('Credits', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
                    elif self.Credits_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Yet Unnamed', self.DISPLAY_W//constants.TILE_SIZE, self.DISPLAY_W * .5, self.DISPLAY_H * .3)
                        self.draw_text('New Game', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Load Game', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                        self.draw_text('Options', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                        self.draw_text('Credits', self.DISPLAY_W//constants.TILE_SIZE//2, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
                    else:
                        self.hovering = False
                elif self.menu_state == constants.INVENTORY:
                    if self.Skill_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.menu_state = constants.SKILL_MENU
                        self.display.fill(self.BLACK)
                        self.draw_text_vertical("Skills", self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .95, self.DISPLAY_H * .5, 90)
                elif self.menu_state == constants.SKILL_MENU:
                    if self.Inventory_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.menu_state = constants.INVENTORY
                        self.display.fill(self.BLACK)
                        self.draw_text_vertical("Inventory", self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .05, self.DISPLAY_H * .5, 270)
                elif self.menu_state == 5:
                    if self.Menu_Button.collidepoint(event.pos) and self.menu_state == 5:
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Main Menu', self.DISPLAY_W//constants.TILE_SIZE//2, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Exit', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                    elif self.Exit_Button.collidepoint(event.pos) and self.menu_state == 5:
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Main Menu', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Exit', self.DISPLAY_W//constants.TILE_SIZE//2, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                    else:
                        self.hovering = False
                elif self.menu_state == 6:
                    if self.Back_Button.collidepoint(event.pos):
                        self.hovering = True
                        self.display.fill(self.BLACK)
                        self.draw_text('Programmers', self.DISPLAY_W//constants.TILE_SIZE, self.DISPLAY_W * .5, self.DISPLAY_H * .25)
                        self.draw_text('Breck', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .4)
                        self.draw_text('Daniel', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .5)
                        self.draw_text('Jeremy', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .6)
                        self.draw_text('Adam', self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .7)
                        self.draw_text("BACK", self.DISPLAY_W//constants.TILE_SIZE//4, self.DISPLAY_W * .5, self.DISPLAY_H * .8)
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