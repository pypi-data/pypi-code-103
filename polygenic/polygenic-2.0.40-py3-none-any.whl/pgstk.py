import argparse
import logging

import sys
import os
import urllib.request

import configparser
import tabix

import yaml 

from polygenic.tools import pgscompute
from polygenic.tools import modelbiobankuk
from polygenic.tools import modelpgscat

# utils
# simulate
from polygenic.data.vcf_accessor import VcfAccessor
from polygenic.data.vcf_accessor import DataNotPresentError
from polygenic.model.utils import is_valid_path
from polygenic.model.utils import download
from polygenic.model.utils import read_header
from polygenic.model.utils import read_table
from polygenic.error.polygenic_exception import PolygenicException
# clumping
import subprocess
import re
# simlating
import random
import statistics
# saving
import json

logger = logging.getLogger('polygenicmaker')
config = configparser.ConfigParser()
config.read(os.path.dirname(__file__) + "/../polygenic/polygenic.cfg")

#######################
### vcf-index #########
#######################


def vcf_index(args):
    parser = argparse.ArgumentParser(
        description='vcf index indexes vcf file for query')  # todo dodać opis
    parser.add_argument('--vcf', type=str, required=True,
                        help='path to vcf file')
    parsed_args = parser.parse_args(args)
    VcfAccessor(parsed_args.vcf)
    return


#####################################################################################################
###                                                                                               ###
###                                   Polygenic Score Catalogue                                   ###
###                                                                                               ###
#####################################################################################################

#######################
### pgs-index #########
#######################

def pgs_index(args):
    parser = argparse.ArgumentParser(
        description='polygenicmaker pgs-index downloads index of gwas results from Polgenic Score Catalogue')  # todo dodać opis
    parser.add_argument('--url', type=str, default='http://ftp.ebi.ac.uk/pub/databases/spot/pgs/metadata/pgs_all_metadata_scores.csv',
                        help='alternative url location for index')
    parser.add_argument('--output', type=str, default='',
                        help='output directory')
    parsed_args = parser.parse_args(args)
    output_path = os.path.abspath(os.path.expanduser(
        parsed_args.output)) + "/pgs_manifest.tsv"
    download(parsed_args.url, output_path, force=True)
    return

#######################
### pgs-get ###########
#######################


def pgs_get(args):
    parser = argparse.ArgumentParser(
        description='polygenicmaker pgs-get downloads specific gwas result from polygenic score catalogue')  # todo dodać opis
    parser.add_argument('-c', '--code', type=str, required=False,
                        help='PGS score code. Example: PGS000814')
    parser.add_argument('-o', '--output-path', type=str,
                        default='', help='output directory')
    parser.add_argument('-f', '--force', action='store_true',
                        help='overwrite downloaded file')
    parsed_args = parser.parse_args(args)
    url = "http://ftp.ebi.ac.uk/pub/databases/spot/pgs/scores/" + \
        parsed_args.code + "/ScoringFiles/" + parsed_args.code + ".txt.gz"
    download(url=url, output_path=parsed_args.output_path,
             force=parsed_args.force, progress=True)
    return

#######################
### pgs-prepare #######
#######################

