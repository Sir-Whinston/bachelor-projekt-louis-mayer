from numpy.random import choice, randint, uniform, random
from utils.block_utils import Blocks, ORIENTATIONS, block_directions, move_coordinate, ClientHandler, Orientation, \
    BlockType, OBSIDIAN, REDSTONE_BLOCK, GLASS, COBBLESTONE, BRICK_BLOCK, SLIME, COAL_BLOCK, LAPIS_BLOCK, PISTON, \
    GLOWSTONE, GOLD_BLOCK, GRASS, GRAVEL
from action_network import *
from prediction_network import *
import numpy as np

ALLOWED_BLOCKS = [GLASS, REDSTONE_BLOCK, COAL_BLOCK, LAPIS_BLOCK, COBBLESTONE]


class Node:
    """Representation of a Minecraft block as a node in a tree"""

    def __init__(self, block_type_id, orientation, coordinate, network_input_mode, neighbor_mode, noise_ratio, prediction_mode):
        self.block_type = block_type_id
        self.orientation = orientation
        self.neighbors = []
        self.coordinate = coordinate
        self.prediction_network = None
        self.action_network = None
        self.score = 0.0
        self.action = 0
        self.prediction = None
        self.network_input_mode = network_input_mode
        self.neighbor_mode = neighbor_mode
        self.noise = noise_ratio
        self.prediction_mode = prediction_mode

    def predict(self, act):
        neighbor_list = self.getNeighborBlockTypes()

        match self.network_input_mode:
            case 0:
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]]])
            case 1:
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]]])
            case 2:
                norm = (act - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]], [norm]])
            case 3:
                norm = (act - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]], [norm]])

        pred = self.prediction_network.input(input_vector)
        if self.prediction_mode == 0:
            denorm = pred * (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS)) + min(ALLOWED_BLOCKS)  # de-normalize
            result = find_nearest(ALLOWED_BLOCKS, denorm)  # find corresponding block
        else:
            result = []
            for p in pred:
                denorm = p * (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS)) + min(ALLOWED_BLOCKS)  # de-normalize
                res = find_nearest(ALLOWED_BLOCKS, denorm)  # find corresponding block
                result.append(res)

        self.prediction = result

    def act(self):
        neighbor_list = self.getNeighborBlockTypes()

        match self.network_input_mode:
            case 0:
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]]])
            case 1:
                norm = (self.action - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]],
                     [norm]])
            case 2:
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]]])
            case 3:
                norm = (self.action - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))
                input_vector = np.array(
                    [[neighbor_list[0]], [neighbor_list[1]], [neighbor_list[2]], [neighbor_list[3]],
                     [norm]])

        act = self.action_network.input(input_vector)
        denorm = act * (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS)) + min(ALLOWED_BLOCKS)  # de-normalize
        result = find_nearest(ALLOWED_BLOCKS, denorm)  # find corresponding block
        self.action = result
        return result

    def getNeighborBlockTypes(self):

        if self.neighbor_mode == 0:
            neighbor_list = [0, 0, 0, 0]
            for i in range(len(self.neighbors)):
                norm = (self.neighbors[i][0].block_type - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))  # normalize
                # with a small chance, pick a random, wrong input
                if random() <= self.noise:
                    neighbor_list[i] = (choice([x for x in ALLOWED_BLOCKS if x != self.neighbors[i][0].block_type]) - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))
                else:
                    neighbor_list[i] = norm
        elif self.neighbor_mode == 1:
            neighbor_list = []
            for n in self.neighbors:
                norm = (n[0].block_type - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))  # normalize
                if random() <= self.noise:
                    neighbor_list.append((choice([x for x in ALLOWED_BLOCKS if x != n[0].block_type])- min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS)))
                else:
                    neighbor_list.append(norm)

        return neighbor_list


"""Find the entry in an array with the smallest distance to a given value. This is used to determine which
block the NN output encodes"""
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


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
    return 1 / (1 + np.exp(-4 * x))  # -4 in order to reach all values in (0,1) with -1 <= x <= 1


def initialize_networks(pop):
    for p in pop:
        act, predict = new_networks(p[0].network_input_mode, p[0].prediction_mode)
        gen_act = act.toGenome()
        gen_pred = predict.toGenome()
        for block in p:
            a, p = new_networks(block.network_input_mode, block.prediction_mode)
            p.fromGenome(gen_pred)
            a.fromGenome(gen_act)
            block.prediction_network = p
            block.action_network = a
    return pop


