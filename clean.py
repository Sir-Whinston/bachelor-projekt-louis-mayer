from utils.block_utils import ClientHandler
from utils.block_utils import ORIENTATIONS, AIR

"""Set these parameters to the same values as in main.py"""
START_COORD = (10, 4, 10)
POPULATION_SIZE = 10
CAGE_SIZE = (8, 12)


def act():
    block_buffer = ClientHandler()
    for i in range(POPULATION_SIZE * (CAGE_SIZE[0] + 1)):
        for t in range(CAGE_SIZE[1]):
            block_buffer.add_block((i+START_COORD[0], 4, START_COORD[2]+t), ORIENTATIONS[0], AIR)
        block_buffer.send_to_server()


if __name__ == "__main__":
    act()
