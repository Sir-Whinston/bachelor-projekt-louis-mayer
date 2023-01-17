from node_structure import Node, ALLOWED_BLOCKS
from typing import List


def evaluate(prediction, action, individual: Node):
    norm_pred = (prediction - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))
    norm_act = (action - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))
    individual.score = individual.score + (1 - abs(norm_pred - norm_act))


def evaluate_individuals(individual):
    overall_score = 0.0
    for block in individual:
        overall_score = overall_score + block.score
        block.score = 0.0  # reset individual block scores
    return overall_score
