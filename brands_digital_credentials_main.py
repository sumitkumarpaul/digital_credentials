#####################################################################################################
# This file implements pedersen commitment
#####################################################################################################
import sys
import os
import pdb
import traceback
import random
import sympy
import numpy
import argparse
import hashlib
from math import gcd

def calculate_subgroups(p):
    def get_group(coprime):
        return tuple(sorted(generate_subgroup(coprime, p)))

    return {get_group(coprime) for coprime in get_coprimes(p)}

def generate_subgroup(factor, p, start=1):
    while True:
        yield start
        start = (start * factor) % p

        if start == 1:
            return

def get_coprimes(number):
    co_primes = []
#    for i in range(2, number):
    for i in range(1, number):
        if (gcd(number, i) == 1):
            co_primes.append(i)
        
    return co_primes


# TODO: I hvae a doubt about this function
def find_generators(group, p, is_prime):
    # Empty list
    generators = []
    tmp_members = []

    # Check each element, whether it is a generator
    for g in group:
        # Try with each elements in the range 1 to (p-1)
        #print("Trying: %d as generator" %(g)) 

        # Calculate g**0, g**1, g**2,.., g**(len(group) - 1): Total len(group) elements
        for j in range(len(group)):
            val = (g**j) % p
            tmp_members.append(val)

            """
            # If generated value is a member of the group
            if (group.count(val) > 0):
                tmp_members.append(val)
            """

        if (len(set(tmp_members)) == len(group)):
            if (is_prime == True):
                if (sympy.isprime(g) == True):
                    generators.append(g)
            else:
                generators.append(g)

        tmp_members.sort()
        #print(*tmp_members, sep = ", ") 
        tmp_members.clear()

    #print(*generators, sep = ", ")

    return generators

    
def find_inverse(a, p):
    # According to the Fermet's Little theorem
    # a^(p-1) = 1 mod p
    # or, a^(p-2)*a = 1 mod p
    # or, a^(p-2) = Inverse(a)
    # a p cannot be less than 2, so no special treatment required
    
    return ((a**(p-2)) % p)


