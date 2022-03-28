"""
CS 121: Language shifts

Siwen Chen

Functions for language shift simulation.

This program takes the following parameters:
    grid _file (string): the name of a file containing a sample region
    R (int): neighborhood radius
    A (float): the language state transition threshold A
    Bs (list of floats): a list of the transition thresholds B to
      use in the simulation
    C (float): the language state transition threshold C
      centers (list of tuples): a list of community centers in the
      region
    max_steps (int): maximum number of steps

Example use:
    $ python3 language.py -grid_file tests/writeup-grid-with-cc.txt
	  --r 2 --a 0.5 --b 0.9 --c 1.2 --max_steps 5
While shown on two lines, the above should be entered as a single command.
"""

import copy
from os import stat
from sys import maxsize
import click
import utility
  
def computer_community_center_service_grid(grid, centers):
  """
  to know which homes are within the service distance of a community center

  Input:
  grid(list of lists): representing regions
  centers(list of tuples): represent all the community centers in a region


  Output:
  service_drid(Boolean) : True if the home is within the service distance; False otherwise
  
  """
  n = len(grid)
  service_grid = [[False for i in range(n)] for j in range(n)]
  for (center_x, center_y), R in centers:
    for x in range(max(center_x - R, 0), min(center_x + R + 1, n)):
      for y in range(max(center_y - R, 0), min(center_y + R + 1, n)):
        service_grid[x][y] = True
  
  return service_grid

def find_neighborhood_states(grid, x, y, R):
  """
  to know what state each neigborhood is

  Input:
  grid(list of lists): representing regions
  X(integer):represent the row location of the home
  Y(integer):represent the column location of the home
  R (int): neighborhood radius

  neigborhoods (list od lists): the state of the neigborhood's state
  
  """
  n = len(grid)
  neighborhoods = []
  neighbor_rows = grid[max(x-R,0):min(x+R+1,n+1)]
  for row in neighbor_rows:
    neighborhoods.extend(row[max(y-R,0):min(y+R+1,n+1)])
  return neighborhoods

def compute_engagement_level(grid, x, y, R):
  """
  determine the engagement level of a neigborhood

  Input: 

  grid(list of lists): representing regions
  X(integer):represent the row location of the home
  Y(integer):represent the column location of the home
  R (int): neighborhood radius

  engagement level (list od lists): the state of the neigborhood's engagement level

  """
  neighborhood_states = find_neighborhood_states(grid, x, y, R)
  return round(sum(neighborhood_states) / len(neighborhood_states), 2)

def compute_child_state(parent_state, parent_engagement_level, within_service_distance, thresholds):
    """
    find out child's state

    Input:
    parent_state (int): parent's state
    parent_engagement_level（int）: parent's engagement level
    within_service_distance(Boolean): wheather or not within the service distance
    thresholds(tuple):  A, B, C 

    output:
    child_state(int): child 's state

    """


    A, B, C = thresholds
    if (parent_state == 0 and parent_engagement_level <= B) or\
          (parent_state == 1 and parent_engagement_level < B) or\
          (parent_state == 2 and parent_engagement_level <= A):
      child_state = 0
    elif parent_state == 0 or\
          (parent_state == 1 and parent_engagement_level <= C) or\
          (parent_state == 2 and parent_engagement_level < B):
      child_state = 1
    else:
      child_state = 2
    if parent_state != 0 and within_service_distance: # The first statement is trivial here since the child state is non-negative
      return max(child_state, parent_state)
    else:
      return child_state

def tranmission(grid, community_center_service_grid, R, thresholds):
    """
    Input:
    grid(list of lists): representing regions
    community_center_service_drid(Boolean) : True if the home is within the service distance; False otherwise
    R (int): neighborhood radius
    thresholds(tuple):  A, B, C 
    output:
    simulate the tranmission process
    """

    n = len(grid)
    A, B, C = thresholds
    for x in range(n):
      for y in range(n):
        parent_state = grid[x][y]
        parent_engagement_level = compute_engagement_level(grid, x, y, R)
        within_service_distance = community_center_service_grid[x][y]
        child_state = compute_child_state(parent_state, parent_engagement_level, within_service_distance, thresholds)
        grid[x][y] = child_state
        
def compute_state_frequencies(grid):
    """
    compute the how many homes are in the different states
    Inputs:
    grid(list of lists of ints): the grid
    returns: frequencies for the different states
    """
    counts = [0, 0, 0]
    for row in grid:
      for state in row:
        counts[state] += 1
    return tuple(counts)

def run_simulation(grid, R, thresholds, centers, max_steps):
    """
    Do the simulation.

    Inputs:
      grid (list of lists of ints): the grid
      R (int): neighborhood radius
      thresholds (float, float, float): the language
        state transition thresholds (A, B, C)
      centers (list of tuples): a list of community centers in the
        region
      max_steps (int): maximum number of steps

    Returns: the frequency of each language state (int, int, int)
    """
    community_center_service_grid = computer_community_center_service_grid(grid, centers)
    for n in range(max_steps):
      old_grid = [row.copy() for row in grid]
      tranmission(grid, community_center_service_grid, R, thresholds)
      if grid == old_grid:
        break
    return compute_state_frequencies(grid)

def simulation_sweep(grid, R, A, Bs, C, centers, max_steps):
    """
    Run the simulation with various values of threshold B.

    Inputs:
      grid (list of lists of ints): the grid
      R (int): neighborhood radius
      A (float): the language state transition threshold A
      Bs (list of floats): a list of the transition thresholds B to
        use in the simulation
      C (float): the language state transition threshold C
      centers (list of tuples): a list of community centers in the
        region
      max_steps (int): maximum number of steps

    Returns: a list of frequencies (tuples) of language states for
      each threshold B.
    """
    list_state_frequencies = []
    for B in Bs:
      thresholds = (A, B ,C)
      state_frequencies = run_simulation([row.copy() for row in grid], R, thresholds, centers, max_steps)
      list_state_frequencies.append(state_frequencies)
    return list_state_frequencies
      



@click.command(name="language")
@click.option('--grid_file', type=click.Path(exists=True),
              default="tests/writeup-grid.txt",
              help="filename of the grid")
@click.option('--r', type=int, default=1, help="neighborhood radius")
@click.option('--a', type=float, default=0.6, help="transition threshold A")
@click.option('--b', type=float, default=0.8, help="transition threshold B")
@click.option('--c', type=float, default=1.6, help="transition threshold C")
@click.option('--max_steps', type=int, default=1,
              help="maximum number of simulation steps")
def cmd(grid_file, r, a, b, c, max_steps):
    '''
    Run the simulation.
    '''

    grid, centers = utility.read_grid(grid_file)
    print_grid = len(grid) < 20

    print("Running the simulation...")

    if print_grid:
        print("Initial region:")
        for row in grid:
            print("   ", row)
        if len(centers) > 0:
            print("With community centers:")
            for center in centers:
                print("   ", center)

    # run the simulation
    frequencies = run_simulation(grid, r, (a, b, c), centers, max_steps)

    if print_grid:
        print("Final region:")
        for row in grid:
            print("   ", row)

    print("Final language state frequencies:", frequencies)

if __name__ == "__main__":
    cmd()