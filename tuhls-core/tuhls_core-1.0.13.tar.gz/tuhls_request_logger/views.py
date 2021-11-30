from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from tuhls_core.utils import AuthenticatedHttpRequest

from .models import Request


@login_required()
def logs(request: AuthenticatedHttpRequest):
    logs = Request.objects.filter(user=request.user.gid).order_by("-created_at")

    return render(
        request,
        "dashboard/logs.html",
        {"logs": logs},
    )
