SETUP

This section provides a detailed instruction on how to set up all required resources, run the program and observe the evolutionary process in Minecraft.

Minecraft
In order to launch Minecraft, a Minecraft license is required. This license can be obtained under https://www.minecraft.net/get-minecraft}{https://www.minecraft.net/get-minecraft. It is not necessary to purchase the deluxe collection, the basic version is sufficient. A Microsoft account is required.
After purchasing the license, follow these steps to launch the correct Minecraft version:

1. Download the Minecraft Launcher suitable for your operating system from \hyperlink{https://www.minecraft.net/download}{https://www.minecraft.net/download}
2. Execute the Launcher
3. Log in with the Microsoft account used to obtain the Minecraft license
4. Switch to the ``Installations" tab
5. Create a new installation by clicking the respective button
6. Give the installation a name and select "release 1.12.2" as version. Everything else can be left as is. Only with these settings the EvoCraft API (see Sec.~\ref{sec:api}) will work. Click ``create" to create the installation.
7. Back in the "Play" tab, select the newly created installation in the dropdown menu next to the play button and click "Play". A new window with the Minecraft home screen will open. 

Minecraft Server and the EvoCraft API

To communicate with Minecraft, it is necessary to install all components of the EvoCraft API. This also includes a plain Minecraft server running on localhost. To accomplish this step, follow the documentation under https://github.com/real-itu/Evocraft-py. It is sufficient to complete steps 1 and 2 ("Setup" and ``Starting the modded Minecraft server") in README.md.

Hint: The required eula.txt file might not be directly visible in the directory, but can usually be found using the search function of the file management system.

Program launch
Once the server is running, follow these steps to launch the program:

1. Open the Minecraft window and select ``Multiplayer"
2. Select "Direct Connect", enter ``localhost" as server adress and join the server. 
3. Clone the repository from https://github.com/Sir-Whinston/bachelor-projekt-louis-mayer
4. In main.py, set all parameters to your liking
5. In Minecraft, navigate to the start coordinates set in main.py. Moving around is possible using the W,A,S,D keys, the players current coordinates can be seen under ``XYZ" after hitting F3. 
    
Hint: Enter "teleport YourPlayerName x y z" in the terminal running the Minecraft server to get to the desired coordinates (x,y,z) directly. YourPlayerName refers to your Minecraft user name. It can be seen in the message appearing in the terminal running the server: ``YourPlayerName joined the game".
 
 6. Open another terminal, navigate to the cloned folder and execute main.py

7. Return to the Minecraft window and watch the evolutionary process. The program waits for 10 seconds before it starts, so there is enough time to switch windows.

Hint: By double-clicking the SPACE key on the keyboard, it is possible to fly around in Minecraft and therefore have a better view over the scene. Changing the altitude is possible through the SPACE and SHIFT keys.

8. If the parameter PLOT is set to "True", a graphic showing the fitness development is automatically displayed after all generations have been completed. Closing the window containing the graphic terminates the program. If PLOT is "False", no graphic is displayed.
    

Boxplot creation

After multiple program runs, it is possible to create a boxplot diagram of the fitness development of all runs - given that PLOT was always set to "True". Execute plot.py to create and view the diagram. As soon as the window containing the diagram is closed, plot.py terminates and all data is deleted. Therefore, make sure to save the boxplot for future use. 

Hint: When running several instances of main.py in parallel (e.g. in several terminals), make sure to close a created fitness diagram before the next one is opened. Otherwise, the data cannot be stored correctly and boxplot creation will not work properly.

Cleaning the Minecraft server

All blocks being placed on the Minecraft server stay until actively removed, even after a server restart. Therefore, if a removal of all blocks is necessary (e.g. for a change in POPULATION_SIZE or CAGE_SIZE), execute clean.py to remove all blocks row by row. Make sure to set the required parameters to the same value as they are set to in main.py.



PARAMETERS

Program behaviour and results are heavily influenced by different parameters that are defined in main.py. This sections provides an overview of these parameters and their effects.

1. START_COORD = (x,y,z)
    
    This parameter defines the x,y,z coordinates of the first "arenas" upper-left block. Therefore, it determines, where the scene will take place on the Minecraft server.

2. POPULATION_SIZE = x

    This parameter defines how many individual "arenas" are created. The larger x is, the higher the chance to create various different "solutions" and patterns and therefore to find solutions with a high fitness fast.
    
3. CAGE_SIZE = (w, l)

    Defines the width and length (in blocks) of an individual "arena". The larger w and l, the larger the "arenas" and the more complex the possible patterns.
    
4. CYCLES_PER_GENERATION = x
    
    Defines how many time steps, i.e. predictions and evaluations made and actions executed, one generation contains. The larger x, the longer the individual blocks can act and form patterns, before the whole "arena" gets evaluated and (possibly) receives new networks.

5. NEW_NETWORK_PROB = p
   
     During network reassignment, this defines the chance to not "pick" networks of other individuals on the wheel of fortune, but to pick completely new networks. Doing this introduces novel solutions from time to time. Therefore, it has the potential to "rescue" the program from dead-end situations where no improvement is made anymore.

6. NETWORK_INPUT_MODE = m

This parameter defines which inputs are given to the action and prediction networks. Therefore, it affects these networks outputs. Possible modes m are:

    0: The 'standard' mode. Networks only receive four inputs, which are the block types of the       blocks  four neighbors
    1: This mode adds the last taken action as a fifth input to the action network.
    2: This mode adds the result of the action network as a fifth input to the prediction network.
    3: This mode combines Mode 1 and 2. Both action and prediction networks now have five inputs.

7. PREDICTION_MODE = m

    This parameter defines how predictions are made and therefore affects how a block performs during evaluation. Possible modes m are:

    0: The prediction network of a block only has one output, with which it predicts the blocks type in the next time step.
    1: The prediction network of a block has four outputs, with which it predicts the types of the blocks neighbors in the next time step. Should a block not have four neighbors (because of NEIGHBOR_MODE = 0), predictions made for non-existing neighbors are discarded during evaluation.

8. NEIGHBOR_MODE = m
    
This parameter defines how neighbors are assigned to blocks. Therefore, it has an effect on the networks inputs (and through that, on the outputs), but also on evaluation. Possible modes m are:

    0: Neighbors are only directly adjacent blocks. Therefore, boundary and corner blocks only have 3 or 2 neighbors, respectively. During action and prediction, missing neighbors are replaced with '0' for the network input.
    1: All blocks have four neighbors. If possible, these are directly adjacent blocks. Boundary and corner blocks fill their missing neighbors with the block from the end of the arena in the opposite direction to the missing neighbor.
    
9. NOISE_RATIO = r

    This parameter defines the chance r by which a block "reads" the block type of a neighbor wrong when collecting it as input for its networks. This aims to resemble noise in a physical sensor and introduces more diversity in the patterns created by the "arenas". The chance of creating "arenas" that do not change their block types is therefore reduced.


10. PREDICTION_WEIGHT = w

This parameter defines how important the prediction is to evaluate a blocks score in comparison to the bonus given for changing block types. This weight w must be between 0 and 1. The higher w,
 the more important the prediction. The importance of the bonus for change in action therefore is 
 w_b = 1 - PREDICTION_WEIGHT. With this parameter, it is possible to define whether visible change or correct predictions are more important for the fitness of an "arena".

 
11. MUTATION_PROB = p

Defines the chance p for a single network weight to change its value during mutation.


12. GENERATIONS = x

 Defines for how many generations x (i.e. arena evaluations and network reassignments) the program should run.
 
13. PLOT = t
    
    This parameter defines whether fitness data (i.e. the fitness values for each individual "arena" and generation) shall be collected and plotted. Possible values for t are True or False. 

14. ALLOWED_BLOCKS = []

    This list, whose declaration can be found in node_structure.py, contains all block types allowed for use by the program. Due to the different looks, colours and functions of different block types, this parameter can affect the overall look and, depending on the block types (e.g. pistons, redstone blocks), also the form of the "arenas".
