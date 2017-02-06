from hlt import *
from networking import *
import random
from learning_methods import SarsaLambda
from collections import Counter
import pickle


k = 1  # the number of neighbours considered
S_lambda = []


def symmetry(state=None):
    s = tuple(state)
    print("state:", s)
    # return s, 0, None

    # check for rotation (3 rotations + 1 gets to the original)
    for rotn in range(4):
        # if s in state-action dictionary, do not attempt symmetry
        # print([key[0] for key in S_lambda.value_action_function])
        print("s:", s)
        if s[0] in [key[0] for key in S_lambda]:
            print("key:", s[0])
            return s, rotn, None

        # if not, try to find symmetry
        # check for reflection (4 reflections)
        print(s)
        for refl in range(4):
            s1 = []
            for j in range(-k, k + 1):
                for i in range(-k, k + 1):
                    if refl == 0:
                        # transpose (i, j) -> (j, i)
                        s1 += [s[0][(k + i) * (2 * k + 1) + (j + k)]]
                    elif refl == 1:
                        # transpose opp (i, j) -> (-j, -i)
                        s1 += [s[0][(k - i) * (2 * k + 1) + (-j + k)]]
                    elif refl == 2:
                        # reflect on vert (i, j) -> (-i, j)
                        s1 += [s[0][(k + j) * (2 * k + 1) + (-i + k)]]
                    elif refl == 3:
                        # reflect on hor (i, j) -> (i, -j)
                        s1 += [s[0][(k - j) * (2 * k + 1) + (i + k)]]
            # if s in state-action dictionary, do not attempt symmetry
            s1 = (tuple(s1), s[-1])
            if tuple(s1[0]) in [key[0] for key in S_lambda]:
                return s1, rotn, refl
        # rotate
        s1 = []
        for j in range(-k, k + 1):
            for i in range(-k, k + 1):
                s1 += [s[0][(k - i) * (2 * k + 1) + (j + k)]]
        s = (tuple(s1), s[-1])
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


def flatten_state(state):
    state_flat = []
    x = 1
    y = 1
    for j in range(-k, k + 1):
        for i in range(-k, k + 1):
            state_flat += [state[y + j][x + i]]
    return tuple(state_flat)


state = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
state_flat = (tuple(flatten_state(state)), 10)
print(state_flat)

state_lambda = ((9, 6, 3), (8, 5, 2), (7, 4, 1))
S_lambda = [(flatten_state(state_lambda), 10)]
print("lambda:", S_lambda)

state_sym = symmetry(state_flat)
print(state_sym)
print(NORTH, action_symmetry(NORTH, *state_sym[1:]))
print(SOUTH, action_symmetry(SOUTH, *state_sym[1:]))
print(WEST, action_symmetry(WEST, *state_sym[1:]))
print(EAST, action_symmetry(NORTH, *state_sym[1:]))
