
coins = [4,5,24,21,35,77,45,33,22,55,6,8,9,14,13,45]

memo = {-1:0}

def pick_coins(n):
    global memo
    if n in memo:
        #print(n, memo)
        return memo[n]
    if n == 0:
        memo[n] = coins[len(coins) - n - 1]
        return coins[len(coins) - n - 1]
        
    x = pick_coins(n - 1)
    y = coins[len(coins) - n - 1] + pick_coins(n - 2)
    print(n,x,y)
    if x > y:
        memo[n] = x
        return x
    else:
        memo[n] = y
        return y


def main():
    
    print(pick_coins(len(coins)))
    print(memo)


if __name__== '__main__':
    main()
