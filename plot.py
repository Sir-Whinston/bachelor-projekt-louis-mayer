import pickle
import matplotlib.pyplot as plt

"""This file creates a multi-run boxplot of the fitness development. For that, fitness development lists of 
individual runs, containing fitness values for each generation, are saved in a pickle file in main.py and accessed
here. For each generation and individual run, fitness values are saved in lists that together form the final_list, 
from which a boxplot is composed."""

try:
    f = open('plot.pickle', 'rb')
    temp = pickle.load(f)
    print(len(temp))
    final_list = []

    # behaviour for long runs (> 50 generations) -> plot only every fifth generation
    if len(temp[0]) > 50:
        gen = 0
        while gen < len(temp[0]):
            data = []
            for no in range(len(temp)):
                data.append(temp[no][gen][0])
            final_list.append(data)
            gen = gen + 5  # only plot every fifth generation
    else:
        for gen in range(len(temp[0])):
            data = []
            for no in range(len(temp)):
                data.append(temp[no][gen][0])
            final_list.append(data)

    fig = plt.figure(figsize=(11, 8))

    ax = fig.add_subplot(111)

    # Creating plot
    bp = ax.boxplot(final_list)
    plt.ylim(0.55, 1)

    # section for long runs (reduces number of labels on x axis and removes ticks)
    if len(temp[0]) > 50:
        n = len(temp[0]) / 10  # Keeps only one tenth of the generation labels
        t = [i for (i, l) in enumerate(ax.xaxis.get_ticklabels())]
        v = [i * 5 for (i, l) in enumerate(ax.xaxis.get_ticklabels())]
        [l.set_visible(False) for (i, l) in enumerate(ax.xaxis.get_ticklabels()) if (i*5) % n != 0]
        plt.xticks(t, v)
        #ax.xaxis.set_ticks_position('none')

    plt.xlabel("Generation", fontsize=14)
    plt.ylabel("Fitness (score of best individual in generation)", fontsize=14)
    plt.title(f"Fitness development of {len(temp)} runs", fontsize=16)

    # show plot
    plt.show()

    # clears pickle file. Therefore, make sure to save the created plot.
    f = open('plot.pickle', 'w').close()

except:
    print('No data found. Please run main.py multiple times first. Make sure to set PLOT=True there.')
