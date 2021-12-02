import fileinput
import sys
import os

n = 0
m = a = b = []


def array_from_input(input_array):
    for x in range(len(input_array)):
        input_array[x] = int(input_array[x].strip())
    return input_array


def lower_array_by_1(input_array):
    for x in range(len(input_array)):
        input_array[x] = input_array[x] - 1
    return input_array


def get_input(file):
    global n, m, a, b
    line_num = 0
    for line in file:
        if line_num == 0:
            n = int(line)
        elif line_num == 1:
            m = line.split(' ')
            m = array_from_input(m)
        elif line_num == 2:
            a = line.split(' ')
            a = array_from_input(a)
            a = lower_array_by_1(a)
        elif line_num == 3:
            b = line.split(' ')
            b = array_from_input(b)
            b = lower_array_by_1(b)
        line_num = line_num + 1


def main():
    if os.fstat(sys.stdin.fileno()).st_size > 0:
        file_object = fileinput.input()
        get_input(file_object)

        min_mass = min(m)
        result = 0

        p = [None] * n
        for i in range(n):
            p[b[i]] = a[i]

        odw = [False] * n

        w = 0
        for i in range(n):
            if not odw[i]:
                x = i
                temp_c = []
                while not odw[x]:
                    odw[x] = True
                    temp_c.append(m[x])
                    x = p[x]
                met1 = sum(temp_c) + (len(temp_c) - 2) * min(temp_c)
                met2 = sum(temp_c) + min(temp_c) + (len(temp_c) + 1) * min_mass
                w = w + min(met1, met2)

        print(w)


if __name__ == '__main__':
    main()
