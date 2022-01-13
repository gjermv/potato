# -*- coding: utf-8 -*-

""" Strong, right truncatable Harshad primes. """
import math

def is_harshad(n):
    if n%len(str(n)) == 0:
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


for i in range(10):
    if is_harshad(i):
        list_of_harshad.append(i)
        
    for j in list_of_harshad:
        for n in range(10):
            k = j + 10 + n
        if is_harshad(k):
            list_of_harshad.append(k)
            
print(list_of_harshad)         
        
        
