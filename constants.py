# Tile type values
FLOOR = 0
WALL = 1
DOOR = 2
WATER = 3
CHEST = 4
PLAYER = 5
ENEMY = 6
SHADOW = 7

# Menu state values
MAIN_MENU = 0
IN_GAME = 1
INVENTORY = 2
SKILL_MENU = 3
COMBAT_MENU = 4
OPTIONS_MENU = 5
CREDITS = 6
NEW_GAME = 7
JOB_SELECT = 8

# tile size
TILE_SIZE = 16

# Game states
EXPLORATION_STATE = 0
COMBAT_STATE = 1
MENU_STATE = 2
MOVING_STATE = 3
RESETTING = 4

# Rendering modes
TOP_DOWN = 4
ISOMETRIC = 5

# Number of radial segments used for fov
OCTANTS = 8

# Sound effect ids
GAME_OVER = 0
LEVEL_UP = 1
MELEE_ATTACK = 2
OPEN_DOOR = 3
VICTORY = 4
BUTTON_CLICK = 5
ILLEGAL_MOVE = 6
ITEM_FOUND = 7
MAGIC = 8
NEW_GAME = 9

# Music track ids
MENU_THEME = 0

# Tile color map
tile_colors = {
    FLOOR : (125, 120, 130),
    WALL : (94, 92, 100),
    DOOR : (125, 88, 55),
    WATER : (0, 102, 255),
    CHEST : (255, 204, 0),
    PLAYER : (0, 0, 255),
    ENEMY : (255, 0, 0),
    SHADOW : (0, 0, 0),
}

# Matrices used for isometric mode rendering and click handling
iso_matrix = (
    (0.5, -0.5),
    (0.25, 0.25)
)
adj_matrix = (
    (iso_matrix[1][1], -iso_matrix[0][1]),
    (-iso_matrix[1][0], iso_matrix[0][0])
)
det_reciprocal = 1 / (iso_matrix[0][0]*iso_matrix[1][1] - iso_matrix[0][1]*iso_matrix[1][0])

click_matrix = (
    (adj_matrix[0][0]*det_reciprocal, adj_matrix[0][1]*det_reciprocal),
    (adj_matrix[1][0]*det_reciprocal, adj_matrix[1][1]*det_reciprocal)
)