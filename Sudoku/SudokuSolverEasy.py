import math

board_pos = [[[i for i in range(1,10)] for i in range(9)] for i in range(9)]

def initiate_board(problem):
    global board_pos
    for i,row in enumerate(problem):
        for j,cell in enumerate(row):
            if cell > 0:
                board_pos[i][j] = [cell]                

def remove_invalid():
    global board_pos
    for i,row in enumerate(board_pos):
        for j,cell in enumerate(row):
            if len(cell) == 1:
                for e in range(9):
                    # 1. Remove from Row
                    if e != j:
                        try:
                            board_pos[i][e].remove(cell[0])
                        except ValueError:
                            pass
                    # 2. Remove from Column
                    if e != i:
                        try:
                            board_pos[e][j].remove(cell[0])
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
                            except ValueError:
                                pass
    print_board()

def board_length():
    global board_pos
    total_length = 0
    for i,row in enumerate(board_pos):
        for j,cell in enumerate(row):    
            total_length +=len(cell)
    return total_length
    
def print_board():
    global board_pos
    for row in board_pos:
        print(row)

def is_solved():
    global board_pos
    for row in board_pos:
        for cell in row:
            if len(cell) != 1:
                return False
    return True

def solve_sudoku():
    board_pos = board_length()
    while not is_solved():
        remove_invalid()
        if board_pos == board_length():
            print('No Easy moves')
        else:
            board_pos = board_length()
            print(f'Board Possibilities : {board_pos}\n')   

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
    initiate_board(problem1)
    solve_sudoku()
            
            
    



if __name__== '__main__':
    main()
    
