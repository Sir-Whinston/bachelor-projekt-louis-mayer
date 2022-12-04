from node_structure import Node
from typing import List


def evaluate(individual):
    pred = individual.prediction
    neigh = individual.neighbors


    fitness = 0

    for i in range(len(pred)):
        if pred[i] == neigh[i].block_type:
           fitness = fitness + 1

    return fitness



