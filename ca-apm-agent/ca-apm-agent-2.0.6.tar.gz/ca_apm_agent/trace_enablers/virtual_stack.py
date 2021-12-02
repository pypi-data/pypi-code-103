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
import threading
from ca_apm_agent.python_modifiers.singleton import Singleton

JAVA_MAX = 9223372036854775807


class VirtualStack(Singleton):
    local_store = threading.local()

    def __init__(self):
        self.max = JAVA_MAX
        self.ls = VirtualStack.local_store

    def init(self):
        if not hasattr(self.ls, 'seed'):
            self.ls.seed = 0
            self.ls.seq = self.ls.seed
            self.ls.trace_id = self.ls.seed
            self.ls.stack = []

    def is_empty(self):
        if self.ls.stack:
            return False
        else:
            return True

    def push(self, value):
        self.ls.stack.append(value)

    def pop(self):
        if self.ls.stack:
            return self.ls.stack.pop()
        else:
            return None

    def peek(self):
        if self.ls.stack:
            return self.ls.stack[-1]
        else:
            return None
            
    def peekIndex(self, index):
        try:
            if self.ls.stack:
                return self.ls.stack[index]
            else:
                return None
        except IndexError:
            return None            

    def size(self):
        return len(self.ls.stack)

    def get_seq(self):
        self.ls.seq += 1
        if self.ls.seq > self.max:
            self.ls.seq = self.ls.seed + 1
        return self.ls.seq

    def get_trace_id(self):
        if not self.ls.stack:
            self.ls.trace_id += 1
            if self.ls.seq + 2000 > self.max:
                self.ls.seq = self.ls.seed
            if self.ls.trace_id > self.max:
                self.ls.trace_id = self.ls.seed + 1
        return self.ls.trace_id
