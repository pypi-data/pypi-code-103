#!usr/bin/python3
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pybedtools import BedTool
from argparse import ArgumentParser

LOGGER = logging.getLogger("Compare")
BED_COLUMNS = ['chr', 'start', 'end', 'positions', 'SMAP', 'strand',
               'cigars', 'RD', 'stack_depth', 'stack_number_count', 'label']


def get_set_information(smap_set: Path):
    final_stacks = pd.read_csv(smap_set, names=BED_COLUMNS, header=0, index_col=0, sep="\t")
    label_set_list = set(final_stacks['label'])
    if len(label_set_list) > 1:
        raise ValueError(f'{label_set_list} contains more then one SMAP ' +
                         'set (more than one distinct value in column 11).')
    set_label = label_set_list.pop()
    max_number_of_samples = final_stacks['stack_number_count'].max()
    return set_label, max_number_of_samples


def intersect(smap_set1: Path, smap_set2: Path):
    # extract name of set from both files, extract maximal number of samples from both files.
    label_set1, max_number_of_samples_set1 = get_set_information(smap_set1)
    label_set2, max_number_of_samples_set2 = get_set_information(smap_set2)

    joined_stacks = BedTool(smap_set1).cat(BedTool(smap_set2),
                                           s=True,
                                           d=-1,
                                           c="8,10,11",
                                           o="collapse,collapse,collapse")

    stack_combo = [[{'set1': [], 'set2': []} for j in range(max_number_of_samples_set1 + 1)]
                   for i in range(max_number_of_samples_set2 + 1)]

    for stack in joined_stacks:
        _, _, _, stack_depths, stack_counts, stack_names = stack
        stack_names_list, stack_counts_list, stack_depth_list = \
            stack_names.split(','), stack_counts.split(','), stack_depths.split(',')

        # ignore lines containing three or more overlapping stacks
        try:
            label1, label2 = stack_names_list
        except ValueError:
            try:
                label, = stack_names_list
            except ValueError:
                continue
            else:
                reverse = label == label1
                stack_count, = stack_counts_list
                stack_depth, = stack_depth_list
                stack_count, stack_depth = int(stack_count), int(stack_depth)
                if stack_count > \
                   (max_number_of_samples_set1 if not reverse else max_number_of_samples_set2):
                    continue
                depth = stack_depth / stack_count
                depth_dict = stack_combo[0][stack_count] if not reverse \
                    else stack_combo[stack_count][0]
                depth_dict['set1' if not reverse else 'set2'].append(depth)
        else:
            reverse = label2 == label_set1
            stack_count_set1, stack_count_set2 = stack_counts_list if not reverse \
                else reversed(stack_counts_list)
            stack_count_set1, stack_count_set2 = int(stack_count_set1), int(stack_count_set2)
            # ignore lines were the number of samples exceeds the given number
            if stack_count_set1 > max_number_of_samples_set1 or \
               stack_count_set2 > max_number_of_samples_set2:
                continue
            depth_set1, depth_set2 = stack_depth_list if not reverse else reversed(stack_depth_list)
            depth_set1, depth_set2 = int(depth_set1), int(depth_set2)
            relative_depth_set1 = depth_set1 / stack_count_set1
            relative_depth_set2 = depth_set2 / stack_count_set2

            stack_combo[stack_count_set2][stack_count_set1]['set1'].append(relative_depth_set1)
            stack_combo[stack_count_set2][stack_count_set1]['set2'].append(relative_depth_set2)

    return (stack_combo, label_set1, label_set2)


def plot_combo(stack_combo, label_set1, label_set2):
    plt.figure(figsize=(10, 10))
    # first plot is a heatmap of the number of overlapping stacks (including non-overlapping stacks)
    h1_dict = [[len(column['set1']) for column in row] for row in stack_combo]
    plt.subplot(411)
    heatmap(h1_dict, 'Number of overlapping stacks.', label_set1, label_set2, mask=False)

    # second plot is a heatmap of the number of
    # overlapping stacks (excluding non-overlapping stacks)
    h2_dict = [[len(column['set2']) for column in row] for row in stack_combo]
    plt.subplot(412)
    heatmap(h2_dict, 'Number of overlapping stacks.', label_set1, label_set2, mask=False, vmax=1000)

    # third plot is a heatmap of the mean read
    # depth of overlapping stacks for label_set1s
    h3_dict = [[np.nanmean(column['set1']) if column['set1'] else np.NaN for column in row]
               for row in stack_combo]
    plt.subplot(413)
    heatmap(h3_dict, f'Mean stack stack depth {label_set1}', label_set1, label_set2, mask=True)

    # fourth plot is a heatmap of the mean read depth of overlapping stacks for label_set2s
    h4_dict = [[np.nanmean(column['set2']) if column['set2'] else np.NaN for column in row]
               for row in stack_combo]
    plt.subplot(414)
    heatmap(h4_dict, f'Stack depth {label_set2}', label_set1, label_set2, mask=True)

    plt.tight_layout()
    plt.savefig('SMAP_compare.pdf', format='pdf')


def heatmap(data_dict, title, xlabel, ylabel, mask=True, **kwargs):
    dataframe = pd.DataFrame(data_dict)
    masked = dataframe.isnull() if mask else None
    heatmap_plot = sns.heatmap(dataframe, cmap=sns.color_palette("RdPu"), mask=masked, **kwargs)
    heatmap_plot.set_facecolor('lightgray')
    heatmap_plot.set_yticklabels(heatmap_plot.get_yticklabels(), rotation=0, fontsize=8)
    heatmap_plot.set_xticklabels(heatmap_plot.get_xticklabels(), fontsize=8)
    heatmap_plot.set_title(title)
    heatmap_plot.set_xlabel(xlabel)
    heatmap_plot.set_ylabel(ylabel)


def parse_args(args):
    compare_parser = ArgumentParser("compare",
                                    description="Compare merged stacks of two SMAP outputs.")

    compare_parser.add_argument('smap_set1',
                                type=Path,
                                help='SMAP output file for set 1')

    compare_parser.add_argument('smap_set2',
                                type=Path,
                                help='SMAP output file for set 2')
    return compare_parser.parse_args(args)


def main(args):
    LOGGER.info('SMAP compare started.')
    parsed_args = parse_args(args)
    if not parsed_args.smap_set1.is_file():
        raise ValueError(f"Smap set {parsed_args.smap_set1!s} was not found.")
    if not parsed_args.smap_set2.is_file():
        raise ValueError(f"Smap set {parsed_args.smap_set2!s} was not found.")
    stack_combo, label_set1, label_set2 = intersect(parsed_args.smap_set1, parsed_args.smap_set2)
    LOGGER.info('Overlapping stacks from %s and %s', label_set1, label_set2)
    LOGGER.info('Plotting')
    plot_combo(stack_combo, label_set1, label_set2)
    LOGGER.info('Finished')
