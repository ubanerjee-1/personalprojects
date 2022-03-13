import random


def generate_crowd(n):
    crowd = []
    for i in range(n):
        crowd.append(random.choice(['F', 'B']))
    return crowd

def conform_crowd(crowd):
    crowd.append('X')
    curr_dir = crowd[0]
    start_point = 0
    end_point = 0
    print(f'All Caps will conform to {crowd[0]}!!')
    
    for i in range(len(crowd)):
        if crowd[i] != curr_dir:
            if curr_dir != crowd[0]:
                if start_point == end_point:
                    print(f'Position {start_point} Flip your Cap')
                else:
                    print(f'Position {start_point} to {end_point} Flip your Caps')
            start_point = i
        end_point = i
        curr_dir = crowd[i]
                
        

def main():
    crowd = generate_crowd(int(input('Enter number of people in line: ')))
    print(crowd)
    conform_crowd(crowd)
    

if __name__== '__main__':
    main()
