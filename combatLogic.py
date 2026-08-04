import os
import time
from combatItems import *
from combatAttacks import *
from combatActors import *
from combatDefines import *
from constants import *

def battleGetTurns(actors, battleTimer): # Steps through battle state when called
    if not battleTimer:
        for actor in actors: 
            battleTimer[actor] = 0

    getsTurn = [] # list of actors that got a turn.
    noTurn = True
    while noTurn:
        for actor in battleTimer: # Iterates through every actor in battleTimer and increments the timer
            battleTimer[actor] += actor.speed # by speed stat
            if battleTimer[actor] > 99: # When a timer exceeds 100, it gets reset to 0 and
                battleTimer[actor] = 0 # the actor is added to a list of actors that get a turn
                getsTurn.append(actor)
                noTurn = False
    random.shuffle(getsTurn) # If multiple actors got a turn in the last loop, randomize their order
    return getsTurn

# Remaining functions are text based display functions used for the testing environment

def TESTcreateBattle(actors, x, y): # Returns a 2d list of either characters '-' or pointers to actors
    actorGrid = [['-' for _ in range(y)] for _ in range(x)]
    for actor in actors: # Iterates through list of actors and randomly assigns a location
        xloc = random.randint(0, x - 1)
        yloc = random.randint(0, y - 1)
        while not actorGrid[yloc][xloc] == '-': # If chosen location is not '-' (already taken), 
            xloc = random.randint(0, x - 1)     # generate a new location
            yloc = random.randint(0, y - 1)
        actorGrid[yloc][xloc] = actor
    return actorGrid

def testEnvironment():
    weaponInit()
    armorInit()
    itemInit()

    members = int(input("How many party members? (1-4)"))
    partyList = []
    while members > 4 or members < 1:
        members = int(input("How many party members? (1-4)"))
    for i in range(members):
        partyList.append(characterInit())
    enemy = Goblin()
    enemy2 = Goblin()
    actors = []
    for member in partyList:
        actors.append(member)
    actors.append(enemy)
    actors.append(enemy2)

    battleGrid = TESTcreateBattle(actors, 8, 8)
    TESTbattleLoop(battleGrid)

