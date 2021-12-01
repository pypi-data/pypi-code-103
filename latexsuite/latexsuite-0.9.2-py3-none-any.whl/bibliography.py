"""
Creation of bibliography (bib) file with required entries subset of all bib entries in several files.
"""

import os

from pybtex import database as bib_parser


def get_all_references_from_aux(aux_file_path):
    """
    Determine citation keys from aux file.

    :param aux_file_path:
        The path of the aux file.
    :return:
    [str]
        The list of all citation keys.
    """
    all_references = set()
    with open(aux_file_path, "r") as aux_file:
        for line in aux_file:
            if line.startswith("\\abx@aux@cite") or line.startswith("\\citation"):
                reference = line.strip().replace("\\abx@aux@cite{", "").replace("\\citation{", "").replace("}", "")
                for one_reference in reference.split(","):
                    all_references.add(one_reference)
    return all_references


def add_entries_from_file(citation_keys, bib_folder_path, bib_db, fields_to_remove, errors_list):
    """
    Adds all references from the files in the bib folder which have a citation key in the specified set
    to the db of references.

    Only files with the extension 'bib' are considered.

    :param citation_keys: [str]
        List of citation keys to look for.
    :param bib_folder_path:
        The folder with bib files path.
    :param bib_db: bib_parser.BibliographyData
        A database to add references to.
    :param fields_to_remove: [str]
        Reference entries' fields that should be removed before adding an entry to the db.
    :param errors_list:
        A list to add any occurring errors to
    """
    for one_file in os.listdir(bib_folder_path):
        if one_file.endswith(".bib"):
            bib_file_bib_db = bib_parser.parse_file(os.path.join(bib_folder_path, one_file))
            for key, entry in bib_file_bib_db.entries.items():
                try:
                    if key in citation_keys:
                        for one_field_to_remove in fields_to_remove:
                            if one_field_to_remove in entry.fields:
                                entry.fields.pop(one_field_to_remove)
                        for field_key in list(entry.fields.keys()):
                            if "\\&" in entry.fields[field_key]:
                                entry.fields[field_key] = entry.fields[field_key].replace("\\&", "&")
                        bib_db.add_entry(key, entry)
                except bib_parser.BibliographyDataError as ex_bib:
                    errors_list.append(ex_bib)


def create_bib_file(aux_file_path, bib_folder_path, out_file_path, fields_to_remove=None):
    """
    Determines all citation keys from an aux file and creates a bib file with all
    the references for these citation keys.

    :param aux_file_path:
        The aux file path.
    :param bib_folder_path:
        The folder with bib files path.
    :param out_file_path:
        The path of the bib file to write to.
    :param fields_to_remove: [str]
        Reference entries' fields that should be removed before adding an entry to the bib file.
    :return:
    [bib_parser.BibliographyDataError]
        A list of errors.
    """
    if fields_to_remove is None:
        fields_to_remove = []
    errors = []
    citation_keys = get_all_references_from_aux(aux_file_path)
    full_bib_db = bib_parser.BibliographyData()
    add_entries_from_file(citation_keys, bib_folder_path, full_bib_db, fields_to_remove, errors)
    full_bib_db.to_file(out_file_path)
    return errors
