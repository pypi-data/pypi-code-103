import random
import string


def rand_int(vmin, vmax):
    return random.randint(vmin, vmax)


def rand_double(vmin, vmax):
    return random.uniform(vmin, vmax)


def rand_list(len, vmin, vmax, distinct = False):
    if not distinct:
        res = []
        for i in range(0, len):
            res.append(rand_int(vmin, vmax))
        return res
    else:
        return random.sample(range(vmin, vmax+1), len)


def rand_str(length, seed=string.ascii_lowercase):
    return ''.join(random.choices(seed, k=length))


# nhập vào một số nguyên dương duy nhất là số thứ tự của test case, bắt đầu từ 1
test_number = int(input())

# print("Generating testcase #%02d" % test_number)

if test_number == 1:
    # testcase tự soạn
    print(2, 5, 11)
elif test_number == 2:
    # testcase tự soạn
    print(3, 18132, 17)
else:
    if test_number <= 5:
        # test case ngẫu nhiên cho sub 1
        vmax = 100
    elif test_number <= 10:
        # test case ngẫu nhiên cho sub 2
        vmax = 100000
    elif test_number <= 15:
        # test case ngẫu nhiên cho sub 3
        vmax = 10000000
    else:
        # test case ngẫu nhiên cho sub 4
        vmax = 2 ** 31 - 1

    a = rand_int(0, vmax)
    b = rand_int(0, vmax)
    m = rand_int(1, 46340)

    print(a, b, m)
