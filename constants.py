# Tile type values
FLOOR = 0
WALL = 1
DOOR = 2
WATER = 3
PLAYER = 4
ENEMY = 5
CHEST = 6
SHADOW = 7

# tile size
TILE_SIZE = 16

# Game states
EXPLORATION_STATE = 0
COMBAT_STATE = 1
MENU_STATE = 2
MOVING_STATE = 3

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

# Tile color map
tile_colors = {
    FLOOR : (125, 120, 130),
    WALL : (94, 92, 100),
    DOOR : (125, 88, 55),
    WATER : (0, 102, 255),
    CHEST : (255, 204, 0),
    PLAYER : (0, 0, 255),
    ENEMY : (255, 0, 0),
    SHADOW : (0, 0, 0)
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