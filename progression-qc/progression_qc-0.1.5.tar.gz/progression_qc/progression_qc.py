#!/usr/bin/python3
from cerberus import Validator, schema_registry
import argparse
import json
import os
import pathlib
import re
import sys
import urllib
import yaml
import yamlinclude
import werkzeug.urls

try:
    import importlib.resources as pkg_resources
except:
    import importlib_resources as pkg_resources

from . import schemas

__args__ = None


def traiter_validation_question_yaml(contenu_yaml, schema):
    v = Validator(schema)
    v.allow_unknown = True
    v.validate(contenu_yaml)
    erreurs = v.errors

    v.allow_unknown = False
    v.validate(contenu_yaml, normalize=True)

    avertissements = {k: v.errors[k] for k in v.errors if k not in erreurs}

    return {"erreurs": erreurs, "avertissements": avertissements}


def valider_schema_yaml_infos_question(contenu_fichier):
    schema_registry.add(
        "rétroactions", eval(pkg_resources.read_text(schemas, "rétroactions.py"))
    )
    schema_registry.add(
        "question_base", eval(pkg_resources.read_text(schemas, "question_base.py"))
    )
    schema_registry.add(
        "question_prog",
        {
            **schema_registry.get("question_base"),
            **eval(pkg_resources.read_text(schemas, "question_prog.py")),
        },
    )

    if "type" in contenu_fichier and contenu_fichier["type"] == "prog":
        schemas_à_valider = "question_prog"
    else:
        schemas_à_valider = "question_base"

    return traiter_validation_question_yaml(contenu_fichier, schemas_à_valider)


def get_readers():
    class URLYamlReader(yamlinclude.YamlReader):
        def __call__(self):
            chemin = werkzeug.urls.iri_to_uri(self._path)
            if __args__.verbose:
                print(f"Inclusion du fichier YML : {chemin}...", file=sys.stderr)
            with urllib.request.urlopen(chemin) as fp:
                résultat = yaml.load(fp, self._loader_class)
            if __args__.verbose:
                print(f"Fin {chemin}", file=sys.stderr)
            return résultat

    class URLPlainTextReader(yamlinclude.PlainTextReader):
        def __call__(self):
            chemin = werkzeug.urls.iri_to_uri(self._path)
            if __args__.verbose:
                print(f"Inclusion du fichier texte : {chemin}...", file=sys.stderr)
            with urllib.request.urlopen(chemin) as fp:
                résultat = fp.read().decode("utf8")
            if __args__.verbose:
                print(f"Fin {chemin}", file=sys.stderr)
            return résultat

    return [
        (re.compile(r"^.+\.ya?ml$", re.IGNORECASE), URLYamlReader),  # *.yml, *.yaml
        (re.compile(r"^.+$"), URLPlainTextReader),  # *
    ]


def charger_question(cible, readers):
    url = urllib.parse.urlparse(cible)

    if url.scheme == "":
        base = pathlib.Path(os.path.abspath(os.path.dirname(cible))).as_uri()
    else:
        base = werkzeug.urls.iri_to_uri(os.path.dirname(cible))

    filename = os.path.basename(url.path)

    yamlinclude.YamlIncludeConstructor.add_to_loader_class(
        loader_class=yaml.SafeLoader, reader_map=readers, base_dir=base
    )

    if __args__.verbose:
        print(f"Chargement du fichier : {filename}")
    return yaml.load(f"!include {filename}", Loader=yaml.SafeLoader)


def afficher_résultats_json(resultats):
    if "erreurs" in resultats and len(resultats["erreurs"]) > 0:
        afficher_erreurs_json(resultats["erreurs"])
        print("---", file=sys.stderr)

    if "avertissements" in resultats and len(resultats["avertissements"]) > 0:
        afficher_avertissements_json(resultats["avertissements"])
        print("---", file=sys.stderr)

    if "infos_question" in resultats:
        afficher_question_json(resultats["infos_question"])


def afficher_résultats(resultats):
    if "erreurs" in resultats and len(resultats["erreurs"]) > 0:
        afficher_erreurs(resultats["erreurs"])

    if "avertissements" in resultats and len(resultats["avertissements"]) > 0:
        afficher_avertissements(resultats["avertissements"])

    if "infos_question" in resultats:
        afficher_question(resultats["infos_question"])


def afficher_question(infos_question):
    print(yaml.dump(infos_question, allow_unicode=True))


def afficher_question_json(infos_question):
    print(json.dumps(infos_question, ensure_ascii=False))


def afficher_erreurs(erreurs):
    for erreur in erreurs:
        print(f"ERREUR : {erreur} > {erreurs[erreur]}", file=sys.stderr)


def afficher_erreurs_json(erreurs):
    print("{erreurs: " + str(erreurs) + "}", file=sys.stderr)


def afficher_avertissements(avertissements):
    for avertissement in avertissements:
        print(
            f"AVERTISSEMENT : {avertissement} > {avertissements[avertissement]}",
            file=sys.stderr,
        )


def afficher_avertissements_json(avertissements):
    print("{avertissements: " + str(avertissements) + "}", file=sys.stderr)


def traiter_paramètres():
    parser = argparse.ArgumentParser(
        description="progression_qc est un compilateur/validateur pour la production de d'exercices pour Progression. dprogression_qc reçoit sur l'entrée standard ou en paramètre un fichier YAML contenant la description d'une question et reproduit sur la sortie standard le résultat traité et validé."  # noqa: E501
    )
    verbosité = parser.add_mutually_exclusive_group()
    verbosité.add_argument(
        "-v", "--verbose", action="store_true", help="Affiche plus d'information."
    )
    verbosité.add_argument(
        "-q", "--quiet", action="store_true", help="Ne produit aucun affichage."
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="affiche le résultat et les erreurs/avertissements de validation en format JSON. Par défaut, le résultat est affiché en YAML et les erreurs/avertissements de la validation est en format humainement lisible.",  # noqa: E501
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="l'exercice n'est considéré valide que si aucune erreur ni avertissement n'a été produit.",  # noqa: E501
    )
    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        help="Affiche la version de progression_qc et termine.",
    )
    parser.add_argument(
        "fichier",
        type=str,
        nargs="?",
        help="Le fichier YML à valider.",
        default="/dev/stdin",
    )

    global __args__
    __args__ = parser.parse_args()

    return __args__


def déterminer_code_retour(resultats):
    if "erreurs" in resultats and len(resultats["erreurs"]) > 0:
        return 1
    elif "avertissements" in resultats and len(resultats["avertissements"]) > 0:
        return 2 if __args__.strict else 0
    return 0
