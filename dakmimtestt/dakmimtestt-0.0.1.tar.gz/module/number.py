from subprocess import Popen, PIPE

def randint():
    p = Popen(['./number'], shell=True, stdout=PIPE, stdin=PIPE)
    result = p.stdout.read().decode('utf-8')
    print(result)

randint()