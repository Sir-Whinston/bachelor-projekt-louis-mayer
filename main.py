from node_structure import random_init, find_neighbors, initialize_networks, assign_new_networks, replaceNetworks, Node
from utils.block_utils import ClientHandler
from evaluation import evaluate, evaluate_individuals

from operator import itemgetter
from numpy.random import uniform, randint
import sys
import time
import pickle

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

sys.setrecursionlimit(10000)

"""Coordinates on the Minecraft server"""
START_COORD = (10, 4, 10)

"""Defines how many individual 'arenas' are created"""
POPULATION_SIZE = 10

"""Defines how large (width x length) one individual 'arena' shall be."""
CAGE_SIZE = (8, 12)

"""Defines how many time steps, i.e. predictions and evaluations made and actions executed, one generation contains."""
CYCLES_PER_GENERATION = 20

"""Defines the chance to 'pick' a completely new network on the wheel of fortune during network reassignment."""
NEW_NETWORK_PROB = 0.05

"""Defines which inputs are given to the action and prediction networks. Possible modes are:
    0: The 'standard' mode. Networks only receive four inputs, which are the block types of the blocks four neighbors 
    1: This mode adds the last taken action as a fifth input to the action network. Prediction remains standard
    2: This mode adds the result of the action network as a fifth input to the prediction network. Action remains standard
    3: This mode combines Mode 1 and 2. Both action and prediction networks now have five inputs."""
NETWORK_INPUT_MODE = 3

"""Defines how predictions are made and therefore how a block performs during evaluation. Possible modes are:
    0: The prediction network of a block only has one output, with which it predicts the blocks type in the next time
    step.
    1: The prediction network of a block has four outputs, with which it predicts the types of the blocks neighbors in 
    the next time step. Should a block not have four neighbors (because of NEIGHBOR_MODE = 0), predictions made for non-
    existing neighbors are discarded during evaluation."""
PREDICTION_MODE = 1

"""Defines how neighbors are assigned to blocks. Possible modes are:
    0: Neighbors are only directly adjacent blocks. Therefore, boundary and corner blocks only have 3 or 2 neighbors, 
    respectively. During action and prediction, missing neighbors are replaced with '0' for the network input.
    1: All blocks have four neighbors. If possible, these are directly adjacent blocks. Boundary and corner blocks
    fill their missing neighbors with the block from the end of the arena in the opposite direction to the missing neighbor"""
NEIGHBOR_MODE = 1

"""Defines the chance by which a network gets a wrong neighbor block type as input. Resembles noise in a physical 
sensor"""
NOISE_RATIO = 0.03

"""Defines how important the prediction is to evaluate a blocks score. Must be between 0 and 1. The higher the value,
 the more important the prediction. The importance of the bonus for change in action therefore is 1 - PREDICTION_WEIGHT"""
PREDICTION_WEIGHT = 0.8

"""Defines the chance for a single network weight to change its value during mutation"""
MUTATION_PROB = 0.05

"""Defines for how many generations (i.e. arena evaluations and network reassignments) the program should run"""
GENERATIONS = 1500

"""Defines whether fitness data shall be collected and plotted. Possible settings: True or False"""
PLOT = True


"""Create all arenas as a list of lists"""
def initialize():
    individual_list = []

    i = 0
    while i < POPULATION_SIZE * (CAGE_SIZE[0] + 1):
        block_list = []
        for j in range(CAGE_SIZE[0]):
            for k in range(CAGE_SIZE[1]):
                node = random_init((START_COORD[0] + i + j, START_COORD[1], START_COORD[2] + k), NETWORK_INPUT_MODE,
                                   NEIGHBOR_MODE, NOISE_RATIO, PREDICTION_MODE)
                block_list.append(node)
        individual_list.append(block_list)

        i = i + CAGE_SIZE[0] + 1

    return individual_list


"""Sends the current population list to the Minecraft server to display"""
def show_population(population, block_buffer: ClientHandler):
    for i in population:
        for p in i:
            block_buffer.add_block(p.coordinate, p.orientation, p.block_type)
    block_buffer.send_to_server()


def evolution(generations=50, mutation_prob=0.05):
    population = initialize()
    block_buffer = ClientHandler()
    population = find_neighbors(population, CAGE_SIZE)
    population = initialize_networks(population)

    # time to switch to Minecraft tab and watch
    time.sleep(10)

    show_population(population, block_buffer)

    fitness = []
    for time_step in range(1, generations * CYCLES_PER_GENERATION + 1):

        print('Time step', time_step)

        # blocks predict and determine their next action, then get evaluated
        for p in population:
            for block in p:
                act = block.act()
                block.predict(act)
            for block in p:  # evaluation has to happen after all blocks have made predictions and actions
                current_type = block.block_type
                block.block_type = block.action  # update block type according to action determined by block
                evaluate(block, PREDICTION_WEIGHT, current_type)

        # show changed situation in Minecraft
        show_population(population, block_buffer)

        if time_step % CYCLES_PER_GENERATION == 0:
            """evaluate individuals and form new population every *CYCLES_PER_GENERATION* time_steps"""

            ev = lambda i: evaluate_individuals(i)
            fitness_values = list(map(ev, population))
            pop_x_fitness = zip(fitness_values, population)
            pop_x_fitness = sorted(pop_x_fitness, key=itemgetter(0), reverse=False)
            sorted_fitness, sorted_pop = map(list, zip(*pop_x_fitness))
            print('End of generation', int(time_step / CYCLES_PER_GENERATION))

            # give new networks to individuals trough 'wheel of fortune' process
            assign_new_networks(population, sorted_fitness, sorted_pop, mutation_prob, NEW_NETWORK_PROB)

            if PLOT:
                # collect data for fitness plotting
                fitness.append((((sorted_fitness[len(sorted_fitness) - 1]) / (CAGE_SIZE[0] * CAGE_SIZE[1] *
                                                                              CYCLES_PER_GENERATION)),
                                    int(time_step / CYCLES_PER_GENERATION)))

            time.sleep(1)

    if PLOT:
        # save fitness development of this single run in pickle file to access when creating boxplot through plot.py
        try:
            f = open('plot.pickle', 'rb')
            temp = pickle.load(f)
        except:
            temp = []

        f = open('plot.pickle', 'wb')
        temp.append(fitness)
        pickle.dump(temp, f)

        # plotting of fitness development of this single run
        df = pd.DataFrame({"Generation": [f[1] for f in fitness],
                           "Fitness (score of best individual in generation)"
                           : [f[0] for f in fitness]})
        sns.lineplot(x="Generation", y="Fitness (score of best individual in generation)", data=df)
        plt.ylim(0.5, 1)
        plt.xticks(rotation=15)
        plt.title('Development of fitness')
        plt.show()


if __name__ == "__main__":
    evolution(generations=GENERATIONS, mutation_prob=MUTATION_PROB)
