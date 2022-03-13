import math
import copy
import sys
import itertools

# GLOBALS
reccursion_depth = 0
dead_end_counter = 0
assumption_counter = 0
solution_counter = 0

# OPTIONS
PRINT_STEPS = True
PRINT_STEP_BOARD = True
PRINT_ASSUMPTION = True
ASSUME_LOWEST_FIRST = True # When True, assumptions will be made on cells with smallest possible choices, else Left2Right-Top2Down.
FIRST_SOLUTION_ONLY = False

def initiate_board(problem):
    board_pos = [[[i for i in range(1,10)] for i in range(9)] for i in range(9)]
    for i,row in enumerate(problem):
        for j,cell in enumerate(row):
            if cell > 0:
                board_pos[i][j] = [cell]
    return board_pos

def remove_invalid(board_pos):
    if PRINT_STEPS: print("Removing Invalid Values..")
    org_length = board_length(board_pos) #Used to check if Rule based algorithm made progress.
    for i,row in enumerate(board_pos):
        for j,cell in enumerate(row):
            if len(cell) == 1:
                for e in range(9):
                    # 1. Remove from Row
                    if e != j:
                        try:
                            board_pos[i][e].remove(cell[0])
                            if len(board_pos[i][e]) == 0:
                                if PRINT_STEPS: print(f"ROW CHECK: Board is invalid at position ({i},{j})")
                                return False, False, board_pos
                            valid_col = False
                            for counter_col in range(9):
                                if cell[0] in board_pos[counter_col][e]:
                                    valid_col = True
                                    break
                            if not valid_col:
                                if PRINT_STEPS: print(f'COLUMN CHECK: Value {cell[0]} not present in column {e}! ')
                                return False, False, board_pos
                        except ValueError:
                            pass

                    # 2. Remove from Column
                    if e != i:
                        try:
                            board_pos[e][j].remove(cell[0])
                            if len(board_pos[e][j]) == 0:
                                if PRINT_STEPS: print(f"COLUMN CHECK: Board is invalid at position ({e},{j})")
                                return False, False, board_pos
                            valid_row = False
                            for counter_row in range(9):
                                if cell[0] in board_pos[e][counter_row]:
                                    valid_row = True
                                    break
                            if not valid_row:
                                if PRINT_STEPS: print(f'ROW CHECK: Value {cell[0]} not present in row {e}! ')
                                return False, False, board_pos
                        except ValueError:
                            pass

                # 3. Remove from Sector
                sector_row = math.floor((i) / 3)
                sector_col = math.floor((j) / 3)
                #print(sector_row, sector_col, ':',cell[0])
                for i_sec in range(sector_row*3, (sector_row+1)*3):
                    for j_sec in range(sector_col*3, (sector_col+1)*3):
                        if i != i_sec and j !=j_sec:
                            try:
                                board_pos[i_sec][j_sec].remove(cell[0])
                                if len(board_pos[i_sec][j_sec]) == 0:
                                    if PRINT_STEPS: print(f"SECTOR CHECK: Board is invalid at position ({i_sec},{j_sec})")
                                    return False, False, board_pos
                                # Add check here to ensure every number is an option for the Sector. Missing check will eventually lead to dead end anyways.
                            except ValueError:
                                pass
    return True, (org_length == board_length(board_pos)), board_pos


def board_length(board_pos):
     return sum((sum(map(len, row)) for row in board_pos))
    
def print_board(board_pos):
    for row in board_pos:
        print(row)
    if not isinstance(board_pos[0][0], int):
        print(f"Current Board Length: {board_length(board_pos)}")
        print(f"Current Reccursion Depth: {reccursion_depth}")
        print(f"Current Number of Dead Ends: {dead_end_counter}")
        print(f"Number of assumptions made: {assumption_counter}")

def is_solved(board_pos):
    for row in board_pos:
        for cell in row:
            if len(cell) != 1:               
                return False 
    return True



