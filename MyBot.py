from hlt import *
from networking import *
import random
from learning_methods import SarsaLambda
from collections import Counter
import pickle

myID, gameMap = getInit()
sendInit("SarsaLambdaBot")

k = 1  # the number of neighbours considered
# with open('help.txt', 'a') as file_debug:
#     with redirect_stdout(file_debug):
#         print('hello')


def get_states(gameMap, myID):
    locations_states = {}
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            # print(x, y)
            location = Location(x, y)
            if gameMap.getSite(location).owner == myID:
                surround = []
                for j in range(-k, k + 1):
                    for i in range(-k, k + 1):
                        if x + i < 0:
                            xi = gameMap.width - (x + i)
                        elif x + i > gameMap.width:
                            xi = x + i - gameMap.width
                        else:
                            xi = x + i
                        if y + j < 0:
                            yj = gameMap.height - (y + j)
                        elif y + j > gameMap.height:
                            yj = y + j - gameMap.height
                        else:
                            yj = y + j
                        surround += [Location(xi, yj)]
                # boundary = ()
                # print(surround)
                surround_state = []
                for loc in surround:
                    ss = gameMap.getSite(loc)
                    if ss.owner == myID:
                        ss.owner = 1
                    elif ss.owner != 0:
                        ss.owner = -1
                    surround_state += [ss]

                state = tuple(surround_state)
                # print(location.x, location.y)
                locations_states[location] = state
    return locations_states


def move(location):
    site = gameMap.getSite(location)
    if site.strength == 0:
        return Move(location, STILL)
    return Move(location, random.choice(DIRECTIONS))


def step(moves=None):
    sendFrame(moves)


def symmetry(state=None):
    s = tuple(state)

    # check for rotation (3 rotations + 1 gets to the original)
    for rotn in range(4):
        # if s in state-action dictionary, do not attempt symmetry
        if s in [key[0] for key in S_lambda.value_action_function]:
            return s, rotn, None

        # if not, try to find symmetry
        # check for reflection (4 reflections)
        for refl in range(4):
            s1 = []
            for j in range(-k, k + 1):
                for i in range(-k, k + 1):
                    if refl == 0:
                        # transpose (i, j) -> (j, i)
                        s1 += [s[(k + i) * (2 * k + 1) + (j + k)]]
                    elif refl == 1:
                        # transpose opp (i, j) -> (-j, -i)
                        s1 += [s[(k - i) * (2 * k + 1) + (-j + k)]]
                    elif refl == 2:
                        # reflect on vert (i, j) -> (-i, j)
                        s1 += [s[(k + j) * (2 * k + 1) + (-i + k)]]
                    elif refl == 3:
                        # reflect on hor (i, j) -> (i, -j)
                        s1 += [s[(k - j) * (2 * k + 1) + (i + k)]]
            # if s in state-action dictionary, do not attempt symmetry
            if tuple(s1) in [key[0] for key in S_lambda.value_action_function]:
                return tuple(s1), rotn, refl
        # rotate
        s1 = []
        for j in range(-k, k + 1):
            for i in range(-k, k + 1):
                s1 += [s[(k - i) * (2 * k + 1) + (j + k)]]
        s = tuple(s1)
    return s, 0, None


def action_symmetry(a, rotn, refl=None):
    # matching chosen action to rotation, reflection
    # rotn
    if a == 0:
        a_add = a
        return a_add
    elif a - rotn > 0:
        a_add = a - rotn
    else:
        a_add = a - rotn + len(DIRECTIONS) - 1

    # refl
    if refl is None:
        a_add = a_add
    elif refl == 0:
        if a_add == NORTH:
            a_add = WEST
        elif a_add == WEST:
            a_add = NORTH
        elif a_add == SOUTH:
            a_add = EAST
        elif a_add == EAST:
            a_add = SOUTH
    elif refl == 1:
        if a_add == NORTH:
            a_add = EAST
        elif a_add == EAST:
            a_add = NORTH
        elif a_add == SOUTH:
            a_add = WEST
        elif a_add == WEST:
            a_add = SOUTH
    elif refl == 2:
        if a_add == EAST:
            a_add = WEST
        elif a_add == WEST:
            a_add = EAST
    elif refl == 3:
        if a_add == NORTH:
            a_add = SOUTH
        elif a_add == SOUTH:
            a_add = NORTH
    return a_add


l = 0.5

try:
    with open('Sarsa_Q_sa_l' + str(l) + '.pickle', 'rb') as fout:
        Sarsa_Q_sa = pickle.load(fout)
    with open('N_s_a_l' + str(l) + '.pickle', 'rb') as fout:
        N_s_a = pickle.load(fout)
except IOError:
    # print("Couldn't load.")
    Sarsa_Q_sa = {}
    N_s_a = None

# Initialising S_lambda object (learning method)
S_lambda = SarsaLambda(step, actions=DIRECTIONS, lambda_sarsa=l,
                       Q_sa=Sarsa_Q_sa,
                       N_s_a=N_s_a)