def TESTbattleLoop(grid):
    xMax = len(grid) - 1 # Get array dimensions
    yMax = len(grid[0]) - 1
    TESTprintGrid(grid)
    input("Battle Start! Press Enter to continue.")
    actorDict = {} # actorDict is a dictionary of coordinates where the keys are the corresponding actor pointers
    x = -1
    y = -1
    battleTimer = {} # Dict of integers that uses actor pointers as an index to their current value
    for cols in grid: # Builds a dictionary containing all actors and their location, 
        y += 1        # and populates battleTimer dictionary
        x = -1
        for actor in cols:
            x += 1
            if not actor == '-': # If current "actor" is a pointer to an actor
                coordList = list()
                coordList.append(y)
                coordList.append(x)
                actorDict[actor] = coordList
                battleTimer[actor] = 0
    combatLoops = True # Is set to false at end of loop if either no players or no enemies are present
    while combatLoops:
        getsTurn = []
        noTurn = True
        while noTurn:
            for actor in battleTimer: # Iterates through every actor in battleTimer and increments the timer
                battleTimer[actor] += actor.speed # by speed stat (very subject to change)
                if battleTimer[actor] > 99: # When a timer exceeds 100, it gets reset to 0 and
                    battleTimer[actor] = 0 # the actor is added to a list of actors that get a turn
                    getsTurn.append(actor)
                    noTurn = False
        random.shuffle(getsTurn) # If multiple actors got a turn in the last loop, randomize their order
        for actor in getsTurn:
            if isinstance(actor, Player): # If actor is a player
                action = 0
                while action < 1 or action > 5:
                    TESTprintGrid(grid)
                    action = int(input(f"Choose an option for {actor.name}.\n1. Move\n2. Attack\n3. Magic\n4. Items\n5. Wait\n"))
                if action == MOVE:
                    x = 0
                    y = 0
                    print("Input a location to move to (X), (Y)")
                    x = int(input())
                    y = int(input())
                    y -= 1
                    x -= 1
                    yDist = abs(y - actorDict[actor][0])
                    xDist = abs(x - actorDict[actor][1])
                    totalDist = yDist + xDist

                    while x > xMax or y > yMax or x < 0 or y < 0 or not grid[y][x] == '-' or totalDist > actor.movementRange: 
                        print("Invalid move.") # While move out of bounds or moving into actor or moved too far
                        x = int(input())
                        y = int(input())
                        y -= 1
                        x -= 1
                        yDist = abs(y - actorDict[actor][0])
                        xDist = abs(x - actorDict[actor][1])
                        totalDist = yDist + xDist

                    grid[y][x] = actor
                    grid[actorDict[actor][0]][actorDict[actor][1]] = '-'
                    actorDict[actor][1] = x
                    actorDict[actor][0] = y
                    
                    # Moving does not use up a turn, so take input again.
                    action = 0
                    while action < 1 or action > 4:
                        TESTprintGrid(grid)
                        action = int(input("Choose an option.\n1. Attack\n2. Magic\n3. Items\n4. Wait\n"))
                    action += 1 # Increment to sneakily reuse code
                if action == ATTACK:
                    attack = ""
                    while attack not in {'U', 'D', 'L', 'R'}:
                        print("Choose a direction to attack (U/D/L/R)")
                        attack = input()
                        attack.strip()
                    x = actorDict[actor][1]
                    y = actorDict[actor][0]
                    if attack == 'U': y -= 1
                    if attack == 'D': y += 1
                    if attack == 'L': x -= 1
                    if attack == 'R': x += 1
                    if x <= xMax and y <= yMax and x >= 0 and y >= 0 and not grid[y][x] == '-': # If attack is within
                        damage = playerAttack(actor, grid[y][x])                        # grid bounds and target
                        print(f"{actor.name} dealt {damage} damage to {grid[y][x].name}!") # is an actor
                        if grid[y][x].health < 1:
                            TESTprintGrid(grid)
                            print(f"{grid[y][x].name} defeated!") 
                            
                            actor.gainExp(grid[y][x].level)
                            
                            actorDict.pop(grid[y][x])
                            battleTimer.pop(grid[y][x])
                            grid[y][x] = '-' # we love garbage collection
                    else:
                        TESTprintGrid(grid)
                        print("Miss!")

                if action == MAGIC:
                    print("Magic: ")
                    magicNum = len(actor.magicAttacks)
                    for i in range(len(actor.magicAttacks)):
                        print(f"{i + 1}. {actor.magicAttacks[i]}")
                    choice = int(input("Choose a spell."))
                    while choice > magicNum or choice < 1:
                        choice = int(input("Choose a spell."))
                    manaChoice = int(input(f"How much mana do you want to spend? Max: {actor.mana}"))
                    while manaChoice > actor.mana or manaChoice < 1:
                        manaChoice = int(input(f"How much mana do you want to spend? Max: {actor.mana}"))

                    damage = actor.magicAttacks[choice - 1](actor, actor, manaChoice)
                    print(f"{actor.name} dealt {damage} damage to {actor.name}!")
                    if actor.health < 1:
                        TESTprintGrid(grid)
                        print(f"{actor.name} defeated!")
                        actorDict.pop(actor)
                        battleTimer.pop(actor)
                        actor = '-' 

                if action == ITEMS:
                    print("Items: ")
                    itemNum = len(actor.inventory)
                    for i in range(len(actor.inventory)):
                        print(f"{i + 1}. {actor.inventory[i]}")
                    choice = int(input("Choose an item."))
                    while choice > itemNum or choice < 1:
                        choice = int(input("Choose an item."))
                    itemDict[actor.inventory[choice - 1]].usageFunction(actor)
                    print(f"{actor.name} used {itemDict[actor.inventory[choice - 1]].name}. {itemDict[actor.inventory[choice - 1]].usageMessage}")

                if action == WAIT:
                    pass
            else:
                playerList = []
                for rows in grid: # Grab all player actors on field
                    for actors in rows:
                        if isinstance(actors, Player):
                            playerList.append(actors)
                coordList = []
                for i in range(len(playerList)): # Get all coordinates of player actors
                    coordList.append(actorDict[playerList[i]])
                distanceList = []
                for i in range(len(coordList)): # Get absolute distance to all player actors
                    distanceList.append(coordList[i][0] + coordList[i][1])
                closest = distanceList.index(min(distanceList)) # Find closest player actor
                target = playerList[closest]
                canAttack = False
                for i in range(actor.movementRange): # Evil pathfinding
                    if actorDict[target][0] == actorDict[actor][0]: # Same Y position as target
                        if actorDict[target][1] > actorDict[actor][1]: # If actor X position is lower than target (target is to the right)
                            if actorDict[actor][1] + 1 == actorDict[target][1] and actorDict[actor][0] == actorDict[target][0]:
                                canAttack = True
                                break
                            elif grid[actorDict[actor][0]][actorDict[actor][1] + 1] == '-':
                                grid[actorDict[actor][0]][actorDict[actor][1] + 1] = actor
                                grid[actorDict[actor][0]][actorDict[actor][1]] = '-'
                                actorDict[actor][1] += 1
                                if actorDict[actor][1] + 1 == actorDict[target][1] and actorDict[actor][0] == actorDict[target][0]:
                                    canAttack = True
                                    break
                                continue

                        if actorDict[target][1] < actorDict[actor][1]: # Target is to left)
                            if actorDict[actor][1] - 1 == actorDict[target][1] and actorDict[actor][0] == actorDict[target][0]:
                                canAttack = True
                                break
                            elif grid[actorDict[actor][0]][actorDict[actor][1] - 1] == '-':
                                grid[actorDict[actor][0]][actorDict[actor][1] - 1] = actor
                                grid[actorDict[actor][0]][actorDict[actor][1]] = '-'
                                actorDict[actor][1] -= 1
                                if actorDict[actor][1] - 1 == actorDict[target][1] and actorDict[actor][0] == actorDict[target][0]:
                                    canAttack = True
                                    break
                                continue

                    if actorDict[target][0] < actorDict[actor][0]: # Target has a different Y position, check if target is above
                        time.sleep(2)
                        if actorDict[actor][0] - 1 == actorDict[target][0] and actorDict[actor][1] == actorDict[target][1]:
                            canAttack = True
                            break
                        elif grid[actorDict[actor][0] - 1][actorDict[actor][1]] == '-':
                            grid[actorDict[actor][0] - 1][actorDict[actor][1]] = actor
                            grid[actorDict[actor][0]][actorDict[actor][1]] = '-'
                            actorDict[actor][0] -= 1
                            if actorDict[actor][0] - 1 == actorDict[target][0] and actorDict[actor][1] == actorDict[target][1]:
                                canAttack = True
                                break
                            continue

                    if actorDict[target][0] > actorDict[actor][0]: # check if target is down
                        if actorDict[actor][0] + 1 == actorDict[target][0] and actorDict[actor][1] == actorDict[target][1]:
                            canAttack = True
                            break
                        elif grid[actorDict[actor][0] + 1][actorDict[actor][1]] == '-':
                            grid[actorDict[actor][0] + 1][actorDict[actor][1]] = actor
                            grid[actorDict[actor][0]][actorDict[actor][1]] = '-'
                            actorDict[actor][0] += 1
                            if actorDict[actor][0] + 1 == actorDict[target][0] and actorDict[actor][1] == actorDict[target][1]:
                                canAttack = True
                                break
                            continue
                        
                if canAttack:
                    canAttack = False
                    attack = random.choice(actor.attackList) # Grabs a random attack from list
                    damage = attack(actor, target)
                    print(f"{actor.name} dealt {damage} damage to {target.name}!")
                    if target.health < 1:
                        TESTprintGrid(grid)
                        print(f"{target.name} defeated!")
                        grid[actorDict[target][0]][actorDict[target][1]] = '-' # we love garbage collection
                        actorDict.pop(target)
                        battleTimer.pop(target)
                else:
                    TESTprintGrid(grid)
            time.sleep(2)
        playerPresent = False
        enemyPresent = False
        for actor in actorDict:
            if isinstance(actor, Player):
                playerPresent = True
            else: 
                enemyPresent = True
        if not playerPresent:
            TESTprintGrid(grid)
            combatLoops = False
            print("You Lose!")
        if not enemyPresent:
            TESTprintGrid(grid)
            combatLoops = False
            print("You Win!")

def TESTprintGrid(grid):
    os.system("clear")
    for row in grid:
        for actor in row:
            if not actor == '-':
                print(f"{actor.name[0]} ", end = "")
            else:
                print(f"{actor} ", end = "")
        print()

if __name__ == "__main__":
    testEnvironment()
