from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import redirect, render

from tuhls_core.utils import AuthenticatedHttpRequest

from .models import Invoice
from .pdf import create
from .services import invoice_to_pdf


@login_required()
def invoice_overview(request: AuthenticatedHttpRequest):
    invoices_due = Invoice.objects.filter(
        user=request.user.gid, type=Invoice.Types.INVOICE, is_paid=False
    ).order_by("-created_at")
    invoices_paid = Invoice.objects.filter(
        user=request.user.gid, type=Invoice.Types.INVOICE, is_paid=True
    ).order_by("-created_at")
    return render(
        request,
        "dashboard/invoice.html",
        {"invoices_due": invoices_due, "invoices_paid": invoices_paid},
    )


def invoice_pdf(request: AuthenticatedHttpRequest, invoice_gid):
    try:
        invoice = Invoice.objects.get(gid=invoice_gid)
    except Invoice.DoesNotExist:
        return redirect("invoice_overview")

    if str(invoice.user) != str(request.user.gid):
        return redirect("invoice_overview")

    return FileResponse(
        invoice_to_pdf(invoice),
        as_attachment=False,
        filename=invoice.get_file_name(),
        content_type="application/pdf",
    )


def receipt_pdf(request: AuthenticatedHttpRequest, invoice_gid):
    try:
        invoice = Invoice.objects.get(gid=invoice_gid)
    except Invoice.DoesNotExist:
        return redirect("invoice_overview")

    if str(invoice.user) != str(request.user.gid):
        return redirect("invoice_overview")

    if not invoice.is_paid:
        return redirect("invoice_overview")

    b = create(
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
            "type": "Receipt",
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
    return FileResponse(
        b,
        as_attachment=False,
        filename=invoice.get_file_name(),
        content_type="application/pdf",
    )
