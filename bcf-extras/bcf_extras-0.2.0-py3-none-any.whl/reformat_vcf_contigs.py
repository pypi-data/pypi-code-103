import re
import subprocess
import sys

from typing import List

__all__ = [
    "reformat_vcf_contigs",
]


def reformat_vcf_contigs(vcfs: List[str], with_chr: bool = False):
    for vcf in vcfs:
        is_bgzipped = vcf.endswith(".gz")

        if is_bgzipped:
            subprocess.check_call(["bgzip", "-d", vcf])
            vcf = vcf.rstrip(".gz")

        # TODO

        tmp_vcf = f"{vcf}.tmp"

        with open(vcf, "rb") as ifh, open(tmp_vcf, "wb") as ofh:
            for line in ifh:
                if line.startswith(b"##reference"):
                    print("WARNING: Changing the names of contigs may invalidate connections between the VCF and the "
                          "linked reference", file=sys.stderr, flush=True)

                if line.startswith(b"##") and not line.startswith(b"##contig"):
                    ofh.write(line)

        if is_bgzipped:
            subprocess.check_call(["bgzip", vcf])

