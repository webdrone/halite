from hlt import *
from networking import *
import random
from learning_methods import State
from learning_methods import SarsaLambda

myID, gameMap = getInit()
sendInit("MyPythonBot")


class State:

    def __init__(self):
        self.player = card_draw('Black')
        self.dealer = card_draw('Black')
        self.turn = 0
        self.terminal = False

    def print_state(self):
        state_str = ""
        state_str += "Player score: " + str(self.player) + "\n"
        state_str += "Dealer score: " + str(self.dealer) + "\n"
        state_str += "Turn: " + str(self.turn) + "\n"
        state_str += "Terminal state: " + str(self.terminal) + "\n"
        return state_str

    def get_s(self):
        s = tuple((int(self.player), int(self.dealer)))
        return s


def get_states(gameMap, myID):
    locations_states = {}
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            if gameMap.getSite(location).owner == myID:
                location = Location(x, y)
                surround = []
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if not (i == 0 and j == 0):
                            surround += [Location(x + k * i, y + k * j)]
                # boundary = ()
                    state = (gameMap.getSite(location), tuple(surround))
                    locations_states[location] = state
    return locations_states


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


l = 0.5

try:
    with open('Sarsa_Q_sa_l' + str(l) + '.pickle', 'rb') as fout:
        Sarsa_Q_sa = pickle.load(fout)
    with open('N_s_a_l' + str(l) + '.pickle', 'rb') as fout:
        N_s_a = pickle.load(fout)
except IOError:
    Sarsa_Q_sa = {}
    N_s_a = None

# Initialising S_lambda object (learning method)
S_lambda = SarsaLambda(step, actions=DIRECTIONS, lambda_sarsa=l, Sarsa_Q_sa,
                       N_s_a)

# Initialising variables for run_episode (SarsaLambda)
s = State()  # state
r = 0  # reward
N_0 = 100
e_s_a = Counter()
delta = 0
epsilon = N_0 / (N_0 + 0)
state_action_list = []
moves = []
gameMap = getFrame()

loc_states = get_states(gameMap, myID)
for loc, s in loc_states.items():
    a = self.choose_action(s, epsilon)
    moves.append(Move(loc, a))
    state_action_list.append((s, a))

sendFrame(moves)

try:
    while True:
        moves = []
        gameMap = getFrame()

        loc_states = get_states(gameMap, myID)
        for loc, s in loc_states.items():
            # if not s.terminal:
            N_s = sum([self.N_s_a[(s, act)]
                       for act in self.actions])
            epsilon = N_0 / (N_0 + N_s)
            a = self.choose_action(s, epsilon)
            moves.append(Move(loc, a))

            delta = r + self.gamma * self.value_action_function[(s, a)]\
                - self.value_action_function[state_action_list[-1]]

            # this happens whether or not s.terminal==True
            e_s_a[state_action_list[-1]] += 1
            self.N_s_a[state_action_list[-1]] += 1

            for s_a in state_action_list:
                self.value_action_function[
                    s_a] += delta * e_s_a[s_a] / self.N_s_a[s_a]
                e_s_a[s_a] *= self.gamma * self.lambda_sarsa
            state_action_list.append((s, a))
        sendFrame(moves)
finally:
    # if s.terminal:
    delta = r - self.value_action_function[state_action_list[-1]]

    # this happens whether or not s.terminal==True
    e_s_a[state_action_list[-1]] += 1
    self.N_s_a[state_action_list[-1]] += 1

    for s_a in state_action_list:
        self.value_action_function[
            s_a] += delta * e_s_a[s_a] / self.N_s_a[s_a]
        e_s_a[s_a] *= self.gamma * self.lambda_sarsa

    # pickling for persisting Q_sa over many episodes
    with open('Sarsa_Q_sa_l' + str(l) + '.pickle', 'wb') as fout:
        pickle.dump(Sarsa_Q_sa, fout)
    with open('N_s_a_l' + str(l) + '.pickle', 'rb') as fout:
        pickle.dump(N_s_a, fout)

# get_state function should depend on the value-function used (maybe imported?)
# Example for state = site.strength:


def get_state(location):
    site = gameMap.getSite(location)
    state = site.strength
    return state


def step():
    sendFrame(moves)