def get_next_assume_candidate(board_pos):
    assume_list = []
    possibilities = 1
    for i,row in enumerate(board_pos):
        for j,cell in enumerate(row):    
            if len(cell) > 1:
                assume_list.append([i,j,len(cell)])
                possibilities = possibilities * len(cell)

    sorted_assume = sorted(assume_list, key = lambda x: x[2]) 
    if ASSUME_LOWEST_FIRST:
        return (sorted_assume[0], possibilities)
    else:
        return (assume_list[0], possibilities)
  

def solve_sudoku(board_pos):
    global reccursion_depth
    global dead_end_counter
    global assumption_counter
    global solution_counter
        
    reccursion_depth += 1
    if PRINT_STEPS: print('reccursion depth :', reccursion_depth)
    while not is_solved(board_pos):
        if PRINT_STEPS: print('Trying to Solve by applying rules of Sudoku:')
        if PRINT_STEP_BOARD: print_board(board_pos)
        # Rule based Sudoku Solver.
        is_valid, stuck, board_pos = remove_invalid(board_pos)
        
        if not is_valid:
            dead_end_counter += 1
            assume_list, possibilities = get_next_assume_candidate(board_pos)
            if PRINT_STEPS: print(f'Dead End Number: {dead_end_counter}!!')        
            if PRINT_STEPS: print_board(board_pos)
            reccursion_depth -= 1
            return False

        # Unable to solve board with the rules of Sudoku, Need to assume a value.
        if stuck:
            if PRINT_STEPS: print('Unable to solve using rules of Sudoku, assuming a value:')
            assume_list, possibilities = get_next_assume_candidate(board_pos)
            org_board = copy.deepcopy(board_pos) # Create Snapshot of board before assuming.
            for assumption in org_board[assume_list[0]][assume_list[1]]:
                board_pos[assume_list[0]][assume_list[1]] = [assumption]
                assumption_counter +=1
                if PRINT_ASSUMPTION: print(f'Assuming {assumption} of {org_board[assume_list[0]][assume_list[1]]} at position ({assume_list[0]}, {assume_list[1]})')

                solve_sudoku(board_pos)
                board_pos = copy.deepcopy(org_board)   #Reset board back to Original State.         
            reccursion_depth -= 1
            return False

    print('SOLVED!!!!!')
    solution_counter +=1
    print(f'#######     SOLUTION NUMBER {solution_counter}     #######')
    print_board(board_pos)
    if FIRST_SOLUTION_ONLY: sys.exit(0)
    reccursion_depth -= 1
    return True

