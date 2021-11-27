from django.http import Http404
from django.shortcuts import redirect
from django.views import generic
from django.views.generic.detail import SingleObjectMixin

from .models import Payment
from .settings import payment_settings


class DebugOnlyMixin(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if not payment_settings.DEBUG_MODE:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class DebugPaymentView(DebugOnlyMixin, generic.DetailView):
    queryset = Payment.objects.filter(status=Payment.StatusType.PENDING)
    template_name = "django_pay2/debug_payment.html"

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class AcceptDebugPaymentView(DebugOnlyMixin, SingleObjectMixin, generic.View):
    queryset = Payment.objects.filter(status=Payment.StatusType.PENDING)

    def post(self, request, *args, **kwargs):
        payment = self.get_object()
        payment.accept()
        return redirect("django_pay2:success")


class RejectDebugPaymentView(DebugOnlyMixin, SingleObjectMixin, generic.View):
    queryset = Payment.objects.filter(status=Payment.StatusType.PENDING)

    def post(self, request, *args, **kwargs):
        payment = self.get_object()
        payment.reject()
        return redirect("django_pay2:fail")


class SuccessPaymentView(generic.TemplateView):
    def get_template_names(self):
        return [payment_settings.TEMPLATES.success]


class RejectedPaymentView(generic.TemplateView):
    def get_template_names(self):
        return [payment_settings.TEMPLATES.rejected]
