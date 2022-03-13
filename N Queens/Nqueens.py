import copy
import sys

PRINT_STEP_BOARD = False
PRINT_STEPS = False
FIND_FIRST_SOLTION_ONLY = False
IGNORE_REFLECTIONS = False
IGNORE_ROTATIONS = False

SOLUTION_COUNT = 0
SOLUTIONS = []


############## CHOOSE VALUE OF "N" ##############
N = 8
#################################################

def place_queen(board, row, col):
    board[row][col] = 2
    nqueens = 0
    open_pos = 0
    edge1 = [row - min(row, col), col - min(row,col)]
    edge2 = [row - min(row, N - 1 - col), col + min(row,N - 1 - col)]
    for i in range(N):
        if board[row][i] == 0: board[row][i] = 1
        if board[i][col] == 0: board[i][col] = 1
        if max(edge1[0], edge1[1]) < N - i:
            if board[edge1[0] + i][edge1[1] + i] == 0: board[edge1[0] + i][edge1[1] + i] = 1
        if edge2[0] + i < N and edge2[1] - i >= 0:
            if board[edge2[0] + i][edge2[1] - i] == 0: board[edge2[0] + i][edge2[1] - i] = 1
        for j in range(N):
            if board[i][j] == 2: nqueens +=1
            if board[i][j] == 0: open_pos +=1
    if PRINT_STEP_BOARD: print_board(board)
    return board, nqueens, open_pos
        

def find_next_pos(board, skip):
    skipped = 0
    for i,row in enumerate(board):
        for j,cell in enumerate(row):
            if cell == 0:
                if skipped == skip:
                    return i,j
                else:
                    skipped += 1
    return N,N # No Open Positions Available

def solve_Nqueens(board):
    global SOLUTION_COUNT
    global SOLUTIONS
    for skip in range(N):
        if PRINT_STEPS: print(f"Will skip {skip} open positions...")
        row,col = find_next_pos(board, skip)
        if row == N:
            if PRINT_STEPS: print('Dead End!!')
            #print_board(board)
            return False
        org_board = copy.deepcopy(board)# Snapshot board
        board, nqueens, open_pos = place_queen(board, row, col)
        if PRINT_STEPS: print(f'{nqueens} queens placed on board...')
        if nqueens == N:
            if board in SOLUTIONS:
                return True
            else:
                SOLUTION_COUNT +=1
                print(f'###########   SOLUTION {SOLUTION_COUNT}   ###########')
                print_board(board)
                SOLUTIONS.append(board)
                if IGNORE_ROTATIONS:
                    r1 = [list(r) for r in list(zip(*board))[::-1]]
                    SOLUTIONS.append(r1)
                    r2 = [list(r) for r in list(zip(*r1))[::-1]]
                    SOLUTIONS.append(r2)
                    r3 = [list(r) for r in list(zip(*r2))[::-1]]
                    SOLUTIONS.append(r3)
                if IGNORE_REFLECTIONS:
                    r1 = board[::-1]
                    #print(' ')
                    #print_board(r1)
                    SOLUTIONS.append(r1)
                    r2 = [ r[::-1] for r in board ]
                    #print(' ')
                    #print_board(r2)
                    SOLUTIONS.append(r2)
                    r3 = [ r[::-1] for r in r1 ]
                    #print(' ')
                    #print_board(r3)
                    SOLUTIONS.append(r3)
                    r4 = [ r[::-1] for r in r2 ]
                    #print(' ')
                    #print_board(r4)
                    SOLUTIONS.append(r4)
                    r5 = [list(r)for r in [*zip(*board)]]
                    #print(' ')
                    #print_board(r5)
                    SOLUTIONS.append(r5)
                    
                if FIND_FIRST_SOLTION_ONLY: sys.exit(0)
                return True
        if open_pos < skip:
            if PRINT_STEPS: print('No Open Positions left !')
            return False
        
        solve_Nqueens(board)
        board = copy.deepcopy(org_board)# revert board

def print_board(board):
    for row in board:
        print(row)
        
def main():
    # 0 means Open, 1 means unavailable, 2 means occupied
    board = [[0 for i in range(N)] for i in range(N)]
    solve_Nqueens(board)



if __name__== '__main__':
    main()
