#!/usr/bin/python3

import sys
import math

if __name__ == "__main__":
    team_size = int(sys.argv[1])
    _round = int(sys.argv[2])
    s = 1
    if len(sys.argv) > 3:
        s = int(sys.argv[3])
    prob = 0
    for i in range(1,_round+1):
        probability = (((team_size - 2) / (team_size - 1)) **
                       (math.ceil(i/s)-1)) * (0**(i%s) / (team_size - 1))
        print("Probability of attacking to the TP in the round {} "
              "in a team of {} is {}"
              .format(i, team_size, probability))
        prob += probability
    print("Probability of attacking to the TP after {} rounds "
          "in a team of {} is {}"
          .format(_round, team_size, prob))
