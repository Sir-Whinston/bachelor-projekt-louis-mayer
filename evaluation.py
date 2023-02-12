from node_structure import Node, ALLOWED_BLOCKS
from typing import List


def evaluate(block: Node, pred_weight, current_type):

    points = 0
    if block.prediction_mode == 0:
        norm_pred = (block.prediction - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))
        norm_act = (block.action - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))
        points = (1 - abs(norm_pred - norm_act))

    else:
        for i in range(len(block.neighbors)):
            norm_pred = (block.prediction[i] - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))
            norm_act = (block.neighbors[i][0].action - min(ALLOWED_BLOCKS)) / (max(ALLOWED_BLOCKS) - min(ALLOWED_BLOCKS))
            points = points + (1 - abs(norm_pred - norm_act))

    # give bonus if next action (future block type) is not current block type -> encourage change
    if current_type == block.action:
        bonus = 0
    else:
        bonus = 1
        
    block.score = block.score + pred_weight*points + (1-pred_weight)*bonus


def evaluate_individuals(individual):
    overall_score = 0.0
    for block in individual:
        overall_score = overall_score + block.score
        block.score = 0.0  # reset individual block scores
    return overall_score
