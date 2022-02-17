import random


def prime_test(N, k):
    # This is the main function connected to the Test button. You don't need to touch it.
    return run_fermat(N,k), run_miller_rabin(N,k)


#O(n^3) time complexity because it recursivly loops n times and each time multiplies n-bit numbers
# Space O(n^2)
#Modular exponentiation
def mod_exp(x, y, N):
    if y == 0: #will stop if if hits base case of y = 0.
        return 1
    z = mod_exp(x, int(y/2), N)   # log(y) => log(N-1) => log(N) => O(n)

    if y%2 == 0:
        return z**2 % N
    else:
        return (x*(z**2)) % N
    
#The probability that the answer returned from fermat's test is correct
def fprobability(k):
    return 1 - (1/(2**k))

#The probability that the answer returned from miller_rabin's test is correct
def mprobability(k):
    return 1 - (1/4**k)

#This function will run the fermat test given a number(N) and the number of loops(k)
def run_fermat(N,k):
    for num in range(k-1):
        a = random.randint(2, N - 1)
        if (mod_exp(a, N-1, N) == 1):  # this is calling mod_exp O(n^3)
            continue
        else:
            return 'composite'

    return 'prime'

#time complexity:O(n^4).Space complexity:O(n^2)
#This function will run the miller_rabin test given a number(N) and the number of loops(k)
def run_miller_rabin(N,k):
    #if a number is divisable by 2 it's composite
    if N % 2 == 0:
        return 'composite'

    for num in range(k - 1):
        a = random.randint(2, N - 1)
        E = N - 1

        #checking if a number is prime or a composite.
        if(mod_exp(a, E, N)) == 1: #This is still going to be O(n^3)
            if MR_loop(a, E/2, N) == True:  # because this is passing E/2 which acts as a bit shift over it will be O(n)
                print('prime')
                return 'prime'
            else:
                return 'composite'
        else:
            return 'composite'

#helper function for the Miller-rabin test.
def MR_loop(a, E, N):
    if E % 2 != 0: #prime
        return True

    if mod_exp(a, E, N) == N -1: #This is equvilant to equaling -1. Prime
        return True

    if mod_exp(a, E, N) != 1: #composite
        return False

    else:
        MR_loop(a, E / 2, N)

    return True
