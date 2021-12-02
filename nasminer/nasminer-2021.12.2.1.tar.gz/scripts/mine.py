import sys
import time

from nasminer import crawler

if __name__ == '__main__':
    topdir = sys.argv[1]
    start_time = time.time()
    crawler.run(topdir)
    end_time = time.time()
    print(f'Ran for {end_time - start_time} seconds')
