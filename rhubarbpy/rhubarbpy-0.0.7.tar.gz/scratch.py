from rhubarbpy import loopsum, fibonacci
from rhubarbpy.subpkg import subpkg_hello

l = [1, 2, 3, 4]
print(f"The sum of {l} is {loopsum(l)}")

subpkg_hello("Dan")

print([fibonacci(i) for i in range(10)])
