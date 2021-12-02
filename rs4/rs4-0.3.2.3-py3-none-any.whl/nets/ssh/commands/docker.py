from . import default
import re

RX_spt = re.compile ("\s{2,}")

class Result (default.Result):
    def parse_output (self, outputs):
        lines = outputs.split ("\n")
        self.header = lines [0]
        d = {}
        for line in lines [1:-1]:
            d = RX_spt.split (line)
            self.data.append ({
                'Container Name': d [-1],
                'Created': d [3],
                'Status': d [4],
            })
