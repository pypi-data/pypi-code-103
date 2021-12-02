#! /usr/bin/env python3

"""
author: Nicolas JEANNE
email: jeanne.n@chu-toulouse.fr
Created on 22 jan. 2020
Copyright (C) PTI CHU Purpan
"""

import os
import subprocess
import sys


def hpc_mafft(path_input, path_output, cores=1, high_accuracy_method=None):
    """
    Align sequences from fasta records with MAFFT on the IUCT cluster if the loaded conda environment contains MAFFT.

    :param str path_input: the path of the input fasta file.
    :param str path_output: the path of the output fasta file.
    :param int cores: the number of provided cores.
    :param str high_accuracy_method: the high accuracy method (for <~200 sequences x <~2,000 aa/nt). Default is
    None, the allowed choices are "localpair", "genafpair" or "globalpair". See MAFFT help for more
    details.
    :return: the alignment path.
    :rtype: str
    """

    cmd = "mafft --thread {} --quiet {}".format(cores, path_input)
    if high_accuracy_method is not None:
        if high_accuracy_method not in ["localpair", "genafpair", "globalpair"]:
            raise ValueError(
                "{} high_accuracy_method argument should be: \"localpair\", \"genafpair\" or \"globalpair\".")

        cmd = "{} --{}".format(cmd, high_accuracy_method)
    cmd = "{} > {}".format(cmd, path_output)

    # run the alignment
    __run_alignment(cmd)

    return path_output


def hpc_tcoffee(path_input, path_output, seq_type="dna", pairwise=False, debug=False):
    """
    Align sequences from fasta records with T-COFFEE on the IUCT cluster if the loaded conda environment contains
    T-COFFEE.

    :param str path_input: the path of the input fasta file.
    :param str path_output: the path of the output fasta file.
    :param str seq_type: the type of sequence to align, choices are "dna", "rna" or "protein",
    default is "dna".
    :param bool pairwise: to do a pairwise alignment instead of a multiple sequences alignment.
    :param bool debug: to record the output steps of the alignment.
    :return: the alignment path.
    :rtype: str
    """

    read_id = os.path.splitext(os.path.basename(path_input))[0]
    # check the seq_type parameter
    if seq_type not in ["dna", "rna", "protein"]:
        raise ValueError("Function align_tcoffee: wrong value for \"seq_type\" parameter \"{}\", "
                         "correct values are \"dna\", \"rna\" or \"protein\".\n".format(seq_type))
    # set the command line
    cmd = " t_coffee -in=S{} -outfile {} -type {}".format(path_input, path_output, seq_type)
    if pairwise:
        cmd = "{} {}".format(cmd, "-dp_mode myers_miller_pair_wise")

    if debug:
        cmd = "{} {}".format(cmd, "-output=fasta_aln,html > {}._tcoffee.log".format(
            os.path.join(os.path.dirname(path_output), read_id)))
    else:
        cmd = "{} {}".format(cmd, "-output=fasta_aln -quiet")

    # run the alignment
    __run_alignment(cmd)

    return path_output


def __run_alignment(command):
    """
    Run the alignment command.

    :param command: the command of the aligner.
    :type command: str
    """
    process = subprocess.Popen(command,
                               stderr=subprocess.PIPE,
                               universal_newlines=True,
                               shell=(sys.platform != "win32"))

    while True:
        if process.poll() is not None:
            break
    if process.poll() != 0:
        raise subprocess.CalledProcessError(process.poll(), command, stderr=process.stderr)
    process.stderr.close()
