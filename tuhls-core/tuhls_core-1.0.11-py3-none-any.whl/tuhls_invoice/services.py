from .models import Invoice
from .pdf import create


def invoice_to_pdf(invoice: Invoice):
    return create(
        {
            "to": {
                "name": invoice.name,
                "company": invoice.company,
                "address1": invoice.address1,
                "address2": invoice.address2,
                "zip_code": invoice.zip_code,
                "state": invoice.state,
                "city": invoice.city,
                "country": invoice.country,
            },
            "type": invoice.get_type_name(),
            "creator": "Bilcom GesmbH.",
            "date": invoice.created_at.strftime("%Y-%m-%d %H:%M"),
            "currency_symbol": "$",
            "footer": [
                "Bankverbindung: Erste Bank, IBAN: AT96 2011 1822 6402 1500, BIC GIBAATWWXXX",
                "Bilcom GesmbH. Universitätstraße 4/4, 1090 Wien, office@bilcom.at, +43 1 641 99 85",
            ],
            "items": [
                {
                    "name": x.name,
                    "description": x.description,
                    "amount": x.amount,
                }
                for x in invoice.details.all()
            ],
        }
    )