def pgs_prepare_model(args):
    parser = argparse.ArgumentParser(
        description='polygenicmaker pgs-prepare-model constructs polygenic score model')  # todo dodać opis
    parser.add_argument('-i', '--input', type=str,
                        required=True, help='path to PRS file from PGS.')
    parser.add_argument('-o', '--output-path', type=str,
                        required=True, help='path to output file.')
    parser.add_argument('--origin-reference-vcf', type=str,
                        required=True, help='path to rsid vcf.')
    parser.add_argument('--model-reference-vcf', type=str,
                        required=True, help='path to rsid vcf.')
    parser.add_argument('--af', type=str, required=True,
                        help='path to allele frequency vcf.')
    parser.add_argument('--pop', type=str, default='nfe',
                        help='population: meta, afr, amr, csa, eas, eur, mid')
    parser.add_argument('--iterations', type=float, default=1000,
                        help='simulation iterations for mean and sd')
    parsed_args = parser.parse_args(args)
    if not is_valid_path(parsed_args.input): return
    if not is_valid_path(parsed_args.origin_reference_vcf): return
    if not is_valid_path(parsed_args.model_reference_vcf): return
    if not is_valid_path(parsed_args.af): return
    data = read_table(parsed_args.input)
    af_vcf = VcfAccessor(parsed_args.af)
    origin_ref_vcf = VcfAccessor(parsed_args.origin_reference_vcf)
    model_ref_vcf = VcfAccessor(parsed_args.model_reference_vcf)

    clean_data = []
    for pgs_entry in data:
        origin_record = origin_ref_vcf.get_record_by_position(
            pgs_entry['chr_name'], pgs_entry['chr_position'])
        model_record = model_ref_vcf.get_record_by_rsid(origin_record.get_id())
        af_records = af_vcf.get_records_by_rsid(origin_record.get_id())
        af_record = None
        for record in af_records:
            if record.get_alt()[0] == pgs_entry['effect_allele']:
                af_record = record
                break
        if model_record is None and not af_record is None:
            model_record = af_record
        if origin_record is None or model_record is None:
            logger.warning("Variant {chromosome}:{position} is not present in reference.".format(
                chromosome=pgs_entry['chr_name'], position=pgs_entry['chr_position']))
            continue
        if not pgs_entry['reference_allele'] == origin_record.get_ref():
            logger.warning("Variant {chromosome}:{position} has mismatch nucleotide in reference.".format(
                chromosome=pgs_entry['chr_name'], position=pgs_entry['chr_position']))
            continue
        if not origin_record.get_ref() == model_record.get_ref():
            logger.warning("Variant {chromosome}:{position} has mismatch nucleotide between references (grch37 vs grch38).".format(
                chromosome=pgs_entry['chr_name'], position=pgs_entry['chr_position']))
            continue
        pgs_entry['rsid'] = origin_record.get_id()
        if af_record is None:
            pgs_entry['af'] = 0.001
        else:
            pgs_entry['af'] = af_record.get_af_by_pop(
                'AF_' + parsed_args.pop)[pgs_entry['effect_allele']]
        pgs_entry['ALT'] = pgs_entry['effect_allele']
        pgs_entry['BETA'] = pgs_entry['effect_weight']
        clean_data.append(pgs_entry)

    description = simulate_parameters(clean_data)
    description.update(read_header(parsed_args.input))
    write_model(clean_data, description, parsed_args.output_path)

    return

#####################################################################################################
###                                                                                               ###
###                                   Global Biobank Engine                                       ###
###                                                                                               ###
#####################################################################################################

#######################
### gbe-index #########
#######################

def gbe_index(args):
    print("GBEINDEX")
    parser = argparse.ArgumentParser(
        description='polygenicmaker gbe-index downloads index of gwas results from pan.ukbb study')  # todo dodać opis
    parser.add_argument('--url', type=str, default='https://biobankengine.stanford.edu/static/degas-risk/degas_n_977_traits.tsv',
                        help='alternative url location for index')
    parser.add_argument('--output-directory', type=str, default='',
                        help='output directory')
    parsed_args = parser.parse_args(args)
    output_path = os.path.abspath(os.path.expanduser(
        parsed_args.output_directory)) + "/gbe_phenotype_manifest.tsv"
    download(parsed_args.url, output_path)
    return

###############
### gbe-get ###
###############

def gbe_get(parsed_args):
    url = "https://biobankengine.stanford.edu/static/PRS_map/" + parsed_args.code + ".tsv"
    output_directory = os.path.abspath(os.path.expanduser(parsed_args.output_directory))
    output_file_name = os.path.splitext(os.path.basename(url))[0]
    output_path = output_directory + "/" + output_file_name
    download(url=url, output_path=output_path,
             force=parsed_args.force, progress=True)
    return output_path

#######################
### gbe-model #########
#######################

