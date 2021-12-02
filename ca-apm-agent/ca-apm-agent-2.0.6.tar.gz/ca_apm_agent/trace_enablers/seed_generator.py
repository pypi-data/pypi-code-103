__copyright__ = """
* Copyright (c) 2018 CA. All rights reserved.
*
* This software and all information contained therein is confidential and proprietary and
* shall not be duplicated, used, disclosed or disseminated in any way except as authorized
* by the applicable license agreement, without the express written permission of CA. All
* authorized reproductions must be marked with this language.
*
* EXCEPT AS SET FORTH IN THE APPLICABLE LICENSE AGREEMENT, TO THE EXTENT
* PERMITTED BY APPLICABLE LAW, CA PROVIDES THIS SOFTWARE WITHOUT WARRANTY
* OF ANY KIND, INCLUDING WITHOUT LIMITATION, ANY IMPLIED WARRANTIES OF
* MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT WILL CA BE
* LIABLE TO THE END USER OR ANY THIRD PARTY FOR ANY LOSS OR DAMAGE, DIRECT OR
* INDIRECT, FROM THE USE OF THIS SOFTWARE, INCLUDING WITHOUT LIMITATION, LOST
* PROFITS, BUSINESS INTERRUPTION, GOODWILL, OR LOST DATA, EVEN IF CA IS
* EXPRESSLY ADVISED OF SUCH LOSS OR DAMAGE.
"""


# This code is not used anywhere, but left for future usage. This was part of an earlier design
class SeedGenerator:
    def __init__(self, seed_queue):
        self.queue = seed_queue
        self.max_value = 2 ** 32  # python can keep counting, this is for Java's limitations
        self.queue.put(1)
        store = 1
        split = self.max_value / 100000
        for i in range((split - 1)):
            store = store + split
            self.queue.put(store)

    def worker(self):
        import time
        while True:
            if self.queue.qsize() < 10:
                self.queue.put(1)
                store = 1
                split = self.max_value / 100000
                for i in range((split - 1)):
                    store = store + split
                    self.queue.put(store)
            time.sleep(300)
