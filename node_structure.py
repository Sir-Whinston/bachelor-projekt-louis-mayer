from numpy.random import choice, randint, uniform, random
from utils.block_utils import Blocks, ORIENTATIONS, block_directions, move_coordinate, ClientHandler, Orientation, \
    BlockType, OBSIDIAN, REDSTONE_BLOCK, GLASS, COBBLESTONE, BRICK_BLOCK, SLIME, COAL_BLOCK, LAPIS_BLOCK, PISTON, \
    GLOWSTONE, GOLD_BLOCK, GRASS, GRAVEL
from action_network import *
from prediction_network import *
import numpy as np

ALLOWED_BLOCKS = [GLASS, REDSTONE_BLOCK, COAL_BLOCK, LAPIS_BLOCK, COBBLESTONE]


class Node:
    """basic node structure for graph representation of a block and its neighbors """

    def __init__(self, block_type_id, orientation, coordinate):
        self.block_type = block_type_id
        self.orientation = orientation
        self.neighbors = []
        self.coordinate = coordinate
        self.prediction_network = None
        self.action_network = None
        self.score = 0.0

    def predict(self):
        list = [0, 0, 0, 0]
        i = 0
        for n in self.neighbors:
            # norm = (n.block_type - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))  # normalize
            list[i] = n.block_type
            i = i + 1
        pred = self.prediction_network.input(np.array([[list[0]], [list[1]], [list[2]], [list[3]]]))
        denorm = pred * (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS)) + min(ALLOWED_BLOCKS)  # de-normalize
        result = find_nearest(ALLOWED_BLOCKS, denorm)
        return result

    def action(self):
        list = [0, 0, 0, 0]
        i = 0
        for n in self.neighbors:
            # norm = (n.block_type - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))  # normalize
            list[i] = n.block_type
            i = i + 1

        pred = self.action_network.input(np.array([[list[0]], [list[1]], [list[2]], [list[3]]]))
        denorm = pred * (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS)) + min(ALLOWED_BLOCKS)  # de-normalize
        result = find_nearest(ALLOWED_BLOCKS, denorm)  # find corresponding block
        return result


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def set_new_block_types(pop, action_list):
    i = 0
    for p in pop:
        for block in p:
            block.block_type = action_list[i]
            i = i + 1

    return pop


def find_neighbors(pop):
    for p in pop:
        for block in p:
            for side in ORIENTATIONS:
                coord = move_coordinate(block.coordinate, side)
                for _block in p:
                    if _block.coordinate == coord:
                        block.neighbors.append(_block)
    return pop


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def initialize_networks(pop):
    for p in pop:
        predict = PredictionNetwork(4, 5, 1, lambda x: sigmoid(x))
        act = ActionNetwork(4, 5, 1, lambda x: sigmoid(x))
        for block in p:
            block.prediction_network = predict
            block.action_network = act
    return pop


def assign_new_networks(individual, sorted_fitness, sorted_population, mutation_prob):
    """Implemenation of a 'wheel of fortune' to determine the new networks for an individual.
    All existing individuals and their networks are taken into account. The fitter an individual, the higher
     its chance to copy its network onto another individual. The copied networks might mutate before being
     assigned to the individual"""

    s = sum(sorted_fitness)
    uni = uniform()
    old_max = 0.0

    for i in range(len(sorted_fitness)):
        if old_max < uni <= (sorted_fitness[i] / s + old_max):
            pred_network = sorted_population[i][0].prediction_network
            act_network = sorted_population[i][0].action_network
            break
        old_max = old_max + sorted_fitness[i] / s

    if pred_network != individual[0].prediction_network:  # only assign network copy if new network is not old network
        genomeAction = act_network.toGenome()
        genomePrediction = pred_network.toGenome()

        # mutate
        genomeAction = [x if random() >= mutation_prob else x + uniform(-0.4, 0.4) for x in genomeAction]
        genomePrediction = [x if random() >= mutation_prob else x + uniform(-0.4, 0.4) for x in
                            genomePrediction]

        copy_act = ActionNetwork(4, 5, 1, lambda x: sigmoid(x))
        copy_pred = PredictionNetwork(4, 5, 1, lambda x: sigmoid(x))
        copy_act.fromGenome(numpy.array(genomeAction))
        copy_pred.fromGenome(numpy.array(genomePrediction))

        for block in individual:
            block.prediction_network = copy_pred
            block.action_network = copy_act


def replaceNetworks(individual):
    print('replace network')
    # genomeAction = individual[0].action_network.toGenome()
    # genomePrediction = individual[0].prediction_network.toGenome()

    new_act = ActionNetwork(4, 5, 1, lambda x: sigmoid(x))
    new_pred = PredictionNetwork(4, 5, 1, lambda x: sigmoid(x))

    for block in individual:
        block.prediction_network = new_pred
        block.action_network = new_act


def random_init(coordinate):
    rand_block_type = choice(ALLOWED_BLOCKS)
    rand_orientation = randint(0, len(ORIENTATIONS))
    node = Node(rand_block_type, rand_orientation, coordinate)
    return node
