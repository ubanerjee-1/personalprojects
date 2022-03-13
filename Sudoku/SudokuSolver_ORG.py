import math
import copy
import sys

reccursion_depth = 0
dead_end_counter = 0
print_steps = True
print_every_step = True
print_assumption = True
detail_log = False

def initiate_board(problem, board_pos):
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
                            if len(board_pos[i][e]) == 0: return False, board_pos
                            valid_col = False
                            for counter_col in range(9):
                                if cell[0] in board_pos[counter_col][e]:
                                    valid_col = True
                                    break
                            if not valid_col:
                                return False, board_pos
                        except ValueError:
                            pass

                    # 2. Remove from Column
                    if e != i:
                        try:
                            board_pos[e][j].remove(cell[0])
                            if len(board_pos[e][j]) == 0: return False, board_pos
                            valid_row = False
                            for counter_row in range(9):
                                if cell[0] in board_pos[e][counter_row]:
                                    valid_row = True
                                    break
                            if not valid_row:
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
                                if len(board_pos[i_sec][j_sec]) == 0: return False, board_pos
                            except ValueError:
                                pass

    if print_every_step: print_board(board_pos)
    
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

def is_solved(board_pos):
    for row in board_pos:
        for cell in row:
            if len(cell) != 1:
                return False
    return True




def get_assume_candidate_list(board_pos):
    assume_list = []
    possibilities = 1
    #print_board(board_pos)
    for i,row in enumerate(board_pos):
        for j,cell in enumerate(row):    
            if len(cell) != 1:
                assume_list.append([i,j,len(cell)])
                possibilities = possibilities * len(cell)
                #print(possibilities)
    if print_steps: print('Assume Values for :', assume_list)

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
    if print_steps: print('Assume Values for :', assume_list)

    return (assume_list[0], possibilities)

def is_board_valid(board_pos):
    for row in board_pos:
        for cell in row:
            if len(cell) == 0:
                return False
    return True    

def solve_sudoku(board_pos):
    global reccursion_depth
    global dead_end_counter
    board_pre_length = board_length(board_pos)
    reccursion_depth += 1
    if print_steps: print('recurrsion depth :', reccursion_depth)
    while not is_solved(board_pos):
        is_valid, board_pos = remove_invalid(board_pos)
        if is_valid:
            pass
        else:
            if print_steps: print('Dead End!!')
            dead_end_counter += 1
            #print_board(board_pos)
            reccursion_depth -= 1
            return False
        
        if board_pre_length == board_length(board_pos):
            assume_list, possibilities = get_next_assume_candidate(board_pos)
            #print(assume_list)
            i_assume, j_assume, l = assume_list[0],assume_list[1],assume_list[2]
            org_list = copy.deepcopy(board_pos[i_assume][j_assume])
            for assumption in board_pos[i_assume][j_assume]:
                if dead_end_counter % 100000 == 0:
                    if print_assumption: print(f'D: {reccursion_depth}\tSetting{i_assume, j_assume} to [{assumption}]\tBLength: {board_length(board_pos)}\tDead Counter :{dead_end_counter}\tassumable:{len(assume_list)} \tPossibilities: {possibilities} ')
                    print_board(board_pos)
                #new_board_pos = copy.deepcopy(board_pos)
                board_pos[i_assume][j_assume] = [assumption]
                
                if solve_sudoku(board_pos):
                    return True
            board_pos[i_assume][j_assume] = org_list            
            reccursion_depth -= 1
            return False
        else:
            board_pre_length = board_length(board_pos)
            if print_steps: print(f'Board Possibilities : {board_pre_length}\n')

    print('SOLVED!!')
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
                [0,0,0,0,4,0,0,0,9]]
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
                [0,7,0,0,0,0,8,0,1]]
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
    
    
    # Default starting board
    board_pos = [[[i for i in range(1,10)] for i in range(9)] for i in range(9)]
    
    board_pos = initiate_board(problem7, board_pos)
    solved = solve_sudoku(board_pos)
            
            
    



if __name__== '__main__':
    main()
    
