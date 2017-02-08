'''
Assignment, Reinforcement Learning, UCL 2015
Michalis Michaelides

Easy 21 -- Learning methods

Requires python3 as well as the packages imported below.
'''
import random
from collections import Counter

def bust(score):
    if 1 <= score <= 21:
        return False
    else:
        return True


def card_draw(colour=None):
    card = random.randint(1, 10)
    if colour is None:
        if random.random() < (1 / 3):
            colour = 'Red'
    if colour == 'Red':
        card *= -1
    return card


class MonteCarlo:

    def __init__(self, step, actions):
        self.value_action_function = dict()
        self.N_s_a = Counter()
        self.actions = actions  # action, "hit" or "stick"
        self.step = step
        # self.gamma = 1

        s = State()
        for player_val in range(1, 22):
            for dealer_val in range(1, 11):
                s.player = player_val
                s.dealer = dealer_val
                for act in self.actions:
                    self.value_action_function[(s.get_s(), act)] = 0.

    def run(self, N=100):
        for i in range(N):
            self.run_episode()

        return self.value_action_function

    def run_episode(self):
        s = State()  # state
        a = self.actions[0]  # action
        r = 0  # reward
        N_0 = 100000
        N_s = 0
        epsilon = N_0 / (N_0 + N_s)
        state_action_list = []

        while not s.terminal:
            N_s = sum([self.N_s_a[(s.get_s(), act)] for act in self.actions])
            epsilon = N_0 / (N_0 + N_s)

            a = self.choose_action(s, epsilon)
            state_action_list.append((s.get_s(), a))
            s, r = self.step(s, a)

        for s_a in state_action_list:
            self.N_s_a[s_a] += 1
            Q = self.value_action_function[s_a]
            self.value_action_function[s_a] = Q + (r - Q) / self.N_s_a[s_a]

        return self.value_action_function

    def choose_action(self, state, epsilon):
        # pick ε-greedy action
        if random.random() < epsilon:
            act = random.choice(self.actions)
        else:
            s = state.get_s()
            poss_act = {(s, a): self.value_action_function[(s, a)]
                        for a in self.actions}
            act = max(
                poss_act, key=lambda k: (poss_act[k], random.random()))[1]
        return act

    def get_optimum_value_function(self):
        V = []  # V will be a 2-D list with  x, y, z
        s = State()
        for player_val in range(1, 22):
            for dealer_val in range(1, 11):
                s.player = player_val
                s.dealer = dealer_val
                poss_act = {(s.get_s(), a): self.value_action_function[s.get_s(), a]
                            for a in self.actions}
                act = max(
                    poss_act, key=lambda k: (poss_act[k], random.random()))[1]
                point = list(s.get_s())
                point.append(self.value_action_function[(s.get_s(), act)])

                V.append(point)
        return V


class SarsaLambda:

    def __init__(self, step, actions, gamma=1, lambda_sarsa=0, Q_sa={},
                 N_s_a=None):
        self.value_action_function = dict(Q_sa)
        self.N_s_a = N_s_a or Counter()
        self.actions = actions  # action, "hit" or "stick"
        self.step = step
        self.gamma = gamma  # default gamma = 1
        self.lambda_sarsa = lambda_sarsa  # default gamma = 0
        """
        s = State()
        for player_val in range(1, 22):
            for dealer_val in range(1, 11):
                s.player = player_val
                s.dealer = dealer_val
                for act in self.actions:
                    self.value_action_function[(s.get_s(), act)] = 0
        """

    def run(self, N=100):
        for i in range(N):
            self.run_episode()
        return self.value_action_function

    def run_episode(self):
        s = State()  # state
        r = 0  # reward
        N_0 = 100
        e_s_a = Counter()
        delta = 0
        epsilon = N_0 / (N_0 + 0)
        state_action_list = []
        a = self.choose_action(s, epsilon)

        while not s.terminal:
            state_action_list.append((s.get_s(), a))
            s, r = self.step(s, a)

            if not s.terminal:
                N_s = sum([self.N_s_a[(s.get_s(), act)]
                           for act in self.actions])
                epsilon = N_0 / (N_0 + N_s)
                a = self.choose_action(s, epsilon)

                delta = r + self.gamma * self.value_action_function[(s.get_s(), a)]\
                    - self.value_action_function[state_action_list[-1]]
            else:
                delta = r - self.value_action_function[state_action_list[-1]]

            e_s_a[state_action_list[-1]] += 1
            self.N_s_a[state_action_list[-1]] += 1

            for s_a in state_action_list:
                self.value_action_function[
                    s_a] += delta * e_s_a[s_a] / self.N_s_a[s_a]
                e_s_a[s_a] *= self.gamma * self.lambda_sarsa

        return self.value_action_function, self.N_s_a

    def choose_action(self, state, epsilon):
        # pick ε-greedy action
        if random.random() < epsilon:
            act = random.choice(self.actions)
        else:
            s = state  # .get_s()
            poss_act = {(s, a): self.value_action_function.get((s, a)) or 0
                        for a in self.actions}
            act = max(
                poss_act, key=lambda k: (poss_act[k], random.random()))[1]
        return act

    def get_optimum_value_function(self):
        V = []  # V will be a 2-D list with  x, y, z
        s = State()
        for player_val in range(1, 22):
            for dealer_val in range(1, 11):
                s.player = player_val
                s.dealer = dealer_val
                poss_act = {(s.get_s(), a): self.value_action_function[s.get_s(), a]
                            for a in self.actions}
                act = max(
                    poss_act, key=lambda k: (poss_act[k], random.random()))[1]
                point = list(s.get_s())
                point.append(self.value_action_function[s.get_s(), act])
                V.append(point)
        return V


