from node_structure import random_init, find_neighbors, initialize_networks, set_new_block_types, Node
from utils.block_utils import ClientHandler
from evaluation import evaluate

from operator import itemgetter
from numpy.random import uniform, randint
import sys
import time
sys.setrecursionlimit(10000)

start_coord = (150, 4, 0)
pop_number = 6
cage_size = (5,7)


def initialize():

    individual_list = []

    i = 0
    while i <= pop_number*cage_size[0]:
        block_list = []
        for j in range(cage_size[0]):
            for k in range(cage_size[1]):
                node = random_init((start_coord[0]+i+j, start_coord[1], start_coord[2]+k))
                block_list.append(node)
        individual_list.append(block_list)

        i = i + cage_size[0] +1

    return individual_list


def show_population(population, block_buffer: ClientHandler):
    for i in population:
        for p in i:
            block_buffer.add_block(p.coordinate, p.orientation, p.block_type)
    block_buffer.send_to_server()


def evolution(generations=1000, mutation_prob=0.1, parent_cuttoff_ratio=0.05):

    population = initialize()
    block_buffer = ClientHandler()

    show_population(population, block_buffer)

    time.sleep(10)

    for generation in range(generations):

        print('Generation', generation)
        if generation == 0:
            population = find_neighbors(population)
            population = initialize_networks(population)

        for p in population:
            for block in p:
                block.predict()
"""
        population = predict_neighbors(population, generation, mutation_prob)
        ev = lambda p: evaluate(p)
        fitness_values = list(map(ev,population))

        pop_x_fitness = zip(fitness_values, population)
        pop_x_fitness= sorted(pop_x_fitness, key=itemgetter(0), reverse=False)
        _ , sorted_pop = map(list, zip(*pop_x_fitness))

        fittest = sorted_pop[-int(parent_cuttoff_ratio * pop_number):]

        new_generation = set_new_block_types(population, fittest, mutation_prob)
        population = new_generation
        show_population(population, block_buffer)

        time.sleep(1)
"""

if __name__ == "__main__":
    evolution(generations=1000, mutation_prob=0.01)



