from setuptools import setup

setup(
    name="progression_qc",
    version="0.1.6",
    description="progression_qc est un compilateur/validateur pour la production de d'exercices pour Progression. progression_qc reçoit sur l'entrée standard ou en paramètre un fichier YAML contenant la description d'une question et reproduit sur la sortie standard le résultat traité et validé.",
    url="https://git.dti.crosemont.quebec/progression/validateur",
    author="Patrick Lafrance",
    author_email="plafrance@crosemont.qc.ca",
    license='GPLv3+',
    packages=["progression_qc", "progression_qc/schemas"],
    install_requires=["cerberus", "pyyaml-include", "werkzeug"],
    classifiers=['Programming Language :: Python :: 3'],
)
