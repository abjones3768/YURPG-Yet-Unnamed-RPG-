from combatDefines import *
from combatAttacks import *
import pathfinder
import constants

def TESTcharacterInit(): # Creates a player object using entered name and job, returns pointer to object
    name = input("Enter character name:\n")
    job = int(input("Enter job.\n1. Warrior\n2. Mage\n3. Rogue\n"))
    while job < 1 or job > NUM_OF_JOBS:
        job = int(input("Enter a valid job.\n"))
    player = Player(name, job)
    return player

class Actor: # Base actor class from which players and enemies inherit from
    def __init__(self, x, y, cur_tile):
        self.x = x
        self.y = y
        self.cur_tile = cur_tile
        self.prev_tile = 0
        self.inventory = list() # List of item names as strings that refer to dict of item stats


    # Destination is the target tile index in the 1D tilemap of the dungeon
    # Other args are for pathfinder functionality
    def move(self, destination, dungeon, state, grid):
        path_map = pathfinder.findPath(self, dungeon, destination, state, grid)
        move_path = None
        if path_map:
            cur = destination
            move_path = [cur]
            while cur != self.cur_tile:
                cur = path_map[cur][3]
                move_path.insert(0, cur)
        return move_path
    
    name = ""

    movementRange = int()

    health = int()
    maxHealth = int()
    mana = int()
    maxMana = int()

    strength = int()
    magic = int() # Magic strength stat
    defense = int()
    magicDefense = int()
    speed = int() # Determines turn order

    weakness = int() # Takes double damage from this element
    resistant = int() # Takes half damage from this element
    immune = int() # Takes no damage from this element
    absorb = int() # Damage turns into healing

    level = int()

    attackList = list() # List of function pointers to valid attacks

class Player(Actor):
    job = int()

    exp = int()
    totalExp = int() 

    # Equipment variables are the names of the equipment.
    # Equipment names serve as keys for a dictionary containing structs that define behavior and stats.
    weapon = ""
    armor = "" 
    accessory = ""

    magicAttacks = list() # List of pointers to spells

    def __init__(self, x, y, cur_tile, name, job):
        super().__init__(x, y, cur_tile)
        self.name = name
        self.job=job
        self.level = 1 
        self.exp = 0 

        self.initInventory()

        match job:
            case _ if job == WARRIOR: # Default stat definitions
                self.movementRange = 12
                self.maxHealth = 50
                self.maxMana = 0
                self.health = 50
                self.mana = 0

                self.strength = 10
                self.defense = 10
                self.magicDefense = 5
                self.speed = 14
                self.magic = 1

                self.weapon = "Iron Sword"
                self.armor = "Iron Chestplate"
                self.accessory = "Armband" # this is actually unused atm
            case _ if job == MAGE:
                self.movementRange = 12
                self.maxHealth = 20
                self.maxMana = 20
                self.health = 20
                self.mana = 20

                self.strength = 3
                self.defense = 0
                self.magicDefense = 10
                self.speed = 12
                self.magic = 10

                self.weapon = "Wooden Staff"
                self.armor = "Apprentice Robe"
                self.accessory = "Necklace" # all of the accessories are unused basically

                self.magicAttacks.append(fireMagic)
                self.magicAttacks.append(iceMagic)
                self.magicAttacks.append(thunderMagic)
                self.magicAttacks.append(healingMagic)
            case _ if job == ROGUE:
                self.movementRange = 12
                self.maxHealth = 40
                self.maxMana = 0
                self.health = 40
                self.mana = 0

                self.strength = 6
                self.defense = 6
                self.magicDefense = 5
                self.speed = 16
                self.magic = 1

                self.weapon = "Iron Dagger"
                self.armor = "Cloth Shirt"
                # self.accessory = "" # No default accessory
            case _:
                print("invalid job lol")
                # this should be validated before the constructor is called
    
    def initInventory(self):
        self.items = {} # Dictionary which uses item name as reference, value is the amount held
        self.items["Potion"] = 3
        self.items["Elixir"] = 1
        self.items["Large Potion"] = 0
        self.items["Large Elixir"] = 0
        self.inventory.append("Potion")
        self.inventory.append("Elixir")
        self.inventory.append("Large Potion")
        self.inventory.append("Large Elixir")

    def expNeeded(self):
        return 100 + (self.level * 50)

    def gainExp(self, enemyLevel):
        expGained = enemyLevel * 20
        self.exp += expGained

        print(self.name, "gained", expGained, "XP!")

        if self.exp >= self.expNeeded():
            self.exp -= self.expNeeded()
            self.levelUp()

    def levelUp(self):
        self.level += 1

        if self.job == WARRIOR:
            self.maxHealth += 8
            self.strength += 3
            self.defense += 2

        elif self.job == MAGE:
            self.maxHealth += 3
            self.maxMana += 5
            self.magic += 3
            self.magicDefense += 2

        elif self.job == ROGUE:
            self.maxHealth += 5
            self.strength += 2
            self.defense += 1

        self.health = self.maxHealth
        self.mana = self.maxMana

        print(self.name, "reached Level", self.level)

class Goblin(Actor): # Remaining class definitions are for enemy types
    name = "Goblin"
    movementRange = 8
    health = 10
    maxHealth = 10

    strength = 17
    speed = 8

    weakness = FIRE

    level = 1

    attackList = list() # List of pointers to all abilites (spells and basic attack)

    def __init__(self, x, y, cur_tile):
        super().__init__(x, y, cur_tile)
        self.attackList.append(enemyAttack)
        self.path_to_player = []
        self.move_step = 0

class SuperGoblin(Actor):
    name = "Super Goblin"
    movementRange = 10
    health = 30
    maxHealth = 30

    strength = 32
    speed = 12

    level = 2

    attackList = list() # List of pointers to all abilites (spells and basic attack)

    def __init__(self, x, y, cur_tile):
        super().__init__(x, y, cur_tile)
        self.attackList.append(enemyAttack)
        self.path_to_player = []
        self.move_step = 0

class MagicGoblin(Actor):
    name = "Goblin Mage"
    movementRange = 6
    health = 20
    maxHealth = 20
    
    magic = 8

    strength = 0
    speed = 10

    level = 3

    attackList = list() # List of pointers to all abilites (spells and basic attack)

    def __init__(self, x, y, cur_tile):
        super().__init__(x, y, cur_tile)
        self.attackList.append(fireMagic)
        self.path_to_player = []
        self.move_step = 0

class LightGoblin(Actor):
    name = "Light Goblin"
    movementRange = 8
    health = 30
    maxHealth = 30
    
    magic = 12

    strength = 2
    speed = 12

    absorb = THUNDER

    level = 4

    attackList = list() # List of pointers to all abilites (spells and basic attack)

    def __init__(self, x, y, cur_tile):
        super().__init__(x, y, cur_tile)
        self.attackList.append(thunderMagic)
        self.path_to_player = []
        self.move_step = 0

class Dragon(Actor):
    name = "Dragon"
    movementRange = 16
    health = 100
    maxHealth = 100
    
    magic = 20

    strength = 20
    speed = 16

    immune = THUNDER
    resistant = ICE
    absorb = FIRE

    level = 4

    attackList = list() # List of pointers to all abilites (spells and basic attack)

    def __init__(self, x, y, cur_tile):
        super().__init__(x, y, cur_tile)
        self.attackList.append(enemyAttack)
        self.attackList.append(fireMagic)
        self.attackList.append(selfHeal)
        self.path_to_player = []
        self.move_step = 0