#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
A coin flip module
"""
import sys
import random

progname = 'coin'

def main(args):
    """The program entry point."""

    random.seed()

    r = random.randint(1, 2)
    if (r%2) == 0:
        print '>Heads'
    else:
        print '>Tails'
    return

if __name__ == '__main__':
    main(sys.argv[1:])