def assign_new_networks(population, sorted_fitness, sorted_population, mutation_prob, new_network_prob):
    """Implementation of a 'wheel of fortune' to determine the new networks for an individual.
    All existing individuals and their networks are taken into account. The fitter an individual, the higher
     its chance to copy its network onto another individual. The copied networks might mutate before being
     assigned to the individual"""

    replacements = []
    for individual in population:
        if individual != sorted_population[len(sorted_population) - 1]:  # fittest individual remains unchanged
            uni = uniform()
            if uni <= new_network_prob:
                # save networks for possible assignment to other individuals
                replacements.append((individual, (individual[0].prediction_network, individual[0].action_network)))
                replaceNetworks(individual)
            else:
                old_max = new_network_prob
                s = (sum(sorted_fitness) - new_network_prob * sum(sorted_fitness))

                for i in range(len(sorted_fitness)):
                    if old_max < uni <= ((sorted_fitness[i] / s) + old_max):
                        # check if networks of chosen individual have previously been replaced
                        if sorted_population[i] not in [x[0] for x in replacements]:
                            pred_network = sorted_population[i][0].prediction_network
                            act_network = sorted_population[i][0].action_network
                        else:
                            # assign saved networks of chosen individual
                            for rep in replacements:
                                if rep[0] == sorted_population[i]:
                                    pred_network = rep[1][0]
                                    act_network = rep[1][1]
                        break
                    old_max = old_max + (sorted_fitness[i] / s)

                if pred_network != individual[0].prediction_network:  # only assign network copy if new network != old network
                    genomeAction = act_network.toGenome()
                    genomePrediction = pred_network.toGenome()

                    # mutate
                    genomeAction = [x if random() >= mutation_prob else x + uniform(-0.4, 0.4) for x in genomeAction]
                    genomePrediction = [x if random() >= mutation_prob else x + uniform(-0.4, 0.4) for x in
                                        genomePrediction]

                    for block in individual:
                        copy_act, copy_pred = new_networks(block.network_input_mode, block.prediction_mode)
                        copy_act.fromGenome(numpy.array(genomeAction))
                        copy_pred.fromGenome(numpy.array(genomePrediction))
                        block.prediction_network = copy_pred
                        block.action_network = copy_act


def replaceNetworks(individual):
    print('replace network')
    new_act, new_pred = new_networks(individual[0].network_input_mode, individual[0].prediction_mode)

    for block in individual:
        a, p = new_networks(block.network_input_mode, block.prediction_mode)
        p.fromGenome(new_pred.toGenome())
        a.fromGenome(new_act.toGenome())
        block.prediction_network = p
        block.action_network = a


def new_networks(network_mode, prediction_mode):
    match network_mode:
        case 0:
            act = ActionNetwork(4, 5, 1, lambda x: sigmoid(x))
            if prediction_mode == 0:
                pred = PredictionNetwork(4, 5, 1, lambda x: sigmoid(x))
            else:
                pred = PredictionNetwork(4, 5, 4, lambda x: sigmoid(x))

        case 1:
            act = ActionNetwork(5, 5, 1, lambda x: sigmoid(x))
            if prediction_mode == 0:
                pred = PredictionNetwork(4, 5, 1, lambda x: sigmoid(x))
            else:
                pred = PredictionNetwork(4, 5, 4, lambda x: sigmoid(x))
        case 2:
            act = ActionNetwork(4, 5, 1, lambda x: sigmoid(x))
            if prediction_mode == 0:
                pred = PredictionNetwork(5, 5, 1, lambda x: sigmoid(x))
            else:
                pred = PredictionNetwork(5, 5, 4, lambda x: sigmoid(x))
        case 3:
            act = ActionNetwork(5, 5, 1, lambda x: sigmoid(x))
            if prediction_mode == 0:
                pred = PredictionNetwork(5, 5, 1, lambda x: sigmoid(x))
            else:
                pred = PredictionNetwork(5, 5, 4, lambda x: sigmoid(x))

    return act, pred


def random_init(coordinate, network_input_mode, neighbor_mode, noise_ratio, prediction_mode):
    rand_block_type = choice(ALLOWED_BLOCKS)
    rand_orientation = randint(0, len(ORIENTATIONS))
    node = Node(rand_block_type, rand_orientation, coordinate, network_input_mode, neighbor_mode, noise_ratio, prediction_mode)
    return node
