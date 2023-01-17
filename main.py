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
POPULATION_SIZE = 8
CAGE_SIZE = (10, 14)
MAX_NETWORK_AGE = 15
CYCLES_BETWEEN_EVALUATION = 7


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
    population = find_neighbors(population)
    population = initialize_networks(population)

    time.sleep(4)
    show_population(population, block_buffer)

    for generation in range(generations):
        time.sleep(1)
        action_list = []
        print('Generation', generation)

        for p in population:
            for block in p:
                pred = block.predict()
                act = block.action()
                evaluate(pred, act, block)
                action_list.append(act)

            # replace an individuals networks if they have reached maximum age
            if p[0].prediction_network.age > MAX_NETWORK_AGE:
                replaceNetworks(p)

            p[0].prediction_network.age += 1

        population = set_new_block_types(population, action_list)
        show_population(population, block_buffer)

        if generation % CYCLES_BETWEEN_EVALUATION == 0 and generation != 0:
            """evaluate individuals and form new population every *CYCLES_BETWEEN_EVALUATION* generations"""
            ev = lambda i: evaluate_individuals(i)
            fitness_values = list(map(ev, population))

            pop_x_fitness = zip(fitness_values, population)
            pop_x_fitness = sorted(pop_x_fitness, key=itemgetter(0), reverse=False)
            sorted_fitness, sorted_pop = map(list, zip(*pop_x_fitness))

            for individual in population:
                if individual != sorted_pop[len(sorted_pop) - 1]:  # fittest individual remains unchanged
                    assign_new_networks(individual, sorted_fitness, sorted_pop, mutation_prob)

            time.sleep(2)


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
    evolution(generations=101, mutation_prob=0.05)
