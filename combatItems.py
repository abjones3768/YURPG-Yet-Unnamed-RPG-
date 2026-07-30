from combatDefines import *

class Weapon:
    attack = 0
    magicAttack = 0
    element = NONE

class Sword(Weapon):
    attack = 4

class Staff(Weapon):
    attack = 1
    magicAttack = 4


class Armor:
    defense = 0
    element = NONE

class Chestplate(Armor):
    defense = 4

class Shirt(Armor):
    defense = 1


class Item:
    name = 0
    power = 0
    usageFunction = 0
    usageMessage = 0

class Potion(Item):
    name = "Potion"
    power = 20
    def usageFunction(self, actor):
        actor.health += self.power
        if actor.health > actor.maxHealth:
            actor.health = actor.maxHealth
    usageMessage = f"Healed {power} health!"

class Elixir(Item):
    name = "Elixir"
    power = 10
    def usageFunction(self, actor):
        actor.mana += self.power
        if actor.mana > actor.maxMana:
            actor.mana = actor.maxMana
    usageMessage = f"Healed {power} mana!"

weaponDict = {}
armorDict = {}
itemDict = {}

def weaponInit():
    weaponDict["Sword"] = Sword()
    weaponDict["Staff"] = Staff()

def armorInit():
    armorDict["Chestplate"] = Chestplate()
    armorDict["Shirt"] = Shirt()

def itemInit():
    itemDict["Potion"] = Potion()
    itemDict["Elixir"] = Elixir()
