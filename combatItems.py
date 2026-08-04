from combatDefines import *

class Weapon:
    attack = 0
    magicAttack = 0
    element = NONE
    level = 0

class Sword(Weapon):
    def __init__(self, level):
        self.attack = 4 + level

class Knife(Weapon):
    def __init__(self, level):
        self.attack = 2 + level

class Staff(Weapon):
    def __init__(self, level):
        self.attack = 1
        self.magicAttack = 4 + level


class Armor:
    defense = 0
    magicDefense = 0
    element = NONE
    level = 0

class Chestplate(Armor):
    def __init__(self, level):
        self.defense = 4 + level

class Shirt(Armor):
    def __init__(self, level):
        self.defense = 1 + level

class Robe(Armor):
    def __init__(self, level):
        self.defense = 1
        self.magicDefense = 4 + level


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

class LargePotion(Item):
    name = "Large Potion"
    power = 100
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

class LargeElixir(Item):
    name = "Large Elixir"
    power = 50
    def usageFunction(self, actor):
        actor.mana += self.power
        if actor.mana > actor.maxMana:
            actor.mana = actor.maxMana
    usageMessage = f"Healed {power} mana!"

weaponDict = {}
armorDict = {}
itemDict = {}

def weaponInit():
    weaponDict["Iron Sword"] = Sword(1)
    weaponDict["Steel Sword"] = Sword(2)
    weaponDict["Mythril Sword"] = Sword(3)
    weaponDict["Iron Dagger"] = Knife(1)
    weaponDict["Steel Dagger"] = Knife(2)
    weaponDict["Mythril Dagger"] = Knife(3)
    weaponDict["Wooden Staff"] = Staff(1)
    weaponDict["Ebony Staff"] = Staff(2)
    weaponDict["Staff of Wisdom"] = Staff(3)

def armorInit():
    armorDict["Iron Chestplate"] = Chestplate(1)
    armorDict["Steel Chestplate"] = Chestplate(2)
    armorDict["Mythril Chestplate"] = Chestplate(3)
    armorDict["Cloth Shirt"] = Shirt(1)
    armorDict["Leather Cuirass"] = Shirt(2)
    armorDict["Studded Leather Cuirass"] = Shirt(3)
    armorDict["Apprentice Robe"] = Robe(1)
    armorDict["Journeyman Robe"] = Robe(2)
    armorDict["Master Robe"] = Robe(3)

def itemInit():
    itemDict["Potion"] = Potion()
    itemDict["Elixir"] = Elixir()
    itemDict["Large Potion"] = Potion()
    itemDict["Large Elixir"] = Elixir()
