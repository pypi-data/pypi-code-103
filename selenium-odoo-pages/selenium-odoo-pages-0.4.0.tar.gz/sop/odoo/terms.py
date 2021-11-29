"""Basic mapping in order to manage application terms
with multi language support

Before using other language you must set
"""
import os

TERMS = {
    "fr": {
        "Create and Edit...": "Créer et modifier...",
        "Create Invoice": "Créer une facture",
        "Confirm": "Confirmer",
        "Sales": "Ventes",
    },
}


def get_term(label):
    language = os.environ.get("SELENIUM_ODOO_PAGE_LANGUAGE", "en")
    if language == "en":
        return label
    return TERMS[language][label]
