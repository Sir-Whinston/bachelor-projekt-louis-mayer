import pickle
import matplotlib.pyplot as plt

"""This file creates a multi-run boxplot of the fitness development. For that, fitness development lists of 
individual runs, containing fitness values for each generation, are saved in a pickle file in main.py and accessed
here. For each generation and individual run, fitness values are saved in lists that together form the final_list, 
from which a boxplot is composed."""

try:
    f = open('plot.pickle', 'rb')
    temp = pickle.load(f)
    print(temp)
    final_list = []

    for gen in range(len(temp[0])):
        data = []
        for no in range(len(temp)):
            data.append(temp[no][gen][0])
        final_list.append(data)

    fig = plt.figure(figsize=(11, 8))

    ax = fig.add_subplot(111)

    # Creating plot
    bp = ax.boxplot(final_list)
    plt.ylim(0.6, 1)
    plt.xlabel("Generation", fontsize=14)
    plt.ylabel("Fitness (score of best individual in generation)", fontsize=14)
    plt.title(f"Fitness development of {len(temp)} runs", fontsize=16)

    # show plot
    plt.show()

    # clear pickle file
    f = open('plot.pickle', 'w').close()

except:
    print('No data found. Please run main.py multiple times first. Make sure to set PLOT=True there.')
