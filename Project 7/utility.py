"""
CS 121: Language shifts

Utility functions for working with grids.
"""

import os
import sys

ALLOWED_VALUES = (0, 1, 2)

def read_grid(filename, allowed=ALLOWED_VALUES):
    """
    Read a grid from a text file.

    Input:
      filename (string): the name of the grid file

    Returns (tuple): 
      (list of list of ints): the grid
      (list of tuples): the community centers
    """

    if not os.path.isfile(filename):
        print("File not found:" + filename)
        sys.exit(0)

    with open(filename) as f:
        grid = []
        centers = []

        # get the grid
        N = f.readline()
        N = int(N)

        for row in range(N):
            line = f.readline()
            line = line.split()

            for i in range(N):
                line[i] = int(line[i])

            # check elements in the row
            if not check_row(N, line, row, allowed):
                print("Row {} has values other than {}").format(row, ",".join(allowed))
                print(row)
                sys.exit(0)

            grid.append(line)

        if not grid:
            print("Empty file")
            sys.exit(0)

        # get the community centers
        num_centers = f.readline()
        num_centers = int(num_centers)

        for row in range(num_centers):
            line = f.readline()
            line = line.split()

            i = int(line[0])
            j = int(line[1])

            # check location of community centers
            if (i < 0) or (j < 0) or (N <= i) or (N <= i):
                print("Center at invalid location: ({}, {})".format(i, j))
            
            location = (i, j)
            distance = int(line[2])

            centers.append((location, distance))

    return grid, centers

def print_grid(grid):
    """
    Print the grid.

    Inputs:
      grid (list of list of ints): the grid

    Returns: Nothing, prints the grid
    """

    print("N:", len(grid))
    for row in grid:
        print(row)

def check_row(N, row, i, allowed=ALLOWED_VALUES):
    """
    Check that there are N ALLOWED_VALUES in the ith row of the grid

    Inputs:
      N (int): expected length
      row (list of ints): a row of the grid
      i (int): the row's line number

    Returns: True if the row is valid, False otherwise
    """

    # check that the row is the right length
    assert len(row) == N, \
        "Row is the wrong length"

    # check that the row contains allowed values
    if set(row) - set(allowed) != set():
        return False

    return True

def is_grid(grid, allowed=ALLOWED_VALUES):
    """
    Check that the grid is a list of length N where each element is
    a list of length N.
    Check that rows contain allowed values in small grids.

    Inputs:
      grid (list of lists of ints): the grid
    
    Returns: True if the row is value, False otherwise
    """
    
    biggest_small_grid = 20

    # check that the grid is a nonempty list
    if not isinstance(grid, list):
        return False
    if not grid:
        return False

    N = len(grid)
    if N <= biggest_small_grid:
        # check each row for small grids
        for row in grid:
            if not isinstance(row, list) or len(row) != N:
                return False
            for home in row:
                if home not in allowed:
                    return False

    else:
        # otherwise, check row lengths
        for row in grid:
            if not isinstance(row, list) or len(row) != N:
                return False

    return True

def find_difference(grid1, grid2):
    """
    Find the first difference in two grids

    Input:
      grid1 (list of lists of ints): first grid
      grid2 (list of lists of ints): second grid

    Returns: A location (int, int) where grid1 and grid2
      differ, None otherwise
    """

    # check grid contents
    assert is_grid(grid1) and is_grid(grid2), \
        "Grids are not lists of lists of ints"

    # check grid dimensions
    assert len(grid1) == len(grid2), \
        "Grids do not have the same number of rows"

    assert len(grid1) == len(grid2), \
        "Grids do not have the same number of columns"

    # find a difference
    for i, row in enumerate(grid1):
        for j, value1 in enumerate(row):
            value2 = grid2[i][j]
            if value1 != value2:
                return (i, j)

    # or return None
    return None