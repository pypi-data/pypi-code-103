from DZDutils.list import divide

my_ultra_long_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
for chunk in divide(my_ultra_long_list, 3):
    print(chunk)