def test_brands_credentials():
    zq = []
    g = []
    y = []
    x = []
    w = []
    a = []
    r = []
    alpha = 0
    q_chosen = False
    q = 0
    h0 = 0
    g0 = 0
    m = 0
    s = 0
    c = 0
    sa = 0

    #Syetem setup
    print("********************************* Start setting up the common parameters *********************************")
    m = int(input("How many attributes do you want to encode within the digital credential? m: "))

    s = int(input("Which attribute Alice wants to show? Enter 1 for 1st attribute, 2 for 2nd attribute..m for m-th attribute: "))

    # Please choose a random prime number, p
    p = int(input("Please choose a random prime number, p: "))

    print ("For p = %d any q is not allowed.There must exist a sub-group(Zq) of Zp* having order q." %(p))

    # Choose q: Number of elements in Zq should be sufficiently large
    while (q_chosen == False):
        for sub_g in calculate_subgroups(p):
            if (sympy.isprime(len(sub_g))):
                print ("    Do you want to use q = %d and corresponding Zq?\n    " %(len(sub_g)), end='')
                print (*sub_g)

                ip = input("    Please enter \"Yes\" to choose this one, or any other key to view the next option: ")

                if (ip.lower() == "Yes".lower()):
                    q_chosen = True
                    q = len(sub_g)
                    print ("    So chosen q is: %d, and corresponding Zq is:" %(q))
                    zq = sub_g
                    print (*sub_g)
                    break


    print ("    There can be many generators of this sub-group, choose any one from the below list:")
    print (find_generators(zq, p, False))

    g.insert(0, int(input("Choose g0: ")))

    print("\n\n>>    So, chosen p = %d, q = %d, g0 = %d, Zq =\n>>    " %(p, q, g[0]))
    print(*zq)
    
    print("*********************************  End setting up the common parameters  *********************************")

    print("*********************************        CA's initial setup start        *********************************")
    
    x.insert(0, int(input("Impersonating CA choose a random value x0: ")))
    
    h0 = (g[0]**x[0])%p
    
    y.insert(0, 0)
    print("Impersonating CA choose m random values, {y1, y2,..yi,..ym}")
    for i in range(1, int(m+1)):
        print("Choose y%d: " %(i))
        y.insert(i, int(input()))
        
        #gi = (g0^yi) mod p
        g.insert(i, (g[0]**y[i])%p)  

    print ("\n\n>>    CA calculates public (m+1) components of his public key, those are {g1, g2,..gi,..gm}:\n>>    ")
    for i in range(1, int(m+1)):
        print(*g)  

    print (">>    and h0: %d " %(h0))
    
    print("*********************************         CA's initial setup end         *********************************")

    print("*********************************    Alice's commitment creation start   *********************************")
    print ("Alice should choose %d attribute values." %(m))
    
    print("Impersonating Alice, choose m attribute values, {x1, x2,..xi,..xm}")
    for i in range(1, int(m+1)):
        print("Choose x%d: " %(i))
        x.insert(i, int(input()))
    
    print ("Alice should choose a random number α.")
    
    alpha  = int(input("Impersonating Alice, choose α: "))
    
    # Alice calculates the commitment
    h = 1
    for i in range(1, int(m+1)):
        h = ((h*(g[i]**x[i])) % p)
    
    h = (h*(h0**alpha)) % p
    
    print("\n\n>>    Alice creates the commitment h: %d" %(h))
    
    print("*********************************     Alice's commitment creation end    *********************************")

    print("*********************************    Alice's public key creation start   *********************************")

    w.insert(0, 0)

    print ("Alice should choose m random values, {w1, w2,.., w(s-1), w(s+1),..w(m+1)}")
    
    print("Impersonating Alice, choose %d random values, "  %(m))

    for i in range(1, m+2):
        if (i == s):
            w.insert(i, 0)
        else:
            print("Choose w%d:" %(i))
            w.insert(i, int(input()))
            
    # Alice generates public key
    a = 1
    for i in range(1, m+1):
        if (i != s):
            a = (a*(g[i]**w[i]))%p

    print(*w)

    a = (a*(h0**w[m+1]))%p            
    
    print("\n\n>>    Alice generates a public key and that is: %d. It is sent to Bob along with the CA's signature on it." %(a))
    
    print("*********************************    Alice's public key creation end   *********************************")

    print("*********************************    Bob's operation start   *********************************")
    print ("After verifying the signature, Bob and sends a random number(c) to Alice.")
    
    c = int(input("Impersonating Alice, choose a random number c:"))

    print("*********************************     Bob's operation end    *********************************")

    print("*********************************    Alice's operation start   *********************************")

    sa = int(input("The value of the attribute which Alice wants to show is:"))
    
    r.insert(0, 0)
    for i in range(1, m+1):
        if (i != s):
            r.insert(i, ((c*x[i]+w[i])%q))
        else:
            r.insert(i, sa)

    r.insert((m+1), ((c*alpha+w[m+1])%q))
    
    print("\n\n>>    Alice computes m-values and sends the attribute to be shown(%d) along with it." %(sa))
    print(">>    Alice sends:\n>>    ")
    print(*r)
    

    print("*********************************    Alice's operation end    *********************************")

    print("*********************************    Bob's verification start   *********************************")
    tmp = ((h**c)*a)%p
    print("\n\n>>    Bob computes (h^c)a mod p = %d" %(tmp))

    tmp = 1
    for i in range(1, m+1):
        if (i != s):
            tmp = tmp*(g[i]**r[i])
        else:
            tmp = tmp*(g[i]**(sa*c))
    
    tmp = (tmp*(h0**r[m+1]))%p

    print(">>    Bob computes (g1^r1..gs^(sa.c)..gm^rm.h0^r(m+1)) mod p = %d" %(tmp))

    print("\n\n>>    As (h^c)a mod p = (g1^r1..gs^(sa.c)..gm^rm.h0^r(m+1)) mod p, Alice successfully revealed %d-th attribute as: %d. And proved that she is the legitimate owner of this credential." %(s, sa))

    print("*********************************    Bob's verification end   *********************************")

    return

