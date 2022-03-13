import locale
locale.setlocale(locale.LC_ALL, '')

memo = {}
def cache(func):
    
    def wrapper_cache(n):
        print(n)
        if n not in memo:
            memo[n] = func(n)
        return memo[n]
    return wrapper_cache

@cache
def fib(n):
    if n == 0 or n == 1: return 1
    number = fib(n-2) + fib(n -1)
    return number


def main():
    n = int(input('N ?'))
    fib(n)
    for i in range(n):
        print(f'Fibonacci Number at Position {i} is {memo[i]:n}')
    






if __name__== '__main__':
    main()
