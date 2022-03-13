import sys
import math
import datetime as dt
from time import sleep


last_print = dt.datetime.now()
dead_end_count = 0
assumption_counter = 0

def get_empty_cell(board):
    for i, row  in enumerate(board):
        for j, cell in enumerate(row):
            if cell == 0 : return i,j
    return 10,10

def get_valid_moves(board, row_int,col_int):
    valid_moves = [i for i in range(1,10)]
    sector_row = math.floor((row_int) / 3)
    sector_col = math.floor((col_int) / 3)
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if i == row_int:
                try:
                    valid_moves.remove(cell)
                except ValueError:
                    pass
            if j == col_int:
                try:
                    valid_moves.remove(cell)
                except ValueError:
                    pass
            curr_sector_row = math.floor((i) / 3)    
            curr_sector_col = math.floor((j) / 3)
            if curr_sector_row == sector_row and curr_sector_col == sector_col:
                try:
                    valid_moves.remove(cell)
                except ValueError:
                    pass
    return valid_moves

def is_solved(board):
    for row in board:
        for cell in row:
            if cell == 0:
                return False
    return True

def print_board(board):
    for row in board:
        print(row)
            
def solve_sudoku(board):
    #while not is_solved(board):
    global dead_end_count
    global assumption_counter
    row,col = get_empty_cell(board)
    global last_print
    if row == 10:
        print('SOLVED')
        print_board(board)
        sys.exit(0)
    valid_moves = get_valid_moves(board, row, col)
    #print_board(board)
    if len(valid_moves) == 0:
        #print(f'No valid moves for {row, col}')
        dead_end_count +=1
        print(f'Dead End # {dead_end_count} @ [{row}][{col}]')
        #print_board(board)
        return False
    for move in valid_moves:
        assumption_counter += 1
        print(f'Assumption {assumption_counter} : Set {row, col} to {move} of {valid_moves}')
        board[row][col] = move
        #if col == 0: print_board(board)
        val = solve_sudoku(board)
        if is_solved(board):
            print('SOLVED after {dead_end_count} dead Ends')
            print_board(board)
            sys.exit(0)
    board[row][col] = 0
    
    return False
        

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
    
    

    solved = solve_sudoku(problem8)
            
            
    



if __name__== '__main__':
    main()
    
