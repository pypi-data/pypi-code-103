#!/usr/bin/env python
"""Takes the <ObsID>_smear_[cpp|py].txt files and plots two at the
same time for comparison.
"""

import argparse

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def read_data(path: Path) -> dict:
    s = list()
    el = list()
    e = list()
    with open(path) as f:
        # for i in range(10000):
        #    line = f.readline()
        for line in f:
            if line.startswith("#") or line.isspace():
                continue
            else:
                tokens = line.strip().split()
                s.append(float(tokens[0]))
                el.append(float(tokens[1]))
                e.append(float(tokens[2]))
    return s, el, e


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file1", type=Path)
    parser.add_argument("file2", type=Path)

    args = parser.parse_args()

    samp1, line1, et1 = read_data(args.file1)
    samp2, line2, et2 = read_data(args.file2)

    plt.ioff()
    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(3, 1)

    axtop = fig.add_subplot(gs[0, 0])
    axtop.set_xlabel("ET")
    axtop.set_ylabel("Sample")

    axbot = fig.add_subplot(gs[1, 0])
    axbot.set_xlabel("ET")
    axbot.set_ylabel("Line")

    axdiff = fig.add_subplot(gs[2, 0])
    axdiff.set_ylabel("Diff")

    axtop.plot(et1, samp1, "o", c="red")
    axtop.plot(et2, samp2, "o", c="blue", ms=2.5)

    axbot.plot(et1, line1, "o", c="red")
    axbot.plot(et2, line2, "o", c="blue", ms=2.5)

    # l1arr = np.array(line1[:-1])
    # l1arr = np.array(line1)
    # l2arr = np.array(line2)
    l2interp = np.interp(et1, et2, line2)

    # s1arr = np.array(samp1[:-1])
    # s1arr = np.array(samp1)
    # s2arr = np.array(samp2)
    s2interp = np.interp(et1, et2, samp2)

    # linediff = l1arr - l2arr
    # sampdiff = s1arr - s2arr
    linediff = line1 - l2interp
    sampdiff = samp1 - s2interp

    ldmax = np.max(np.abs(linediff))
    sdmax = np.max(np.abs(sampdiff))

    axdiff.plot(et1, linediff, c="purple", label=f"Line Diff Max: {ldmax}")
    axdiff.plot(et1, sampdiff, c="orange", label=f"Sample Diff Max: {sdmax}")
    axdiff.legend()

    plt.show()
