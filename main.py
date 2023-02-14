from node_structure import random_init, find_neighbors, initialize_networks, assign_new_networks, set_new_block_types, \
    replaceNetworks, Node
from utils.block_utils import ClientHandler
from evaluation import evaluate, evaluate_individuals

from operator import itemgetter
from numpy.random import uniform, randint
import sys
import time

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

sys.setrecursionlimit(10000)

START_COORD = (10, 4, 10)
POPULATION_SIZE = 10
CAGE_SIZE = (8, 12)
"""If should go 3D, put Orientations up and down back into minecraft_pb2.py, line 54 _descriptor.EnumValueDescriptor(
      name='UP', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DOWN', index=5, number=5,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),"""
CYCLES_BETWEEN_EVALUATION = 10
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
PREDICTION_WEIGHT = 0.75


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


def show_population(population, block_buffer: ClientHandler):
    for i in population:
        for p in i:
            block_buffer.add_block(p.coordinate, p.orientation, p.block_type)
    block_buffer.send_to_server()


def evolution(generations=1000, mutation_prob=0.1):
    population = initialize()
    block_buffer = ClientHandler()
    population = find_neighbors(population, CAGE_SIZE)
    population = initialize_networks(population)

    time.sleep(2)
    show_population(population, block_buffer)

    fitness = []
    for generation in range(generations):
        #time.sleep(1)

        print('Time step', generation)

        if generation % CYCLES_BETWEEN_EVALUATION == 0 and generation != 0:
            """evaluate individuals and form new population every *CYCLES_BETWEEN_EVALUATION* generations"""
            ev = lambda i: evaluate_individuals(i)
            fitness_values = list(map(ev, population))
            pop_x_fitness = zip(fitness_values, population)
            pop_x_fitness = sorted(pop_x_fitness, key=itemgetter(0), reverse=False)
            sorted_fitness, sorted_pop = map(list, zip(*pop_x_fitness))

            print('Generation', int(generation / CYCLES_BETWEEN_EVALUATION))

            # give new networks to individuals trough 'wheel of fortune'-process
            assign_new_networks(population, sorted_fitness, sorted_pop, mutation_prob, NEW_NETWORK_PROB)

            # collect data for fitness plotting
            if PREDICTION_WEIGHT != 1.0:
                bonus = (1-PREDICTION_WEIGHT) * CAGE_SIZE[0] * CAGE_SIZE[1] * CYCLES_BETWEEN_EVALUATION
            else:
                bonus = 0
            if PREDICTION_MODE == 0:
                fitness.append((((sorted_fitness[len(sorted_fitness) - 1])/((PREDICTION_WEIGHT*CAGE_SIZE[0]*CAGE_SIZE[1]*CYCLES_BETWEEN_EVALUATION) + bonus)), int(generation / CYCLES_BETWEEN_EVALUATION)))
            elif PREDICTION_MODE == 1 and NEIGHBOR_MODE == 0:
                fitness.append((((sorted_fitness[len(sorted_fitness) - 1])/(PREDICTION_WEIGHT*((CAGE_SIZE[0]*CAGE_SIZE[1]*CYCLES_BETWEEN_EVALUATION*4) - (2*CAGE_SIZE[0] + 2*CAGE_SIZE[1])) + bonus)), int(generation / CYCLES_BETWEEN_EVALUATION)))
            elif PREDICTION_MODE == 1 and NEIGHBOR_MODE == 1:
                fitness.append((((sorted_fitness[len(sorted_fitness) - 1])/((PREDICTION_WEIGHT*CAGE_SIZE[0]*CAGE_SIZE[1]*CYCLES_BETWEEN_EVALUATION*4) + bonus)), int(generation / CYCLES_BETWEEN_EVALUATION)))

            time.sleep(1)

        for p in population:
            for block in p:
                act = block.act()
                block.predict(act)
            for block in p:  # evaluation has to happen after all blocks have made predictions
                current_type = block.block_type
                evaluate(block, PREDICTION_WEIGHT, current_type)

        set_new_block_types(population)
        show_population(population, block_buffer)

    # plotting of fitness development
    df = pd.DataFrame({"Generation": [f[1] for f in fitness],
                       "Fitness (score of best individual in generation)"
                       : [f[0] for f in fitness]})
    sns.lineplot(x="Generation", y="Fitness (score of best individual in generation)", data=df)
    plt.xticks(rotation=15)
    plt.title('Development of fitness')
    plt.show()


if __name__ == "__main__":
    evolution(generations=201, mutation_prob=0.05)

