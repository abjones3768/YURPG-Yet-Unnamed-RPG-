from combatDefines import *
from combatItems import *
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

def fireMagic(attacker, defender, manaUsed):
    damage = attacker.magic + weaponDict[attacker.weapon].magicAttack - defender.magicDefense + (manaUsed * 2)
    
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

