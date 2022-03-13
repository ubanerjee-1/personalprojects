import math
import copy
import sys


reccursion_depth = 0
dead_end_counter = 0
assumption_counter = 0
print_steps = False
print_every_step = False
print_assumption = False
detail_log = False
sorted_assumption = True # When True, assumptions will be made on cells with smallest possible choices, else Left2Right-Top2Down.


def initiate_board(problem):
    board_pos = [[[i for i in range(1,10)] for i in range(9)] for i in range(9)]
    for i,row in enumerate(problem):
        for j,cell in enumerate(row):
            if cell > 0:
                board_pos[i][j] = [cell]
    return board_pos

def remove_invalid(board_pos):
    for i,row in enumerate(board_pos):
        for j,cell in enumerate(row):
            if len(cell) == 1:
                for e in range(9):
                    # 1. Remove from Row
                    if e != j:
                        try:
                            board_pos[i][e].remove(cell[0])
                            if len(board_pos[i][e]) == 0:
                                if print_every_step: print(f"ROW CHECK: Board is invalid at position ({i},{j})")
                                return False, board_pos
                            valid_col = False
                            for counter_col in range(9):
                                if cell[0] in board_pos[counter_col][e]:
                                    valid_col = True
                                    break
                            if not valid_col:
                                if print_every_step: print(f'COLUMN CHECK: Value {cell[0]} not present in column {e}! ')
                                return False, board_pos
                        except ValueError:
                            pass

                    # 2. Remove from Column
                    if e != i:
                        try:
                            board_pos[e][j].remove(cell[0])
                            if len(board_pos[e][j]) == 0:
                                if print_every_step: print(f"COLUMN CHECK: Board is invalid at position ({e},{j})")
                                return False, board_pos
                            valid_row = False
                            for counter_row in range(9):
                                if cell[0] in board_pos[e][counter_row]:
                                    valid_row = True
                                    break
                            if not valid_row:
                                if print_every_step: print(f'ROW CHECK: Value {cell[0]} not present in row {e}! ')
                                return False, board_pos
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
                                    if print_every_step: print(f"SECTOR CHECK: Board is invalid at position ({i_sec},{j_sec})")
                                    return False, board_pos
                            except ValueError:
                                pass
    if print_every_step: print("Removed Invalid Values..")
    #if print_every_step: print_board(board_pos)
    return True, board_pos

def board_length(board_pos):
    total_length = 0
    for i,row in enumerate(board_pos):
        for j,cell in enumerate(row):    
            total_length +=len(cell)
    return total_length
    
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




def get_assume_candidate_list(board_pos):
    # Not used
    assume_list = []
    possibilities = 1
    #print_board(board_pos)
    for i,row in enumerate(board_pos):
        for j,cell in enumerate(row):    
            if len(cell) != 1:
                assume_list.append([i,j,len(cell)])
                possibilities = possibilities * len(cell)
                #print(possibilities)
    #if print_steps: print('Assume Values for :', assume_list)

    return (sorted(assume_list, key = lambda x: x[2]), possibilities)
    #sys.exit(0)

def get_next_assume_candidate(board_pos):
    assume_list = []
    possibilities = 1
    #print_board(board_pos)
    for i,row in enumerate(board_pos):
        for j,cell in enumerate(row):    
            if len(cell) > 1:
                assume_list.append([i,j,len(cell)])
                possibilities = possibilities * len(cell)
                #print(possibilities)
    #if print_steps: print('Assume Values for :', assume_list)
    sorted_assume = sorted(assume_list, key = lambda x: x[2])
    #if print_steps: print('Sorted Values for :',sorted_assume)    
    if sorted_assumption:
        return (sorted_assume[0], possibilities)
    else:
        return (assume_list[0], possibilities)

def is_board_valid(board_pos):
    # Not used
    for row in board_pos:
        for cell in row:
            if len(cell) == 0:
                if print_steps: (f"Board is invalid at row ({row})")
                return False
    if  print_steps: print(">> Board is Valid <<")
    return True    

def solve_sudoku(board_pos):
    global reccursion_depth
    global dead_end_counter
    global assumption_counter
    board_pre_length = board_length(board_pos)
    if board_pre_length == 81:
        print('SOLVED!!!!')
        print_board(board_pos)
        sys.exit(0)
        
    reccursion_depth += 1
    if print_steps: print('reccursion depth :', reccursion_depth)
    while not is_solved(board_pos):
        if print_every_step: print('Trying to Solve:')
        if print_every_step: print_board(board_pos)
        # Rule based Sudoku Solver.
        is_valid, board_pos = remove_invalid(board_pos)
        
        if is_valid:
            pass
        else:
            dead_end_counter += 1
            if print_steps: print(f'Dead End Number: {dead_end_counter}!!')        
            if print_steps: print_board(board_pos)
            reccursion_depth -= 1
            return False

        # Unable to solve board with the rules of Sudoku, Need to assume a value.
        if board_pre_length == board_length(board_pos):
            if print_steps: print('Unable to solve using rules of Sudoku, assuming a value:')
            if print_steps: print_board(board_pos)
            assume_list, possibilities = get_next_assume_candidate(board_pos)
            if print_steps: print('Assume Values for :', assume_list)
            i_assume, j_assume, l = assume_list[0],assume_list[1],assume_list[2]
            org_board = copy.deepcopy(board_pos) # Create Snapshot of board before assuming.
            for assumption in org_board[i_assume][j_assume]:
                board_pos[i_assume][j_assume] = [assumption]
                assumption_counter +=1
                if print_assumption: print(f'Assuming {assumption} of {org_board[i_assume][j_assume]} at position ({i_assume}, {j_assume})')
                #if print_assumption: print_board(board_pos)
                if solve_sudoku(board_pos):
                    print('SOLVED!!')
                    print_board(board_pos)
                    sys.exit(0)
                    return True
                board_pos = copy.deepcopy(org_board)   #Reset board back to Original State.         
            reccursion_depth -= 1
            return False
        else:
            board_pre_length = board_length(board_pos)
            #if print_steps: print(f'Current Board Length : {board_pre_length}\n')

    print('SOLVED!!!!!')
    print_board(board_pos)
    sys.exit(0)
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
                [0,7,0,0,0,0,8,0,1]] #Use to understand Algorithm, Print all steps.
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
                [0,0,0,0,0,0,0,0,0]]
    problem10= [[8,0,0,0,0,0,0,0,0],
                [0,0,3,6,0,0,0,0,0],
                [0,7,0,0,9,0,2,0,0],
                [0,5,0,0,0,7,0,0,0],
                [0,0,0,0,4,5,7,0,0],
                [0,0,0,1,0,0,0,3,0],
                [0,0,1,0,0,0,0,6,8],
                [0,0,8,5,0,0,0,1,0],
                [0,9,0,0,0,0,4,0,0]]
    
    # Default starting board
    
    puzzle = problem2 # Choose problem to solve here.
    
    board_pos = initiate_board(puzzle)
    print("Trying to Solve Board")
    print_board(puzzle)
    solved = solve_sudoku(board_pos)
            
            
    



if __name__== '__main__':
    main()
    
