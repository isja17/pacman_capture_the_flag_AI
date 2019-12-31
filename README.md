This was made by Sasha Valone, Elliot Tower and me, Isaac Allison.

All of our work is in the file capture.py.

This file includes two minimax q-learning agents which competed in my classes Capture the Flag tournament. 
We won 34/50 matches against our classmates AI, earning us an 100% on the project. 

The Capture the Flag Pacman game has the following rules:

1. The board is split in half such that each agent is a ghost when on their starting half.
   That is, if you are the red team, then you are a ghost when you are on the red side of the board.
   Ghost follow the same rules as they do in standard Pacman.

2. When on the enemies side of the board, you are Pacman.
   This means that you can eat the enemies food and fruit, but you can also be eaten.
   If you are eaten by a ghost, then all food you are carrying explodes around the spot of death and
   you return to your side of the board.
 
3. You must bring your food back to your side of the board to get points. 
   So, if you get eaten on the enemies side of the board, you lose all your food and thus 
   all potential points from that food. 

4. The winner is the team with the most points. That is, the team which returns the most amount of 
   food to their side of the board. 

To run this:

Go to terminal or command prompt and change your directory to wherever you placed the project.\

Run this line: 

	python capture.py -r myTeam -b baselineTeam 

The red team is my team, the blue team is a given team which we tested ours against before the tournament. 

Note: if this does not work, make sure you have Python installed. If you do, make sure your calling Python 
correctly based on how you set it in PATH.