# Initialising variables for run_episode (SarsaLambda)
r = 0  # reward
N_0 = 10000
e_s_a = Counter()
delta = 0
epsilon = N_0 / (N_0 + 0)
state_action_list = []
moves = []
gameMap = getFrame()
s_a_track = {}

loc_states = get_states(gameMap, myID)
for loc, s in loc_states.items():
    s, rotn, refl = symmetry(s)
    r = sum(ss.strength for ss in s if ss.owner == myID)
    a = 0  # S_lambda.choose_action(s, epsilon)
    N_s = sum(S_lambda.N_s_a[(s, act)] for act in S_lambda.actions)
    epsilon = N_0 / (N_0 + N_s)
    a_move = action_symmetry(a, rotn=rotn, refl=refl)
    moves.append(Move(loc, a_move))
    state_action_list.append((s, a))
    s_a_track[(gameMap.getLocation(loc, a_move).x,
               gameMap.getLocation(loc, a_move).y)] = (s_a_track.get(
                   (loc.x, loc.y)) or []) + [len(state_action_list) - 1]
    #print(s_a_track, a)
sendFrame(moves)

try:
    while True:
        moves = []
        gameMap = getFrame()
        loc_states = get_states(gameMap, myID)

        for loc, s in loc_states.items():
            # checking for rotational/reflective symmetry
            s, rotn, refl = symmetry(s)

            # reward = territory
            r = sum(ss.strength for ss in s if ss.owner == myID)

            # if not s.terminal:
            # choose action
            N_s = sum(S_lambda.N_s_a[(s, act)] for act in S_lambda.actions)
            epsilon = N_0 / (N_0 + N_s)
            a = S_lambda.choose_action(s, epsilon)
            # checking for action symmetry
            a_move = action_symmetry(a, rotn=rotn, refl=refl)

            # with open('help.txt', 'a') as file_debug:
            #     with redirect_stdout(file_debug):
            #         print(loc)
            #         print(a_add)

            moves.append(Move(loc, a_move))

            # previous s_a in state_action_list
            track_idx = s_a_track.get((loc.x, loc.y))
            s_a_list = None if track_idx is None else [
                state_action_list[t] for t in track_idx]

            delta = r + S_lambda.gamma * \
                (0 if S_lambda.value_action_function.get((s, a)) is None
                    else S_lambda.value_action_function[(s, a)]) \
                - \
                (0 if (s_a_list is None or
                    S_lambda.value_action_function.get(s_a_list[-1]) is None)
                    else S_lambda.value_action_function[s_a_list[-1]])

            # this happens whether or not s.terminal==True
            if s_a_list is not None:
                e_s_a[s_a_list[-1]] += 1
                S_lambda.N_s_a[s_a_list[-1]] += 1

                for s_a in s_a_list:
                    S_lambda.value_action_function[
                        s_a] = S_lambda.value_action_function.get(s_a) or 0
                    S_lambda.value_action_function[
                        s_a] += delta * e_s_a[s_a] / S_lambda.N_s_a[s_a]
                    e_s_a[s_a] *= S_lambda.gamma * S_lambda.lambda_sarsa
                state_action_list.append((s, a))
                s_a_track[(gameMap.getLocation(loc, a_move).x,
                           gameMap.getLocation(loc, a_move).y)] = (s_a_track.get(
                               (loc.x, loc.y)) or []) + \
                    [len(state_action_list) - 1]
                del s_a_track[(loc.x, loc.y)]

        # pickling for persisting Q_sa over many episodes
        with open('Sarsa_Q_sa_l' + str(l) + '.pickle', 'wb') as fout:
            pickle.dump(S_lambda.value_action_function, fout)
        with open('N_s_a_l' + str(l) + '.pickle', 'wb') as fout:
            pickle.dump(S_lambda.N_s_a, fout)

        S_lambda.step(moves)
finally:
    # if s.terminal:
    delta = r - (0 if S_lambda.value_action_function.get(state_action_list[-1])
                 is None
                 else S_lambda.value_action_function[state_action_list[-1]])

    # this happens whether or not s.terminal==True
    e_s_a[state_action_list[-1]] += 1
    S_lambda.N_s_a[state_action_list[-1]] += 1

    for s_a in state_action_list:
        S_lambda.value_action_function[
            s_a] = S_lambda.value_action_function.get(s_a) or 0
        S_lambda.value_action_function[
            s_a] += delta * e_s_a[s_a] / S_lambda.N_s_a[s_a]
        e_s_a[s_a] *= S_lambda.gamma * S_lambda.lambda_sarsa

    # pickling for persisting Q_sa over many episodes
    with open('Sarsa_Q_sa_l' + str(l) + '.pickle', 'wb') as fout:
        pickle.dump(S_lambda.value_action_function, fout)
    with open('N_s_a_l' + str(l) + '.pickle', 'wb') as fout:
        pickle.dump(S_lambda.N_s_a, fout)

# get_state function should depend on the value-function used (maybe imported?)
# Example for state = site.strength:


def get_state(location):
    site = gameMap.getSite(location)
    state = site.strength
    return state