class SarsaLambdaLFA:

    def __init__(self, step, actions, gamma=1, lambda_sarsa=0):
        self.N_s_a = Counter()
        self.actions = actions  # action, "hit" or "stick"
        self.step = step
        self.gamma = gamma  # default gamma = 1
        self.lambda_sarsa = lambda_sarsa  # default gamma = 0

        # VFA cuboids
        self.dealer_phis = [tuple(range(1, 5)), tuple(range(4, 8)),
                            tuple(range(7, 11))]
        self.player_phis = [tuple(range(1, 7)), tuple(range(4, 10)),
                            tuple(range(7, 13)), tuple(range(10, 16)),
                            tuple(range(13, 19)), tuple(range(16, 22))]
        self.phi_lambda = lambda x, ranges: True if x in ranges else False
        self.theta = [float(0)] * (len(self.dealer_phis) *
                                   len(self.player_phis) * len(self.actions))

    def phi(self, state, act):
        s_player, s_dealer = state
        phi_sa = [int(0)] * (len(self.dealer_phis) *
                             len(self.player_phis) * len(self.actions))
        i = 0
        for a_phi in self.actions:
            if act == a_phi:
                for d_phi in self.dealer_phis:
                    if self.phi_lambda(s_dealer, d_phi):
                        for p_phi in self.player_phis:
                            if self.phi_lambda(s_player, p_phi):
                                phi_sa[i] = 1
                            i += 1
                    else:
                        i += len(self.player_phis)
            else:
                i += len(self.dealer_phis) * len(self.player_phis)

        return phi_sa

    def value_action_function(self, s, a):
        phi_sa = self.phi(s, a)
        Q = sum([f * t for f, t in zip(phi_sa, self.theta)])
        return Q

    def get_value_function(self):
        V = dict()
        s = State()
        for player_val in range(1, 22):
            for dealer_val in range(1, 11):
                s.player = player_val
                s.dealer = dealer_val
                for act in self.actions:
                    V[(s.get_s(), act)] = self.value_action_function(
                        s.get_s(), act)
        return V

    def run(self, N=100):
        for i in range(N):
            self.run_episode()
        V = self.get_value_function()
        return V

    def run_episode(self):
        s = State()  # state
        r = 0  # reward
        # N_0 = 100
        e_s_a = [float(0)] * (len(self.dealer_phis) *
                              len(self.player_phis) * len(self.actions))
        delta = 0
        epsilon = 0.05
        alpha = 0.01
        state_action_list = []
        a = self.choose_action(s, epsilon)
        phi_sa = self.phi(s.get_s(), a)
        while not s.terminal:
            s_a = (s.get_s(), a)
            state_action_list.append(s_a)
            phi_sa = self.phi(s.get_s(), a)
            s, r = self.step(s, a)
            delta = r - self.value_action_function(s_a[0], s_a[1])
            if not s.terminal:
                a = self.choose_action(s, epsilon)
                delta += self.gamma * self.value_action_function(s.get_s(), a)

            e_s_a = [self.gamma * self.lambda_sarsa *
                     e + f for e, f in zip(e_s_a, phi_sa)]
            # should the + f be here ore at the beginning of the episode?
            self.theta = [
                t + alpha * delta * e for t, e in zip(self.theta, e_s_a)]
            # is this the right order or should theta update predate e?
        V = self.get_value_function()
        return V

    def choose_action(self, state, epsilon):
        # pick ε-greedy action
        if random.random() < epsilon:
            act = random.choice(self.actions)
        else:
            s = state.get_s()
            poss_act = {(s, a): self.value_action_function(s, a)
                        for a in self.actions}
            act = max(
                poss_act, key=lambda k: (poss_act[k], random.random()))[1]
        return act

    def get_optimum_value_function(self):
        V = []  # V will be a 2-D list with  x, y, z
        s = State()
        for player_val in range(1, 22):
            for dealer_val in range(1, 11):
                s.player = player_val
                s.dealer = dealer_val
                poss_act = {(s.get_s(), a): self.value_action_function(s.get_s(), a)
                            for a in self.actions}
                act = max(
                    poss_act, key=lambda k: (poss_act[k], random.random()))[1]
                point = list(s.get_s())
                point.append(self.value_action_function(s.get_s(), act))
                V.append(point)
        return V
