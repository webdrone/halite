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
    prod = {}
    # prod_tot = 0
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            # print(x, y)
            location = Location(x, y)
            # prod_tot += gameMap.getSite(location).production
            if gameMap.getSite(location).owner == myID:
                # prod_me += gameMap.getSite(location).production
                locations_states[location] = 0

    # prod_frac = prod_me / prod_tot

    for location in locations_states:
        x = location.x
        y = location.y
        surround = []

        for j in range(-k, k + 1):
            for i in range(-k, k + 1):
                if x + i < 0:
                    xi = gameMap.width + (x + i)
                elif x + i >= gameMap.width:
                    xi = x + i - gameMap.width
                else:
                    xi = x + i
                if y + j < 0:
                    yj = gameMap.height + (y + j)
                elif y + j >= gameMap.height:
                    yj = y + j - gameMap.height
                else:
                    yj = y + j
                surround += [Location(xi, yj)]
        # boundary = ()
        # print(surround)
        surround_state = []
        prod_me = 0
        # prod_me = 0
        # prod_tot = 0
        for loc in surround:
            ss = gameMap.getSite(loc)
            # prod_tot += ss.production
            if ss.owner == myID:
                ss.owner = 1
                prod_me += ss.production
            elif ss.owner != 0:
                ss.owner = -1
            surround_state += [(ss.owner, ss.strength, ss.production)]
        # prod_frac = prod_me / prod_tot
        # if prod_frac == 1:
        #     prod_frac = 0
        state = tuple(surround_state)
        # print(state[0].strength, state[0].production,
        #       state[1].strength, state[1].production)
        # print(location.x, location.y)
        locations_states[location] = state
        prod[(location.x, location.y)] = prod_me
    return locations_states, prod


def get_my_production_at(gameMap, myID, locations):
    prod = {}
    for location in locations:
        x = location.x
        y = location.y
        surround = []

        for j in range(-k, k + 1):
            for i in range(-k, k + 1):
                if x + i < 0:
                    xi = gameMap.width + (x + i)
                elif x + i >= gameMap.width:
                    xi = x + i - gameMap.width
                else:
                    xi = x + i
                if y + j < 0:
                    yj = gameMap.height + (y + j)
                elif y + j >= gameMap.height:
                    yj = y + j - gameMap.height
                else:
                    yj = y + j
                surround += [Location(xi, yj)]

        prod_me = 0

        for loc in surround:
            ss = gameMap.getSite(loc)
            if ss.owner == myID:
                prod_me += ss.production

        prod[(location.x, location.y)] = prod_me
    return prod


def move(location):
    site = gameMap.getSite(location)
    if site.strength == 0:
        return Move(location, STILL)
    return Move(location, random.choice(DIRECTIONS))


def step(moves=None):
    sendFrame(moves)


def revert_direction(dir=STILL):
    if dir == STILL:
        return STILL
    if dir == NORTH:
        return SOUTH
    if dir == SOUTH:
        return NORTH
    if dir == EAST:
        return WEST
    if dir == WEST:
        return EAST


def symmetry(state=None):
    s = tuple(state)
    return s, 0, None

    # check for rotation (3 rotations + 1 gets to the original)
    for rotn in range(4):
        # if s in state-action dictionary, do not attempt symmetry
        # print([key[0] for key in S_lambda.value_action_function])
        if s in [key for key in S_lambda.value_action_function]:
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
            if tuple(s1) in [key for key in S_lambda.value_action_function]:
                return s1, rotn, refl
        # rotate
        s1 = []
        for j in range(-k, k + 1):
            for i in range(-k, k + 1):
                s1 += [s[(k - i) * (2 * k + 1) + (j + k)]]
        s = tuple(s1)
    return s, 0, None


def action_symmetry(a, rotn, refl=None):
    # return a
    a_add = a

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

    # matching chosen action to rotation, reflection
    # rotn
    if a_add == STILL:
        return a_add
    elif a_add - rotn > 0:
        a_add = a_add - rotn
    else:
        a_add = a_add - rotn + len(DIRECTIONS) - 1
    return a_add


lam = 0.5

