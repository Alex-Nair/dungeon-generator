import json
import math
import random
import copy
import os

# Used for word-wrap and \n paragraph splitting.
def prettyPrint(inputString):
    paragraphs = inputString.split("\n")

    for (i, paragraph) in enumerate(paragraphs):
        if i > 0:
            print("") # Add a paragraph buffer for cases where we have more than one paragraph.
        
        buffer = ""

        for character in paragraph:
            if (character == " " and len(buffer) >= 80) or len(buffer) >= 120:
                print(buffer)
                buffer = ""
        
            else:
                buffer += character
        
        if buffer != "":
            print(buffer)


def battle(arg):
    xpThresholds = [ # As seen in the DM guide for player characaters
        [25, 50, 75, 100],
        [50, 100, 150, 200],
        [75, 150, 225, 400],
        [125, 250, 375, 500],
        [250, 500, 750, 1100],
        [300, 600, 900, 1400],
        [350, 750, 1100, 1700],
        [450, 900, 1400, 2100],
        [550, 1100, 1600, 2400],
        [600, 1200, 1900, 2800],
        [800, 1600, 2400, 3600],
        [1000, 2000, 3000, 4500],
        [1100, 2200, 3400, 5100],
        [1250, 2500, 3800, 5700],
        [1400, 2800, 4300, 6400],
        [1600, 3200, 4800, 7200],
        [2000, 3900, 5900, 8800],
        [2100, 4200, 6300, 9500],
        [2400, 4900, 7300, 10900],
        [2800, 5700, 8500, 12700]
    ]

    thresholds = [0, 0, 0, 0] # Easy, Normal, Hard, Deadly

    for partyCharacter in arg["party"]:
        for i in range(4):
            if partyCharacter["level"] - 1 >= len(xpThresholds):
                xp = ((partyCharacter["level"] - 20) * 200 + 2800) * (i + 1) # Backup calculation for party members past Level 20.

            else:
                xp = xpThresholds[partyCharacter["level"] - 1][i]

            thresholds[i] += xp * partyCharacter["count"]
    
    targetXP = (thresholds[0] + ((thresholds[3] - thresholds[0]) * (arg["difficulty"] / 10))) * random.uniform(0.8, 1.2)

    creatures = [0 for _ in range(len(arg["enemies"]))]
    totalXP = 0
    creaturesAdded = 0

    currentMultiplier = 1

    while totalXP * currentMultiplier < targetXP:
        # Handle the different multiplier ranges.
        creaturesAdded += 1
        
        if creaturesAdded >= 15:
            currentMultiplier = 4
        elif 14 >= creaturesAdded >= 11:
            currentMultiplier = 3
        elif 10 >= creaturesAdded >= 7:
            currentMultiplier = 2.5
        elif 6 >= creaturesAdded >= 3:
            currentMultiplier = 2
        elif creaturesAdded == 2:
            currentMultiplier = 1.5
        else:
            currentMultiplier = 1

        # Predict the XP cost of each other monster.
        predictions = [[i, totalXP + enemy["xp"]] for (i, enemy) in enumerate(arg["enemies"])]

        validPredictions = []

        for prediction in predictions:
            if prediction[1] * currentMultiplier <= targetXP:
                validPredictions.append(prediction)
        
        if len(validPredictions) <= 0:
            lowestIndex = 0
            lowestXP = None

            for (i, enemy) in enumerate(arg["enemies"]):
                if lowestXP == None or (lowestXP > enemy["xp"]):
                    lowestXP = enemy["xp"]
                    lowestIndex = i
                
            validPredictions.append([lowestIndex, totalXP + lowestXP]) # Fallback option - Add the weakest enemy to reach the target XP.
        
        chosenMonster = random.choice(validPredictions)

        creatures[chosenMonster[0]] += 1
        totalXP = chosenMonster[1]

    difficulties = ["Very Easy", "Easy", "Normal", "Hard", "Deadly"]
    currentDifficulty = 0

    for threshold in thresholds:
        if totalXP * currentMultiplier >= threshold:
            currentDifficulty += 1
        else:
            break
    
    print(f"Predicted Difficulty: {difficulties[currentDifficulty]}\n")

    for (i, creature) in enumerate(creatures):
        if creature > 0:
            name = arg["enemies"][i]["name"]
            print(f"{name}: {creature}")

    input("\nPress enter to continue...")


def event(arg):
    chosenEvent = random.choice(arg)
    arg.remove(chosenEvent)

    print(chosenEvent["name"] + ":")
    prettyPrint(chosenEvent["description"])

    input("\nPress enter to continue...")


def treasure(arg):
    gold = random.choice(range(arg["treasure_minimum"], arg["treasure_maximum"] + 1))

    itemCosts = { # Estimated costs. Edit if needed.
        "Standard Item": 30,
        "Common Magic Item": 75,
        "Uncommon Magic Item": 250,
        "Rare Magic Item": 3000,
        "Very Rare Magic Item": 30000,
        "Legendary Magic Item": 75000
    }

    pureGold = math.floor(gold * random.uniform(0.25, 0.75)) # Gold that isn't converted into items.
    gold -= pureGold

    items = [0 for i in range(len(list(itemCosts)))]

    itemNames = [key for key in list(itemCosts.keys())]
    itemNames.reverse() # Reversed so that we go from most expensive to least expensive.

    addedValidItem = True

    while addedValidItem:
        addedValidItem = False

        for i, name in enumerate(itemNames):
            if gold >= itemCosts[name] and (random.choice([0, 1]) == 0 or name == itemNames[-1]):
                items[i] += 1
                gold -= math.floor(itemCosts[name] * random.uniform(0.6, 1.4))
                addedValidItem = True
                break
    
    print(f"Gold: {pureGold}")
    print("\nItems:")

    # Reverse the items again for displaying.
    items.reverse()
    itemNames.reverse()

    for (i, name) in enumerate(itemNames):
        if items[i] > 0:
            print(f"{name}: {items[i]}")

    input("\nPress enter to continue...")


def elite(arg):
    chosenElite = random.choice(arg["elite_fights"])
    print(chosenElite["name"] + ":")
    prettyPrint(chosenElite["description"])

    input("\nPress enter to continue...")


def boss(arg):
    chosenBoss = random.choice(arg["bosses"])
    print(chosenBoss["name"] + ":")
    prettyPrint(chosenBoss["description"])

    input("\nPress enter to continue...")


def manager():
    # Load settings.
    with open("settings.json", "r") as file:
        settings = json.load(file)
    
    # We keep track of the events that we've already shown such that we cycle through every event before repeats.
    loadedEvents = copy.deepcopy(settings["events"])

    os.system("cls")

    while True:
        try:
            options = {
                "Battle": battle,
                "Event": event,
                "Treasure": treasure,
                "Elite": elite,
                "Boss": boss
            }

            for (i, option) in enumerate(options.keys()):
                print(f"{i + 1}: {option}")
            
            choice = int(input("\n> "))
            os.system("cls")

            if choice < 1 or choice > len(options.keys()):
                print("Invalid input, please try again.\n")
            
            else:
                options[list(options.keys())[choice - 1]](settings if list(options.keys())[choice - 1] != "Event" else loadedEvents)
                os.system("cls")

                # Refresh events if there are none.
                if len(loadedEvents) <= 0:
                    loadedEvents = copy.deepcopy(settings["events"])

        except ValueError:
            os.system("cls")
            print("Invalid input, please try again.\n")


if __name__ == "__main__":
    manager()