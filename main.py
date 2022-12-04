from node_structure import random_init, find_neighbors, predict_neighbors, set_new_block_types, Node
from utils.block_utils import ClientHandler
from evaluation import evaluate

from operator import itemgetter
from numpy.random import uniform, randint
import sys
import time
sys.setrecursionlimit(10000)

start_coord = (400, 4, 430)
cube_size = (15, 15, 15) #BxHxT

pop_number = cube_size[0] * cube_size[1] * cube_size[2]



def generate_individual_blocks():

    block_list = []

    for i in range(cube_size[0]):
        for j in range(cube_size[1]):
            for k in range(cube_size[2]):
                node = random_init((start_coord[0]+i, start_coord[1]+j, start_coord[2]+k))
                block_list.append(node)

    return block_list


def show_population(population, block_buffer: ClientHandler):
    for p in population: block_buffer.add_block(p.coordinate, p.orientation, p.block_type)
    block_buffer.send_to_server()


def evolution(generations=1000, mutation_prob=0.1, parent_cuttoff_ratio=0.05):

    population = generate_individual_blocks()
    block_buffer = ClientHandler()

    show_population(population, block_buffer)

    time.sleep(10)

    for generation in range(generations):

        print('Generation', generation)
        if generation == 0:
            population = find_neighbors(population)

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


if __name__ == "__main__":
    evolution(generations=200, mutation_prob=0.01)



