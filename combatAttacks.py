from combatDefines import *
from combatItems import *
import combatActors
import random

"""RNG DOCS:
random.randint() generates a random integer between the left and right values.
Left value can be as low as -100, right value does not have a limit.
After getting a random integer, it is divided by 100 to get a multiplier value.
1 is added to the value to guarantee it is positive, it is then multiplied with the calculated damage to get the final value

Examples of usage:
random.randomint(-50, 50)...
Floor becomes -0.5x, ceiling becomes 1.5x

random.randomint(-100, 100)...
Floor becomes 0x, ceiling becomes 2.
"""

def playerAttack(attacker, defender):
    damage = attacker.strength + weaponDict[attacker.weapon].attack - defender.defense
    if damage < 0:
        damage = 0
    randy = random.randint(-50, 50)
    mul = float(randy)/100
    mul += 1
    damage = damage * mul
    defender.health -= damage
    return int(damage)

def enemyAttack(attacker, defender):
    damage = attacker.strength - defender.defense - armorDict[defender.armor].defense
    if damage < 0:
        damage = 0
    randy = random.randint(-50, 50)
    mul = float(randy)/100
    mul += 1
    damage = damage * mul
    defender.health -= damage
    return int(damage)

def fireMagic(attacker, defender):
    damage = attacker.magic - defender.magicDefense

    if isinstance(attacker, combatActors.Player):
        damage += weaponDict[attacker.weapon].magicAttack 
    
    if defender.weakness == FIRE:
        damage *= 2
    if defender.resistant == FIRE:
        damage /= 2
    if defender.immune == FIRE:
        return 0
    if defender.absorb == FIRE:
        damage = -damage
    if damage < 0:
        damage = 0

    randy = random.randint(-50, 50)
    mul = float(randy)/100
    mul += 1
    damage = damage * mul
    defender.health -= damage
    return int(damage)

def iceMagic(attacker, defender):
    damage = attacker.magic - defender.magicDefense

    if isinstance(attacker, combatActors.Player):
        damage += weaponDict[attacker.weapon].magicAttack 
    
    if defender.weakness == ICE:
        damage *= 2
    if defender.resistant == ICE:
        damage /= 2
    if defender.immune == ICE:
        return 0
    if defender.absorb == ICE:
        damage = -damage
    if damage < 0:
        damage = 0

    randy = random.randint(-50, 50)
    mul = float(randy)/100
    mul += 1
    damage = damage * mul
    defender.health -= damage
    return int(damage)

def thunderMagic(attacker, defender):
    damage = attacker.magic - defender.magicDefense

    if isinstance(attacker, combatActors.Player):
        damage += weaponDict[attacker.weapon].magicAttack 
    
    if defender.weakness == THUNDER:
        damage *= 2
    if defender.resistant == THUNDER:
        damage /= 2
    if defender.immune == THUNDER:
        return 0
    if defender.absorb == THUNDER:
        damage = -damage
    if damage < 0:
        damage = 0

    randy = random.randint(-50, 50)
    mul = float(randy)/100
    mul += 1
    damage = damage * mul
    defender.health -= damage
    return int(damage)

def healingMagic(attacker, defender):
    damage = -attacker.magic
    
    if isinstance(attacker, combatActors.Player):
        damage -= weaponDict[attacker.weapon].magicAttack

    randy = random.randint(-50, 50)
    mul = float(randy)/100
    mul += 1
    damage = damage * mul
    defender.health += damage
    return int(damage)

def selfHeal(attacker, defender): # Used for dragon, not used by player
    damage = -50
    attacker.health += 50
    return int(damage)

magicList = list()
magicList.append("Fire")
magicList.append("Ice")
magicList.append("Thunder")
magicList.append("Heal")