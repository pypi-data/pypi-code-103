from dscal.tools import pi , e

def factorial(number : int) -> int:
    '''computes factorial for integer inputs for the notion of
       x! = x*(x-1)*(x-2)*...*2*1'''

    from functools import cache

    @cache
    def fac(n : int) -> int :
        if n == 0 or n == 1:
            return 1
        else :
            return n*fac(n-1)

    for i in range(number+1):
        x = fac(i)
    
    return x

def sub_factorial(number : int) -> int:
    '''sub_factorials point to the number of de-arrangements of given 
       number of objects.  
       sub-factorial for integer input (x) can be computed as : 
       !x = x!*(1/0!-1/1!+...+1/x!)'''
       
    x=factorial(number)

    s=0
    for i in range(number+1):
        s+=((-1)**i)/factorial(i)

    return int(x*s)

def double_factorial(number : int) -> int:
    '''Double factorial refers to x!! . It is not the same as (x!)! .
       x!! = x*(x-2)*(x-4)*...*(2 or 1)'''
    if number == 1:
        return 1
    
    elif number == 2:
        return 2

    else:
        return factorial(number)//double_factorial(number-1)

def sin(theta : float) -> float:
    '''theta : the concerned angle in radians.
       returns sin(theta)'''

    def angle_correction(angle : float):
    
        sign = 1
        if angle < 0:
            sign = -1
            angle = -angle
            
        index, value = (angle//pi, angle%pi)

        if index%2 != 0:
            sign*=-1
        
        return sign, value

    def Sin(theta : float) -> float:        
        s=0

        for i in range(51):

            sign,p=(-1)**i,2*i+1
            s+= sign*theta**p/factorial(p)

        return s
    
    sign, theta = angle_correction(theta)
    
    return sign*Sin(theta)

def cos(theta : float) -> float:
    '''theta : the concerned angle in radians'''
    return (sin(pi/2 - theta))

def tan(theta : float) -> float:
    '''theta : the concerned angle in radians.
       returns tan(theta)'''
    return sin(theta)/cos(theta)

def cosec(theta : float) -> float:
    '''theta : the concerned angle in radians.
       returns cosec(theta)'''
    return 1/sin(theta)

def sec(theta : float) -> float:
    '''theta : the concerned angle in radians.
       returns sec(theta)'''
    return 1/cos(theta)

def cot(theta : float) -> float:
    '''theta : the concerned angle in radians.
       returns cot(theta)'''
    return 1/tan(theta)

def radians(theta : float) -> float:
    '''convets the angle (theta) from degrees to radians.'''
    return pi*theta/180

def degrees(theta : float) -> float:
    '''converts the angle (theta) from radians to degrees.'''
    return 180*theta/pi

def lcm(*args : int) -> int:
    '''computes Lowest Common Multiple of the given positive integer values.'''
    
    for i in args:
        if i != int or i <= 0:
            raise ValueError(f'arguments can only be positive integers, but {i} was given')
        
    def LCM(n1 : int, n2 : int) -> int :
        if n1 > n2 :
            n1 , n2 = n2 , n1
        
        step = 1
        multiple = n2*step
        
        while True:
            
            if multiple % n1 == 0 :
                return multiple
            
            step += 1
            multiple = n2*step

    last_lcm = args[0]

    for i in range(1,len(args)):
        last_lcm = LCM(last_lcm,args[i])

    return last_lcm

def factor(number : int) -> tuple:
    '''returns a tuple of all the factors of the given positive integer.'''
    
    if number != int or number <= 0:
        raise ValueError(f'arguments can only be positive integers, but {number} was given')
    
    l = []
    for i in range(1, number+1):
        if number%i == 0:
            l.append(i) 

    return tuple(l)

def prime(number : int) -> bool:
    '''returns boolean value for the number being prime or not. '''
    if number < 2:
        return False
    else:    
        for i in range(2,number//2+1):
            if number%i == 0:
                return False
        else:
            return True

def prime_factorize(number : int) -> tuple:
    '''returns a tuple of the factors in the prime-factorized form of the number given.'''
    
    def prime_factor(number : int) -> tuple:
        
        l = []

        for i in factor(number):
            if prime(i):
                l.append(i)

        return tuple(l)
    
    if number < 2:
        return None

    else:
        l = []

        for i in prime_factor(number):
            x = number
            while x%i == 0 :
                l.append(i)
                x = x//i

        return tuple(l)

def hcf(*args) -> tuple:
    '''computes Highest Common Factor of the given positive integers values.'''
    for i in args:
        if i != int or i <= 0:
            raise ValueError(f'arguments can only be positive integers, but {i} was given')
    
    def HCF(n1 : int, n2 : int) -> int:
        return n1*n2//(lcm(n1, n2))
        
    last_hcf = args[0]

    for i in range(1,len(args)):
        last_hcf = HCF(last_hcf,args[i])

    return last_hcf

def floor(number : float) -> int:
    '''returns the largest integer >= number.'''
    
    if number >= 0:
        return int(number)
    else :
        return int(number)-1

def ceil(number : float) -> int:
    '''returns the largest integer <= number.'''
    if number >= 0:
        return int(number)-1
    else:
        return int(number)

def P(n : int, r : int) -> int:
    '''computes the number of possible arrangements of r objects chosen\n from n objects. '''
    return factorial(n)//factorial(n-r)

def C(n : int, r : int) -> int:
    '''computes the number of possible groups of r objects chosen\n from n objects. '''
    return factorial(n)//(factorial(n-r)*factorial(r))

def log(number : float, base : float = e) -> float:
    '''computes the logarithm for a given number and a given base.'''
    if number <= 0:
        raise ValueError('input must be a real number greater than 0')
    
    elif base == e:
        b = 1e-10
        return (number**b-1)/b
    
    elif base >= 0:
        return log(number)/log(base)
    
    else:
        return None
    
def log2(number : float) -> float:
    '''computes logarithm for the base 2.'''
    return log(number, 2)

def log10(number : float) -> float:
    '''computes logarithm for the base 10.'''
    return log(number, 10)
