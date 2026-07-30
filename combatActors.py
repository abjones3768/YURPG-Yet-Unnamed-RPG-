from combatDefines import *
from combatAttacks import *

def characterInit(): # Creates a player object using entered name and job, returns pointer to object
    name = input("Enter character name:\n")
    job = int(input("Enter job.\n1. Warrior\n2. Mage\n3. Rogue\n"))
    while job < 1 or job > NUM_OF_JOBS:
        job = int(input("Enter a valid job.\n"))
    player = Player(name, job)
    return player

class Actor: # Base actor class from which players and enemies inherit from
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

    def __init__(self, name, job):
        self.name = name

        items = {} # Dictionary which uses item name as reference, value is the amount held

        match job:
            case _ if job == WARRIOR: # Default stat definitions
                self.movementRange = 3
                self.maxHealth = 50
                self.maxMana = 0
                self.health = 50
                self.mana = 0

                self.strength = 10
                self.defense = 10
                self.magicDefense = 5
                self.speed = 3 # default 5
                self.magic = 1

                self.weapon = "Sword"
                self.armor = "Chestplate"
                self.accessory = "Armband"
            case _ if job == MAGE:
                self.movementRange = 3
                self.maxHealth = 20
                self.maxMana = 20
                self.health = 20
                self.mana = 20

                self.strength = 3
                self.defense = 0
                self.magicDefense = 10
                self.speed = 2 # default 3
                self.magic = 10

                self.weapon = "Staff"
                self.armor = "Shirt"
                self.accessory = "Necklace"
            case _ if job == ROGUE:
                self.movementRange = 3
                self.maxHealth = 40
                self.maxMana = 0
                self.health = 40
                self.mana = 0

                self.strength = 6
                self.defense = 6
                self.magicDefense = 5
                self.speed = 10
                self.magic = 1

                self.weapon = "Knife"
                self.armor = "Shirt"
                # self.accessory = "" # No default accessory
            case _:
                print("invalid job lol")
                # this should be validated before the constructor is called

class Goblin(Actor): # Remaining class definitions are for enemy types
    name = "Goblin"
    movementRange = 2
    health = 10
    maxHealth = 10

    strength = 2
    speed = 1

    weakness = FIRE

    level = 1

    attackList = list() # List of pointers to all abilites (spells and basic attack)

    def __init__(self):
        self.attackList.append(enemyAttack)