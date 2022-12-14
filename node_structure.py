from numpy.random import choice, randint, uniform
from utils.block_utils import Blocks, ORIENTATIONS, block_directions, move_coordinate, ClientHandler, Orientation, \
    BlockType, OBSIDIAN, REDSTONE_BLOCK, GLASS, COBBLESTONE, BRICK_BLOCK, SLIME, COAL_BLOCK, LAPIS_BLOCK
from action_network import *
from prediction_network import *
import numpy as np

ALLOWED_SIDES = [ORIENTATIONS[0], ORIENTATIONS[1], ORIENTATIONS[2], ORIENTATIONS[3], ORIENTATIONS[4], ORIENTATIONS[5]] #allow all direction (N,S,E,W,UP,DOWN)
ALLOWED_BLOCKS = [REDSTONE_BLOCK, LAPIS_BLOCK, SLIME, COBBLESTONE]


class Node:
    """basic node structure for graph representation of a block and its neighbors """

    def __init__(self, block_type_id, orientation, coordinate):
        self.block_type = block_type_id
        self.orientation = orientation
        self.neighbors = []
        self.coordinate = coordinate
        self.prediction_network = None
        self.action_network = None

    def predict(self):
        list = []
        for n in self.neighbors:
            norm = (n.block_type-min(ALLOWED_BLOCKS))/(max(ALLOWED_BLOCKS)-min(ALLOWED_BLOCKS)) #normalize
            list.append(norm)
        pred = self.prediction_network.input(np.array(list))
        print(pred*(max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))+min(ALLOWED_BLOCKS))
        return pred*(max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))+min(ALLOWED_BLOCKS) #de-normalize

    def action(self):
        list = []
        for n in self.neighbors:
            norm = (n.block_type-min(ALLOWED_BLOCKS))/(max(ALLOWED_BLOCKS)-min(ALLOWED_BLOCKS)) #normalize
            list.append(norm)
        act = self.action_network.input(np.array(list))
        print(act*(max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))+min(ALLOWED_BLOCKS))
        return act*(max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))+min(ALLOWED_BLOCKS) #de-normalize


def set_new_block_types(pop, fittest, mutation_prob):

    return None


def find_neighbors(pop):
    for p in pop:
        for block in p:
            for side in ORIENTATIONS:
                coord = move_coordinate(block.coordinate, side)
                for _block in p:
                    if _block.coordinate == coord:
                        block.neighbors.append(_block)
    return pop

def initialize_networks(pop):
    for p in pop:
        for block in p:
            block.prediction_network = PredictionNetwork(len(block.neighbors),len(block.neighbors)+1, 1, lambda x : abs(x))
            block.action_network = ActionNetwork(len(block.neighbors),len(block.neighbors)+1, 1, lambda x : abs(x))

    return pop


def random_init(coordinate):
    rand_block_type = choice(ALLOWED_BLOCKS)
    rand_orientation = randint(0, len(ORIENTATIONS))
    node = Node(rand_block_type, rand_orientation, coordinate)
    return node