try:
    with open('Sarsa_Q_sa_l' + str(lam) + '.pickle', 'rb') as fout:
        Sarsa_Q_sa = pickle.load(fout)
    with open('N_s_a_l' + str(lam) + '.pickle', 'rb') as fout:
        N_s_a = pickle.load(fout)
except IOError:
    # print("Couldn't load.")
    Sarsa_Q_sa = {}
    N_s_a = None

# Initialising S_lambda object (learning method)
S_lambda = SarsaLambda(step, actions=DIRECTIONS, lambda_sarsa=lam,
                       Q_sa=Sarsa_Q_sa,
                       N_s_a=N_s_a)

# Initialising variables for run_episode (SarsaLambda)
r = 0  # reward
N_0 = 1
e_s_a = Counter()
delta = 0
epsilon = N_0 / (N_0 + 0)
state_action_list = []
moves = []
s_a_track = {}
prod = {}

"""
gameMap = getFrame()
loc_states, prod = get_states(gameMap, myID)
for loc, s in loc_states.items():
    s, rotn, refl = symmetry(s)
    # r = sum(ss.strength for ss in s if ss.owner == myID)
    r = prod[(loc.x, loc.y)]
    a = 0  # S_lambda.choose_action(s, epsilon)
    N_s = sum(S_lambda.N_s_a[(s, act)] for act in S_lambda.actions)
    epsilon = N_0 / (N_0 + N_s)
    a_move = action_symmetry(a, rotn=rotn, refl=refl)
    moves.append(Move(loc, a_move))
    state_action_list += [(s, a)]
    s_a_track[(gameMap.getLocation(loc, a_move).x,
               gameMap.getLocation(loc, a_move).y)] = (s_a_track.get(
                   (loc.x, loc.y)) or []) + [len(state_action_list) - 1]
    #print(s_a_track, a)
sendFrame(moves)
"""
try:
    while True:
        gameMap = getFrame()
        # loc_states_prev = dict(loc_states)
        prod_prev = dict(prod)
        moves_prev = list(moves)
        s_a_track_old = dict(s_a_track)
        loc_states, prod = get_states(gameMap, myID)
        # prod_new = get_my_production_at(loc_states.keys())
        moves = []

        del_loc = [loc for loc in s_a_track_old
                   if loc not in [(l.x, l.y) for l in loc_states]]
        for loc in del_loc:
            del s_a_track_old[loc]
        # if len(del_loc) > 0:
        #     print(del_loc)
        s_a_track = {}

        for loc, s in loc_states.items():
            # checking for rotational/reflective symmetry
            s_or = tuple(s)
            s, rotn, refl = symmetry(s)

            if (rotn != 0) or (refl is not None):
                print("original state", s_or)
                print(s, rotn, refl)

            # reward = territory
            # ss.owner = 1 if owner = myID (in get_states)
            # r = sum(ss.strength for ss in s if ss.owner == 1) \
            # r = sum(ss.production for ss in s if ss.owner == 1)  # + \
            if s_a_track_old.get((loc.x, loc.y)) is None:
                r = 0  # -prod[(loc.x, loc.y)]  # - prod_prev[(loc.x, loc.y)]
            else:
                loc_old = next(
                    (obj.loc for obj in moves_prev if
                     (gameMap.getLocation(obj.loc, obj.direction).x,
                      gameMap.getLocation(obj.loc, obj.direction).y) ==
                     (loc.x, loc.y)), 0)

                # if loc_old == 0:
                #     print('loc_new:', loc.x, loc.y)
                #     print([(obj.loc.x, obj.loc.y, obj.direction)
                #            for obj in moves_prev])
                #     print(track_temp)
                #     print(s_a_track_old)
                #     print(state_action_list[
                #            s_a_track_old[(loc.x, loc.y)][-1]][-1])
                #     print(del_loc)

                r = get_my_production_at(
                    gameMap, myID, [loc_old])[(loc_old.x, loc_old.y)] \
                    - prod_prev[(loc_old.x, loc_old.y)]

            # if prod_new == 0:
            #     r = 0
            # else:
            #     r = (s[int((len(s) - 1) / 2)][-1] -
            #          (loc_states_prev.get(loc) or (0, 0))[-1])  # / prod_new

            # if not s.terminal:
            # choose action
            N_s = sum(S_lambda.N_s_a[(s, act)] for act in S_lambda.actions)
            epsilon = N_0 / (N_0 + N_s)
            a = S_lambda.choose_action(s, epsilon)
            # reverting action symmetry
            a_move = action_symmetry(a, rotn=rotn, refl=refl)

            moves += [Move(loc, a_move)]

            # previous s_a in state_action_list
            track_idx = s_a_track_old.get((loc.x, loc.y))
            s_a_list = None if track_idx is None else [
                state_action_list[t] for t in track_idx]
            # if track_idx is None:
            #     s_a_track[(loc.x, loc.y)] = []

            # this happens whether or not s.terminal==True
            if s_a_list is not None:
                delta = r + S_lambda.gamma * \
                    (0 if S_lambda.value_action_function.get((s, a)) is None
                     else S_lambda.value_action_function[(s, a)]) \
                    - \
                    (0 if (s_a_list is None or
                           S_lambda.value_action_function.get(s_a_list[-1])
                           is None)
                     else S_lambda.value_action_function[s_a_list[-1]])

                e_s_a[s_a_list[-1]] += 1
                S_lambda.N_s_a[s_a_list[-1]] += 1

                for s_a in s_a_list:
                    S_lambda.value_action_function[
                        s_a] = S_lambda.value_action_function.get(s_a) or 0
                    S_lambda.value_action_function[
                        s_a] += delta * e_s_a[s_a] / S_lambda.N_s_a[s_a]
                    e_s_a[s_a] *= S_lambda.gamma * S_lambda.lambda_sarsa

            state_action_list += [tuple((s, a))]
            # if s_a_track.get((loc.x, loc.y)) is not None:
            track_temp = list(s_a_track_old.get((loc.x, loc.y)) or [] +
                              [len(state_action_list) - 1])
            s_a_track[(gameMap.getLocation(loc, a_move).x,
                       gameMap.getLocation(loc, a_move).y)] = track_temp
            # if (s_a_track.get((loc.x, loc.y)) is not None) & (a_move != 0):
            #     print('wtf')

        # Checking for killed bots and punishing
        # loc_states_dict = [(loc.x, loc.y) for loc in loc_states]
        # del_loc = []
        # for loc in s_a_track:
        #     if loc not in loc_states_dict:
        #         # r = -1 * gameMap.getSite(Location(*loc)).strength
        #         # track_idx = s_a_track[loc]
        #         # s_a_list = [state_action_list[t] for t in track_idx]
        #         # e_s_a[s_a_list[-1]] += 1
        #         # S_lambda.N_s_a[s_a_list[-1]] += 1

        #         # for s_a in s_a_list:
        #         #     S_lambda.value_action_function[
        #         #         s_a] = S_lambda.value_action_function.get(s_a) or 0
        #         #     S_lambda.value_action_function[
        #         #         s_a] += delta * e_s_a[s_a] / S_lambda.N_s_a[s_a]
        #         #     e_s_a[s_a] *= S_lambda.gamma * S_lambda.lambda_sarsa
        #         del_loc += [loc]
        # for loc in del_loc:
        #     del s_a_track[loc]

        # pickling for persisting Q_sa over many episodes
        with open('Sarsa_Q_sa_l' + str(lam) + '.pickle', 'wb') as fout:
            pickle.dump(S_lambda.value_action_function, fout)
        with open('N_s_a_l' + str(lam) + '.pickle', 'wb') as fout:
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
    with open('Sarsa_Q_sa_l' + str(lam) + '.pickle', 'wb') as fout:
        pickle.dump(S_lambda.value_action_function, fout)
    with open('N_s_a_l' + str(lam) + '.pickle', 'wb') as fout:
        pickle.dump(S_lambda.N_s_a, fout)

# get_state function should depend on the value-function used (maybe imported?)
# Example for state = site.strength:


def get_state(location):
    site = gameMap.getSite(location)
    state = site.strength
    return state
