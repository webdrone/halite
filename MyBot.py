from hlt import *
from networking import *
import random

myID, gameMap = getInit()
sendInit("MyPythonBot")


def move(location):
    site = gameMap.getSite(location)
    if site.strength == 0:
        return Move(location, STILL)
    return Move(location, random.choice(DIRECTIONS))


def choose_action(location, epsilon=0):
    # pick ε-greedy action
    if random.random() < epsilon:
        act = random.choice(actions)
    else:
        s = get_state(location)
        poss_act = {(s, a): value_action_function[(s, a)]
                    for a in actions}
        act = max(
            poss_act, key=lambda k: (poss_act[k], random.random()))[1]
        return act


# Finding own pieces, invoking move function, and creating reply frame.
while True:
    moves = []
    gameMap = getFrame()
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            location = Location(x, y)
            if gameMap.getSite(location).owner == myID:
                # moves.append(move(location))
                moves.append(choose_action(location), get_state)

    sendFrame(moves)


# Value function should be loaded as value_action_function
value_action_function = {}


# get_state function should depend on the value-function used (maybe imported?)
# Example for state = site.strength:
def get_state(location):
    site = gameMap.getSite(location)
    state = site.strength
    return state
