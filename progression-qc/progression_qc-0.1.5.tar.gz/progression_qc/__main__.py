from progression_qc.progression_qc import *
import progression_qc
import traceback

if __name__ == "__main__":
    args = traiter_paramètres()

    if args.version:
        print(f"progression_qc version {progression_qc.__version__}")
        code_retour = 0
    else:

        try:
            infos_question = charger_question(args.fichier, get_readers())
            resultats = valider_schema_yaml_infos_question(infos_question)
            resultats["infos_question"] = infos_question
        except Exception as e:
            if args.verbose:
                print(traceback.format_exc(), file=sys.stderr)
            resultats = {"erreurs": {args.fichier: e}}

        code_retour = déterminer_code_retour(resultats)

        if not args.quiet:
            if args.json:
                afficher_résultats_json(resultats)
            else:
                afficher_résultats(resultats)

    exit(code_retour)
