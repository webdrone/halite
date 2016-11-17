'''
Assignment, Reinforcement Learning, UCL 2015
Michalis Michaelides

Easy 21 -- Environment

Requires python3 as well as the packages imported below.
'''
# from learning_methods import State
# from learning_methods import card_draw
# from learning_methods import bust
from learning_methods import MonteCarlo
from learning_methods import SarsaLambda
from learning_methods import SarsaLambdaLFA
import subprocess


def step(state, action):
    state_prime = state
    # state_prime = State()
    # state_prime.dealer = int(state.dealer)
    # state_prime.player = int(state.player)
    # state_prime.turn = state.turn
    # state_prime.terminal = bool(state.terminal)

    reward = 0

    state_prime.turn += 1
    if action == "hit":
        state_prime.player += card_draw()
        if bust(state_prime.player):
            state_prime.terminal = True
            reward = -1
            return state_prime, reward
    elif action == "stick":
        state_prime.terminal = True
        while (state_prime.dealer < 17):
            state_prime.dealer += card_draw()
            if bust(state_prime.dealer):
                reward = 1
                return state_prime, reward

        if state_prime.dealer < state_prime.player:
            reward = 1
        elif state_prime.dealer > state_prime.player:
            reward = -1
    else:
        print("Invalid action.")

    return state_prime, reward


if __name__ == '__main__':

    # action, "hit" or "stick"

    '''
    # Monte Carlo (question 2)
    print("Starting Monte Carlo with epsilon-greedy policy.")
    MCC = MonteCarlo(step, actions)
    MCC_Q_sa = MCC.run(N=3000000)
    # print(MCC.value_action_function)
    V = MCC.get_optimum_value_function()
    with open("MCC_data.csv", 'w') as f:
        for row in V:
            f.write(", ".join(str(i) for i in row))
            f.write(" \n")
    '''

    # Sarsa Lambda (question 3)
    print("Starting SARSA episodes.")
    MSE_Sarsa_MCC = []
    n_episodes = 1000

    for i in range(n_episodes):
        subprocess.run('runGame.sh', shell=True)


        # V = S_lambda.get_optimum_value_function()
        # with open("S_lambda_data"+str(l)+".csv", 'w') as f:
        #     for row in V:
        #         f.write(", ".join(str(i) for i in row))
        #         f.write(" \n")

        with open('Sarsa_Q_sa_l' + str(l) + '.pickle', 'wb') as fout:
            pickle.dump(Sarsa_Q_sa, fout)

    # with open("MSE_Sarsa_MCC.csv", 'w') as f:
    #     for i, l in enumerate(lambdas):
    #         line = [l, MSE_Sarsa_MCC[i]]
    #         f.write(", ".join(str(e) for e in line))
    #         f.write(" \n")

    print("Starting SARSA lambda 0 and 1.")
    lambdas = [0, 1]
    for l in lambdas:
        MSE_epi = []
        S_lambda = SarsaLambda(step, actions, lambda_sarsa=l)
        for epi in range(n_episodes):
            Sarsa_Q_sa = S_lambda.run_episode()
            MSE_epi.append(0)
            for s_a in Sarsa_Q_sa.keys():
                MSE_epi[-1] += (Sarsa_Q_sa[s_a] - MCC_Q_sa[s_a])**2

        with open("MSE_episodes" + str(l) + ".csv", 'w') as f:
            for epi in range(n_episodes):
                line = [epi, MSE_epi[epi]]
                f.write(", ".join(str(e) for e in line))
                f.write(" \n")

    '''
    # Sarsa Lambda with LFA (question 4)
    print("Starting SARSA LFA episodes.")
    MSE_SarsaLFA_MCC = []
    n_episodes = 1000
    lambdas = [l/10 for l in range(11)]

    for l in lambdas:
        print("Running Sarsa-lambda LFA for lambda =", l)
        S_lambda = SarsaLambdaLFA(step, actions, lambda_sarsa=l)
        Sarsa_Q_sa = S_lambda.run(N=n_episodes)
        MSE_SarsaLFA_MCC.append(0)

        for s_a in MCC_Q_sa.keys():
            MSE_SarsaLFA_MCC[-1] += (Sarsa_Q_sa[s_a] - MCC_Q_sa[s_a])**2
        # V = S_lambda.get_optimum_value_function()
        # with open("SLFA_lambda_data"+str(l)+".csv", 'w') as f:
        #     for row in V:
        #         f.write(", ".join(str(i) for i in row))
        #         f.write(" \n")

    with open("MSE_SarsaLFA_MCC.csv", 'w') as f:
        for i, l in enumerate(lambdas):
            line = [l, MSE_SarsaLFA_MCC[i]]
            f.write(", ".join(str(e) for e in line))
            f.write(" \n")

    print("Starting SARSA LFA lambda 0 and 1.")
    lambdas = [0, 1]
    for l in lambdas:
        MSE_epi = []
        S_lambda = SarsaLambdaLFA(step, actions, lambda_sarsa=l)
        for epi in range(n_episodes):
            Sarsa_Q_sa = S_lambda.run_episode()
            MSE_epi.append(0)
            for s_a in Sarsa_Q_sa.keys():
                MSE_epi[-1] += (Sarsa_Q_sa[s_a] - MCC_Q_sa[s_a])**2

        with open("MSE_LFA_episodes"+str(l)+".csv", 'w') as f:
            for epi in range(n_episodes):
                line = [epi, MSE_epi[epi]]
                f.write(", ".join(str(e) for e in line))
                f.write(" \n")
    '''
