from numpy.random import choice, randint, uniform
from utils.block_utils import Blocks, ORIENTATIONS, block_directions, move_coordinate, ClientHandler, Orientation, \
    BlockType, OBSIDIAN, REDSTONE_BLOCK, GLASS, COBBLESTONE, BRICK_BLOCK, SLIME, COAL_BLOCK, LAPIS_BLOCK
from typing import List
from copy import deepcopy
from numpy.random import randint

ALLOWED_SIDES = [ORIENTATIONS[0], ORIENTATIONS[1], ORIENTATIONS[2], ORIENTATIONS[3], ORIENTATIONS[4], ORIENTATIONS[5]] #allow all direction (N,S,E,W,UP,DOWN)
ALLOWED_BLOCKS = [REDSTONE_BLOCK, GLASS, SLIME]


class Node:
    """basic node structure for graph representation of a block and its neighbors """

    def __init__(self, block_type_id, orientation, coordinate):
        self.block_type = block_type_id
        self.orientation = orientation
        self.neighbors = []
        self.coordinate = coordinate
        self.prediction = []

    ALLOWED_BLOCKS_NEW = []



def set_new_block_types(pop, fittest, mutation_prob):

    allowed_blocks_new = []
    for f in fittest:
        allowed_blocks_new.append(f.block_type)

    for p in pop:
        if uniform() <= mutation_prob:
            p.block_type = choice(ALLOWED_BLOCKS)
        else:
            p.block_type = allowed_blocks_new[randint(0,len(allowed_blocks_new))]

    Node.ALLOWED_BLOCKS_NEW = allowed_blocks_new

    return pop

def find_neighbors(pop):
    for p in pop:
        for side in ORIENTATIONS:
            coord = move_coordinate(p.coordinate, side)
            for _p in pop:
                if _p.coordinate == coord:
                    p.neighbors.append(_p)
                    p.prediction.append(None)
    return pop


def predict_neighbors(pop, generation, mutation_prob):

    for p in pop:
        for i in range(len(p.prediction)):
            if generation == 0 or uniform() > 1 - mutation_prob:
                p.prediction[i] = choice(ALLOWED_BLOCKS)
            else:
                p.prediction[i] = choice(Node.ALLOWED_BLOCKS_NEW)
    return pop


def random_init(coordinate):
    rand_block_type = choice(ALLOWED_BLOCKS)
    rand_orientation = randint(0, len(ORIENTATIONS))
    node = Node(rand_block_type, rand_orientation, coordinate)

    return node
