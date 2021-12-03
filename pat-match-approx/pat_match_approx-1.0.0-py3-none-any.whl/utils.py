from Bio import SeqIO


# THE PARSER
# reads and returns the seq as string from the FASTA/FASTQ file
def get_seq_from_file(file_path, fmt="fasta"):
    seqs = []

    for seq_record in SeqIO.parse(file_path, fmt):
        seqs.append(seq_record)

    return seqs


def output_sam(answers, fasta_seq, fastq_seq, output_file):
    for (label_idx, cigar) in answers:
        # TODO: replace the print statement with proper SAM output logic
        output_file.write(
            f"{fastq_seq.description}\t0\t{fasta_seq.description}\t{label_idx}\t0\t{cigar}\t*\t0\t0\t{fastq_seq.seq}\t{len(fastq_seq.seq) * '~'}")
        output_file.write("\n")
