#!/usr/bin/python3
import sys


if __name__ == "__main__":
    team_size = int(sys.argv[1])
    _round = int(sys.argv[2])
    probability = (((team_size - 2) / (team_size - 1)) **
                   (_round - 1)) * (1 / (team_size - 1))
    print("Probability of attacking to the TP in the round {} "
          "in a team of {} is {}"
          .format(_round, team_size, probability))
