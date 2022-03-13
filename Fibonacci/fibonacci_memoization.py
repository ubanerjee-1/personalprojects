import locale
locale.setlocale(locale.LC_ALL, '')

memo = {}


def fib(n):
    global numbers
    if n in memo: return memo[n]
    if n == 0 or n == 1:
        memo[n] = 1
        #print(1)
        return 1
    number = fib(n-2) + fib(n -1)
    memo[n] = number
    #print(number)
    return number


def main():
    n = int(input('N ?'))
    fib(n)
    print(memo)
    for i in range(n):
        print(f'Fibonacci Number at Position {i} is {memo[i]:n}')
    






if __name__== '__main__':
    main()
