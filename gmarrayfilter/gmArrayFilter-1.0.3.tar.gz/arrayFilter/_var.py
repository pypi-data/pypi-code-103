from pathlib import Path

FILE_SEP_MAP = {".txt": "\t", ".csv": ","}
LOCATION_COL = ["Chromosome", "Physical Position"]
MERGE_COLS = ["Probe Set ID", "Affy SNP ID", "Flank", "Allele A", "Allele B"]
KEEP_COLS = MERGE_COLS + LOCATION_COL
ID_NAME = "Probe Set ID"
GT_COL = "GenoType"
NA_CHARS = ["na"]

SCRIPT_DIR = Path(__file__).parent
CHR_SIZE_FILE = SCRIPT_DIR / "chr.size"
DENSITY_PLOT_R = SCRIPT_DIR / "array_plot.R"
PARAMS_CFG = SCRIPT_DIR / "params.cfg"
ARRAY_ANN_DIR = SCRIPT_DIR / "array_data"

LABEL_NAMES = ["mutant", "wild", "mutant_parent", "wild_parent"]


class SnpDensityStatsTable:
    CHROM = "chrom"
    START = "start"
    END = "end"
    COUNT = "variantCount"


class DataType:
    homo = "homozygous"
    mut_het = "mutant-heterozygous"
    wild_het = "wild-heterozygous"


class HybridStrategy:
    homo = "homozygous"
    het = "heterozygous"
    both = "both"
    homo_like = ["homozygous", "both"]
    het_like = ["heterozygous", "both"]


class AlleleType:
    HYBRID = "HS"
    NA = "NA"


class EchoPrefix:
    error = "[ERROR]"
    info = "[INFO]"
    warning = "[WARNING]"
