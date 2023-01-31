from node_structure import random_init, find_neighbors, initialize_networks, assign_new_networks, set_new_block_types, \
    replaceNetworks, Node
from utils.block_utils import ClientHandler
from evaluation import evaluate, evaluate_individuals

from operator import itemgetter
from numpy.random import uniform, randint
import sys
import time

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
NETWORK_INPUT_MODE = 2

"""Defines how neighbors are assigned to blocks. Possible modes are:
    0: Neighbors are only directly adjacent blocks. Therefore, boundary and corner blocks only have 3 or 2 neighbors, 
    respectively. During action and prediction, missing neighbors are replaced with '0' for the network input.
    1: All blocks have four neighbors. If possible, these are directly adjacent blocks. Boundary and corner blocks
    fill their missing neighbors with the block from the end of the arena in the opposite direction to the missing neighbor"""
NEIGHBOR_MODE = 1


def initialize():
    individual_list = []

    i = 0
    while i < POPULATION_SIZE * (CAGE_SIZE[0] + 1):
        block_list = []
        for j in range(CAGE_SIZE[0]):
            for k in range(CAGE_SIZE[1]):
                node = random_init((START_COORD[0] + i + j, START_COORD[1], START_COORD[2] + k))
                block_list.append(node)
        individual_list.append(block_list)

        i = i + CAGE_SIZE[0] + 1

    return individual_list


def show_population(population, block_buffer: ClientHandler):
    for i in population:
        for p in i:
            block_buffer.add_block(p.coordinate, p.orientation, p.block_type)
    block_buffer.send_to_server()


def evolution(generations=1000, mutation_prob=0.1, parent_cuttoff_ratio=0.05):
    population = initialize()
    block_buffer = ClientHandler()
    population = find_neighbors(population, CAGE_SIZE, NEIGHBOR_MODE)
    population = initialize_networks(population, NETWORK_INPUT_MODE)

    time.sleep(8)
    show_population(population, block_buffer)

    for generation in range(generations):
        time.sleep(1)

        print('Generation', generation)

        if generation % CYCLES_BETWEEN_EVALUATION == 0 and generation != 0:
            """evaluate individuals and form new population every *CYCLES_BETWEEN_EVALUATION* generations"""
            ev = lambda i: evaluate_individuals(i)
            fitness_values = list(map(ev, population))
            pop_x_fitness = zip(fitness_values, population)
            pop_x_fitness = sorted(pop_x_fitness, key=itemgetter(0), reverse=False)
            sorted_fitness, sorted_pop = map(list, zip(*pop_x_fitness))

            for individual in population:
                if individual != sorted_pop[len(sorted_pop) - 1]:  # fittest individual remains unchanged
                    assign_new_networks(individual, sorted_fitness, sorted_pop, mutation_prob, NEW_NETWORK_PROB)

            time.sleep(2)

        for p in population:
            for block in p:
                act = block.action()
                block.predict(act)
                evaluate(block)

        set_new_block_types(population)
        show_population(population, block_buffer)


"""
        population = predict_neighbors(population, generation, mutation_prob)
        
        ev = lambda p: evaluate(p)
        fitness_values = list(map(ev,population))
        pop_x_fitness = zip(fitness_values, population)
        pop_x_fitness= sorted(pop_x_fitness, key=itemgetter(0), reverse=False)
        _ , sorted_pop = map(list, zip(*pop_x_fitness))

        fittest = sorted_pop[-int(parent_cuttoff_ratio * POPULATION_SIZE):]

        new_generation = set_new_block_types(population, fittest, mutation_prob)
        population = new_generation
        show_population(population, block_buffer)

        time.sleep(1)
"""

if __name__ == "__main__":
    evolution(generations=121, mutation_prob=0.07)