def gbe_model(args):
    parser = argparse.ArgumentParser(
        description='polygenicmaker biobankuk-build-model constructs polygenic score model based on p value data')  # todo dodać opis
    parser.add_argument('-c','--code', required=True, type=str, help='path to PRS file from gbe. It can be downloaded using gbe-get')
    parser.add_argument('-o', '--output-directory', type=str, default='output', help='output directory')
    parser.add_argument('--gbe-index', type=str, default='gbe-index.1.3.1.tsv', help='gbe-index')
    parser.add_argument('--source-ref-vcf', type=str, default='dbsnp155.grch37.norm.vcf.gz', help='source reference vcf (hg19)')
    parser.add_argument('--target-ref-vcf', type=str, default='dbsnp155.grch38.norm.vcf.gz', help='source reference vcf (hg38)')
    parser.add_argument('--af-vcf', type=str, default='gnomad.3.1.vcf.gz', help='path to allele frequency vcf.')
    parser.add_argument('--af-field', type=str, default='AF_nfe', help='name of the INFO field with ALT allele frequency')
    parser.add_argument('--gene-positions', type=str, default='ensembl-genes.104.tsv', help='table with ensembl genes')
    parser.add_argument('-i', '--iterations', type=float, default=1000, help='simulation iterations for mean and sd')
    parser.add_argument('-f', '--force', action='store_true', help='overwrite downloaded file')
    parsed_args = parser.parse_args(args)

    if not is_valid_path(parsed_args.output_directory, is_directory=True): return
    path = gbe_get(parsed_args)

    if not is_valid_path(path): return
    data = read_table(path)

    if not is_valid_path(parsed_args.gbe_index): return
    gbe_index = read_table(parsed_args.gbe_index)
    info = [line for line in gbe_index if parsed_args.code in line['Trait name']][0]

    if not is_valid_path(parsed_args.gene_positions): return
    gene_positions = read_table(parsed_args.gene_positions)

    if not is_valid_path(parsed_args.af_vcf, possible_url = True): return
    af_vcf = VcfAccessor(parsed_args.af_vcf)

    if not is_valid_path(parsed_args.source_ref_vcf, possible_url = True): return
    source_vcf = VcfAccessor(parsed_args.source_ref_vcf)

    if not is_valid_path(parsed_args.target_ref_vcf, possible_url = True): return
    target_vcf = VcfAccessor(parsed_args.target_ref_vcf)

    data = [line for line in data if "rs" in line['ID']]
    for line in data: line.update({"rsid": line['ID']})
    data = [validate(line, validation_source = target_vcf) for line in data]

    for line in data:
        if not "rsid" in line:
            print(line)

    data = [line for line in data if "rs" in line['ID']]

    data = [add_annotation(
        line, 
        annotation_name = "af", 
        annotation_source = af_vcf, 
        annotation_source_field = parsed_args.af_field,
        default_value = 0.001) for line in data]

    symbols = [add_gene_symbol(
        line, 
        target_vcf, 
        gene_positions) for line in data]
    symbols = [symbol for symbol in symbols if symbol]

    description = dict()
    parameters = simulate_parameters(data)
    description["pmids"] = [33095761]
    description["info"] = info
    description["parameters"] = parameters
    description["genes"] = symbols

    model_path = parsed_args.output_directory + "/" + parsed_args.code + ".yml"
    write_model(data, description, model_path)
    return




def main(args=sys.argv[1:]):
    try:
        if args[0] == 'pgs-compute':
            pgscompute.main(args[1:])
        elif args[0] == 'model-biobankuk':
            modelbiobankuk.main(args[1:])
        elif args[0] == 'model-pgscat':
            modelpgscat.main(args[1:])
        elif args[0] == 'vcf-index':
            vcf_index(args[1:])
        else:
            print('ERROR: Please select proper tool name"')
            print("""
            Program: polygenicmaker (downloads gwas data, clumps and build polygenic scores)
            Contact: Marcin Piechota <piechota@intelliseq.com>
            Usage:   pgstk <command> [options]

            Command:
            pgs-compute             computes pgs score for vcf file
            model-biobankuk         prepare polygenic score model based on gwas results from biobankuk
            model-pgscat            prepare polygenic score model based on gwas results from PGS Catalogue
            vcf-index               prepare rsidx for vcf

            """)
    except PolygenicException as e:
        print("Analysis failed")
        print("ERROR: " + str(e))
    except RuntimeError as e:
        print("ERROR: " + str(e))

if __name__ == '__main__':
    main(sys.argv[1:])
