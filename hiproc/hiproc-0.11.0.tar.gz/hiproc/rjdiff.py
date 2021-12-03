#!/usr/bin/env python
"""Takes the <ObsID>_jitter_plot_[cpp|py].txt files and plots two at the
same time for comparison.
"""

import argparse
import re

from pathlib import Path

import matplotlib.pyplot as plt


def read_data(path: Path) -> dict:
    lines = path.read_text().splitlines()
    labels = lines[0].lstrip('# ').split()
    lists = [[] for i in range(len(labels))]
    for line in lines[1:]:
        tokens = line.split()
        for i, token in enumerate(tokens):
            if token != "nan":
                lists[i].append(float(token))

    return dict(zip(labels, lists))


def get_titles(path: Path) -> list:
    plt_p = path.with_suffix(".plt")

    text = plt_p.read_text()

    t = list()
    for i in (1, 2, 3):
        # m = re.search(fr"filePath{i}\s+=\s+'.*/?(\S+)\.flat\.tab'", text)
        m = re.search(fr"filePath{i}\s+=\s+'(\S+)'", text)
        if m is None:
            raise ValueError(f"filePath{i} could not be found in {plt_p}")
        else:
            # t.append(m.group(1))
            p = Path(m.group(1))
            # The expectation is that this will end in .flat.tab, so x2
            t.append(p.with_suffix("").with_suffix("").stem)

    return t


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file1", type=Path)
    parser.add_argument("file2", type=Path)

    args = parser.parse_args()

    titles = get_titles(args.file1)
    t2 = get_titles(args.file2)
    if titles != t2:
        raise ValueError(
            f"The titles in file1 ({titles}) do not match the titles in "
            f"file 2 ({t2})"
        )

    one = read_data(args.file1)
    two = read_data(args.file2)

    plt.ioff()
    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(3, 6)

    ax00 = fig.add_subplot(gs[0, 0:2])
    ax00.set_title(titles[0])

    ax01 = fig.add_subplot(gs[0, 2:4])
    ax01.set_title(titles[1])

    ax02 = fig.add_subplot(gs[0, 4:])
    ax02.set_title(titles[2])

    ax10 = fig.add_subplot(gs[1, 0:2])
    ax11 = fig.add_subplot(gs[1, 2:4])
    ax12 = fig.add_subplot(gs[1, 4:])

    ax20 = fig.add_subplot(gs[2, 0:3])
    ax20.set_title("Cross-Track Jitter")

    ax21 = fig.add_subplot(gs[2, 3:])
    ax21.set_title("Down-Track Jitter")

    ax00.set_ylabel('X, Cross-Track')
    ax00.plot(one["t1_shift"], one["offx1"], "o", c="red")
    ax00.plot(two["t1_shift"], two["offx1"], "o", c="pink", ms=2.5)
    ax00.plot(one["ET_shift"], one["xinterp1"], c="green")
    ax00.plot(two["ET_shift"], two["xinterp1"], c="lime", ls="--", lw=0.5)
    ax00.plot(one["ET_shift"], one["jittercheckx1_shift"], c="yellow")
    ax00.plot(two["ET_shift"], two["jittercheckx1_shift"], c="gold")

    ax01.plot(one["t2_shift"], one["offx2"], "o", c="red")
    ax01.plot(two["t2_shift"], two["offx2"], "o", c="pink", ms=2.5)
    ax01.plot(one["ET_shift"], one["xinterp2"], c="green")
    ax01.plot(two["ET_shift"], two["xinterp2"], c="lime", ls="--", lw=0.5)
    ax01.plot(one["ET_shift"], one["jittercheckx2_shift"], c="yellow")
    ax01.plot(two["ET_shift"], two["jittercheckx2_shift"], c="gold")

    ax02.plot(one["t3_shift"], one["offx3"], "o", c="red")
    ax02.plot(two["t3_shift"], two["offx3"], "o", c="pink", ms=2.5)
    ax02.plot(one["ET_shift"], one["xinterp3"], c="green")
    ax02.plot(two["ET_shift"], two["xinterp3"], c="lime", ls="--", lw=0.5)
    ax02.plot(one["ET_shift"], one["jittercheckx3_shift"], c="yellow")
    ax02.plot(two["ET_shift"], two["jittercheckx3_shift"], c="gold")

    ax10.set_ylabel('Y, Down-Track')
    ax10.plot(one["t1_shift"], one["offy1"], "o", c="red", label="F1, Offset")
    ax10.plot(two["t1_shift"], two["offy1"], "o", c="pink", ms=2.5, label="F2, Offset")
    ax10.plot(one["ET_shift"], one["yinterp1"], c="green", label="F1, interp")
    ax10.plot(two["ET_shift"], two["yinterp1"], c="lime", ls="--", lw=0.5, label="F2, interp")
    ax10.plot(one["ET_shift"], one["jitterchecky1_shift"], c="yellow", label="F1, jittercheck")
    ax10.plot(two["ET_shift"], two["jitterchecky1_shift"], c="gold", label="F2, jittercheck")
    ax10.legend()

    ax11.plot(one["t2_shift"], one["offy2"], "o", c="red")
    ax11.plot(two["t2_shift"], two["offy2"], "o", c="pink", ms=2.5)
    ax11.plot(one["ET_shift"], one["yinterp2"], c="green")
    ax11.plot(two["ET_shift"], two["yinterp2"], c="lime", ls="--", lw=0.5)
    ax11.plot(one["ET_shift"], one["jitterchecky2_shift"], c="yellow")
    ax11.plot(two["ET_shift"], two["jitterchecky2_shift"], c="gold")

    ax12.plot(one["t3_shift"], one["offy3"], "o", c="red")
    ax12.plot(two["t3_shift"], two["offy3"], "o", c="pink", ms=2.5)
    ax12.plot(one["ET_shift"], one["yinterp3"], c="green")
    ax12.plot(two["ET_shift"], two["yinterp3"], c="lime", ls="--", lw=0.5)
    ax12.plot(one["ET_shift"], one["jitterchecky3_shift"], c="yellow")
    ax12.plot(two["ET_shift"], two["jitterchecky3_shift"], c="gold")

    ax20.plot(one["ET_shift"], one["Sample"], c="blue")
    ax20.plot(two["ET_shift"], two["Sample"], c="cyan", ls="--")
    ax21.plot(one["ET_shift"], one["Line"], c="blue")
    ax21.plot(two["ET_shift"], two["Line"], c="cyan", ls="--")

    plt.show()
