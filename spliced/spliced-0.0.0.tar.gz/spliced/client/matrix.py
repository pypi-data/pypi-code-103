# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


import spliced.experiment
import random
import requests
import sys
import json


def main(args, parser, extra, subparser):

    # Generate a base experiment
    experment = spliced.experiment.Experiment()
    experiment.load(args.config_yaml)

    if args.generator == "spack":
        generate_spack_matrix(args, experiment)


def generate_spack_matrix(args, experiment)
    """A spack matrix derives versions from spack, and prepares 
       to generate commands (and metadata) to support a spack splice 
       experiment
    """
    # Get versions of package
    versions = requests.get(
        "https://raw.githubusercontent.com/spack/packages/main/data/packages/%s.json"
        % pkg
    )
    if versions.status_code != 200:
        sys.exit("Failed to get package versions")
    versions = versions.json()
    versions = list(set([x["name"] for x in versions["versions"]]))

    # We will build up a matrix of container and associated compilers
    matrix = []
    print(args.container)
    response = requests.get("https://crane.ggcr.dev/config/%s" % args.container)
    if response.status_code != 200:
        sys.exit(
            "Issue retrieving image config for % container: %s"
            % (args.container, response.reason)
         )

    config = response.json()
    labels = config["config"].get("Labels", {}).get("org.spack.compilers")

    # If the container has labels, we can use them to pin compilers
    if not labels:
        labels = ["all"]
    else:
        labels = [x for x in labels.strip("|").split("|") if x]

    # programatically get labels or default to "all compilers in the image"
    for label in labels:
        name = (
            container.split("/")[-1]
            .replace("spack", "")
            .replace(":", "-")
            .strip("-")
        )
        if "gcc" not in name and "clang" not in name:
            name = name + "-" + label.replace("@", "-")

        # TODO this needs to be a command instead, when UI for that developer
        for version in versions:
            container_name = version + "-" + name
            matrix.append(
                [
                    container,
                    label,
                    container_name,
                    experiment.package,
                    version,
                    experiment.splice,
                    experiment.command,
                    experiment.experiment,
                    experiment.replace,
                ]
            )

    # We can only get up to 256 max - select randomly
    if len(matrix) >= 256:
        print(
            "Warning: original output is length %s and we can only run 256 jobs!"
            % len(matrix)
        )
        matrix = random.sample(matrix, 256)

    if args.outfile:
        write_json(matrix, args.outfile)    
    print("::set-output name=containers::%s\n" % json.dumps(matrix))
