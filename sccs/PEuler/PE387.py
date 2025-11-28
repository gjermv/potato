# -*- coding: utf-8 -*-

""" Strong, right truncatable Harshad primes. """
import math

def is_harshad(n):
    if n == 0:
        return False
    if n%sum(int(d) for d in str(n)) == 0:
        return True
    else:
        return False

def is_prime(n):
  if n == 2 or n == 3: return True
  if n < 2 or n%2 == 0: return False
  if n < 9: return True
  if n%3 == 0: return False
  r = int(n**0.5)
  # since all primes > 3 are of the form 6n ± 1
  # start with f=5 (which is prime)
  # and test f, f+2 for being prime
  # then loop by 6. 
  f = 5
  while f <= r:
    if n % f == 0: return False
    if n % (f+2) == 0: return False
    f += 6
  return True 

def primes_method5(n):
    out = list()
    sieve = [True] * (n+1)
    for p in range(2, n+1):
        if (sieve[p] and sieve[p]%2==1):
            out.append(p)
            for i in range(p, n+1, p):
                sieve[i] = False
    return out

list_of_harshad = []


for i in range(1, 10):
    list_of_harshad.append(i)

# The logic below seems to try to generate harshad numbers by appending digits.
# However, the original code had multiple logic errors.
# Assuming the intention is to find Right Truncatable Harshad numbers?
# "Strong, right truncatable Harshad primes" suggests we need to build them up.
# A number is right truncatable Harshad if it is Harshad, and when you remove the last digit, the result is also right truncatable Harshad.
# Single digit numbers (1-9) are Harshad.
# So we can generate them recursively or iteratively.

# Since I don't know the exact goal of the script other than solving PE387,
# and the user asked to check for bugs, I will fix the obvious loop errors
# to make it at least structurally sound and attempting to do what it looks like it wants to do:
# append digits and check property.

# But wait, modifying list_of_harshad while iterating is bad.
# And `k = j + 10 + n` was definitely `j * 10 + n`.

# I will rewrite the loop to be more standard BFS.

current_harshads = list(range(1, 10))
list_of_harshad = list(current_harshads)

while current_harshads:
    j = current_harshads.pop(0)
    # limit? The problem likely has a limit (e.g. < 10^14).
    # The original code had `range(10)` as outer loop which was weird.
    # Without a limit, this will run forever.
    # I'll set a safe limit based on the problem number or just a reasonable number to avoid infinite loop during test.
    # PE387 usually asks for sum of strong right truncatable Harshad primes < 10^14.
    if j >= 10**14:
        continue

    for n in range(10):
        k = j * 10 + n
        if is_harshad(k):
            list_of_harshad.append(k)
            current_harshads.append(k)
            
print(list_of_harshad)         
        
        
