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

    def __init__(self, block_type_id, orientation, coordinate, network_input_mode, neighbor_mode, noise_ratio):
        self.block_type = block_type_id
        self.orientation = orientation
        self.neighbors = []
        self.coordinate = coordinate
        self.prediction_network = None
        self.action_network = None
        self.score = 0.0
        self.last_action = 0
        self.prediction = None
        self.mode = network_input_mode
        self.neighbor_mode = neighbor_mode
        self.noise = noise_ratio


    def predict(self, act):

        neighbor_list = self.getNeighborBlockTypes()

        match self.mode:
            case 0:
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]]])
            case 1:
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]]])
            case 2:
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]], [act]])
            case 3:
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]], [act]])

        pred = self.prediction_network.input(input_vector)

        denorm = pred * (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS)) + min(ALLOWED_BLOCKS)  # de-normalize
        result = find_nearest(ALLOWED_BLOCKS, denorm)  # find corresponding block

        self.prediction = result

    def action(self):

        neighbor_list = self.getNeighborBlockTypes()

        match self.mode:
            case 0:
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]]])
            case 1:
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]],
                     [self.last_action]])
            case 2:
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]]])
            case 3:
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]],
                     [self.last_action]])

        act = self.action_network.input(input_vector)
        denorm = act * (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS)) + min(ALLOWED_BLOCKS)  # de-normalize
        result = find_nearest(ALLOWED_BLOCKS, denorm)  # find corresponding block
        self.last_action = result
        return result

    def getNeighborBlockTypes(self):

        if self.neighbor_mode == 0:
            neighbor_list = [0, 0, 0, 0]
            for i in range(len(self.neighbors)):
                # norm = (self.neighbors[i][0].block_type - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))  # normalize
                if uniform() <= self.noise:
                    neighbor_list[i] = choice([x for x in ALLOWED_BLOCKS if x != self.neighbors[i][0].block_type])
                else:
                    neighbor_list[i] = self.neighbors[i][0].block_type
        elif self.neighbor_mode == 1:
            neighbor_list = []
            for n in self.neighbors:
                # norm = (n[0].block_type - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))  # normalize
                if random() <= self.noise:
                    neighbor_list.append(choice([x for x in ALLOWED_BLOCKS if x != n[0].block_type]))
                else:
                    neighbor_list.append(n[0].block_type)

        return neighbor_list


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def set_new_block_types(pop):
    for p in pop:
        for block in p:
            block.block_type = block.last_action


def find_neighbors(pop, cage_size):
    for p in pop:
        # find neighbors for each block
        for block in p:
            for side in ORIENTATIONS:
                coord = move_coordinate(block.coordinate, side)
                for _block in p:
                    if _block.coordinate == coord:
                        block.neighbors.append((_block, side))
            if block.neighbor_mode == 1:
                # if block is at edge or corner of arena, then he currently has only two or three neighbors
                if len(block.neighbors) < 4:
                    # get sides of block that currently have an assigned neighbor
                    sides_with_neighbor = [x[1] for x in block.neighbors]
                    for side in ORIENTATIONS:
                        # get sides that currently have no assigned neighbor
                        if side not in sides_with_neighbor:
                            # if north or south side are missing
                            if side == 0 or side == 2:
                                coord = move_coordinate(block.coordinate, side, delta=-(cage_size[1] - 1))
                            # if west or east side are missing
                            else:
                                coord = move_coordinate(block.coordinate, side, delta=-(cage_size[0] - 1))
                            # find 'neighbor' blocks from other side of arena and add them to neighbor list
                            for _block in p:
                                if _block.coordinate == coord:
                                    block.neighbors.append((_block, side))
    return pop


def sigmoid(x):
    return 1 / (1 + np.exp(-3 * x))


def initialize_networks(pop):
    for p in pop:
        act, predict = new_networks(p[0].mode)
        for block in p:
            block.prediction_network = predict
            block.action_network = act
    return pop


def assign_new_networks(individual, sorted_fitness, sorted_population, mutation_prob, new_network_prob):
    """Implementation of a 'wheel of fortune' to determine the new networks for an individual.
    All existing individuals and their networks are taken into account. The fitter an individual, the higher
     its chance to copy its network onto another individual. The copied networks might mutate before being
     assigned to the individual"""

    uni = uniform()
    if uni <= new_network_prob:
        replaceNetworks(individual)

    else:
        old_max = new_network_prob
        s = (sum(sorted_fitness) - new_network_prob * sum(sorted_fitness))

        for i in range(len(sorted_fitness)):
            if old_max < uni <= ((sorted_fitness[i] / s) + old_max):
                pred_network = sorted_population[i][0].prediction_network
                act_network = sorted_population[i][0].action_network
                break
            old_max = old_max + (sorted_fitness[i] / s)

        if pred_network != individual[
            0].prediction_network:  # only assign network copy if new network is not old network
            genomeAction = act_network.toGenome()
            genomePrediction = pred_network.toGenome()

            # mutate
            genomeAction = [x if random() >= mutation_prob else x + uniform(-0.4, 0.4) for x in genomeAction]
            genomePrediction = [x if random() >= mutation_prob else x + uniform(-0.4, 0.4) for x in
                                genomePrediction]

            for block in individual:
                copy_act, copy_pred = new_networks(block.mode)
                copy_act.fromGenome(numpy.array(genomeAction))
                copy_pred.fromGenome(numpy.array(genomePrediction))
                block.prediction_network = copy_pred
                block.action_network = copy_act


def replaceNetworks(individual):
    print('replace network')
    new_act, new_pred = new_networks(individual[0].mode)

    for block in individual:
        block.prediction_network = new_pred
        block.action_network = new_act


def new_networks(mode):
    match mode:
        case 0:
            act = ActionNetwork(4, 5, 1, lambda x: sigmoid(x))
            pred = PredictionNetwork(4, 5, 1, lambda x: sigmoid(x))
        case 1:
            act = ActionNetwork(5, 5, 1, lambda x: sigmoid(x))
            pred = PredictionNetwork(4, 5, 1, lambda x: sigmoid(x))
        case 2:
            act = ActionNetwork(4, 5, 1, lambda x: sigmoid(x))
            pred = PredictionNetwork(5, 5, 1, lambda x: sigmoid(x))
        case 3:
            act = ActionNetwork(5, 5, 1, lambda x: sigmoid(x))
            pred = PredictionNetwork(5, 5, 1, lambda x: sigmoid(x))

    return act, pred


def random_init(coordinate, network_input_mode, neighbor_mode, noise_ratio):
    rand_block_type = choice(ALLOWED_BLOCKS)
    rand_orientation = randint(0, len(ORIENTATIONS))
    node = Node(rand_block_type, rand_orientation, coordinate, network_input_mode, neighbor_mode, noise_ratio)
    return node