def main():
    problem1 = [[5,3,0,0,7,0,0,0,0],
                [6,0,0,1,9,5,0,0,0],
                [0,9,8,0,0,0,0,6,0],
                [8,0,0,0,6,0,0,0,3],
                [4,0,0,8,0,3,0,0,1],
                [7,0,0,0,2,0,0,0,6],
                [0,6,0,0,0,0,2,8,0],
                [0,0,0,4,1,9,0,0,5],
                [0,0,0,0,8,0,0,7,9]]
    problem2 = [[0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,3,0,8,5],
                [0,0,1,0,2,0,0,0,0],
                [0,0,0,5,0,7,0,0,0],
                [0,0,4,0,0,0,1,0,0],
                [0,9,0,0,0,0,0,0,0],
                [5,0,0,0,0,0,0,7,3],
                [0,0,2,0,1,0,0,0,0],
                [0,0,0,0,4,0,0,0,9]] # Sudoku designed against brute force. Notice Line 1 of solution.
    problem3 = [[1,0,0,0,6,8,0,0,9],
                [0,8,4,9,0,0,0,0,0],
                [0,3,0,0,4,2,0,0,0],
                [0,0,0,5,0,0,0,7,0],
                [7,9,0,0,3,0,4,0,0],
                [0,5,0,0,0,4,9,0,0],
                [0,4,0,0,0,3,0,0,0],
                [0,0,6,0,0,7,0,0,4],
                [0,0,2,0,8,6,0,3,0]]
    problem4 = [[0,0,0,0,3,7,6,0,0],
                [0,0,0,6,0,0,0,9,0],
                [0,0,8,0,0,0,0,0,4],
                [0,9,0,0,0,0,0,0,1],
                [6,0,0,0,0,0,0,0,9],
                [3,0,0,0,0,0,0,4,0],
                [7,0,0,0,0,0,8,0,0],
                [0,1,0,0,0,9,0,0,0],
                [0,0,2,5,4,0,0,0,0]]
    problem5 = [[9,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,1,0,0,7],
                [5,0,0,0,0,3,0,0,4],
                [0,0,7,0,0,0,2,0,0],
                [0,0,3,6,0,8,0,0,0],
                [0,0,0,4,0,0,6,1,0],
                [0,8,5,0,4,0,0,0,0],
                [0,0,0,3,2,0,0,6,0],
                [0,4,0,0,1,0,0,9,0]]
    problem6 = [[3,0,6,0,0,0,0,0,0],
                [0,0,0,0,0,6,0,7,0],
                [0,0,1,0,0,3,0,0,9],
                [2,0,0,7,0,8,0,9,0],
                [0,0,0,0,0,0,5,0,8],
                [0,0,0,1,0,0,2,3,0],
                [0,2,0,5,4,0,0,0,0],
                [0,9,0,0,2,0,0,0,0],
                [0,7,0,0,0,0,8,0,1]] #Use to understand Algorithm, with Print all steps.
    problem7 = [[8,5,0,0,0,2,4,0,0],
                [7,2,0,0,0,0,0,0,9],
                [0,0,4,0,0,0,0,0,0],
                [0,0,0,1,0,7,0,0,2],
                [3,0,5,0,0,0,9,0,0],
                [0,4,0,0,0,0,0,0,0],
                [0,0,0,0,8,0,0,7,0],
                [0,1,7,0,0,0,0,0,0],
                [0,0,0,0,3,6,0,4,0]]
    problem8 = [[0,0,5,3,0,0,0,0,0],
                [8,0,0,0,0,0,0,2,0],
                [0,7,0,0,1,0,5,0,0],
                [4,0,0,0,0,5,3,0,0],
                [0,1,0,0,7,0,0,0,6],
                [0,0,3,2,0,0,0,8,0],
                [0,6,0,5,0,0,0,0,9],
                [0,0,4,0,0,0,0,3,0],
                [0,0,0,0,0,9,7,0,0]]
    problem9 = [[0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0]] # Blank Board.
    problem10= [[8,0,0,0,0,0,0,0,0],
                [0,0,3,6,0,0,0,0,0],
                [0,7,0,0,9,0,2,0,0],
                [0,5,0,0,0,7,0,0,0],
                [0,0,0,0,4,5,7,0,0],
                [0,0,0,1,0,0,0,3,0],
                [0,0,1,0,0,0,0,6,8],
                [0,0,8,5,0,0,0,1,0],
                [0,9,0,0,0,0,4,0,0]]
    problem11= [[8,0,0,6,0,0,9,0,5],
                [0,0,0,0,0,0,0,0,0],
                [0,0,0,0,2,0,3,1,0],
                [0,0,7,3,1,8,0,6,0],
                [2,4,0,0,0,0,0,7,3],
                [0,0,0,0,0,0,0,0,0],
                [0,0,2,7,9,0,1,0,0],
                [5,0,0,0,8,0,0,3,6],
                [0,0,3,0,0,0,0,0,0]] # Multiple Solutions
    
    # Default starting board

    #####################################################
    puzzle = problem6 # Choose problem to solve here.
    #####################################################
    
    board_pos = initiate_board(puzzle)
    print("Trying to Solve Board")
    print_board(puzzle)
    solved = solve_sudoku(board_pos)
            
            
    



if __name__== '__main__':
    main()
    
