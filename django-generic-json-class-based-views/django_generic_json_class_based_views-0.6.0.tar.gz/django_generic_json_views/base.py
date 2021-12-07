from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import JsonResponse
from django.views.generic.base import View
from django.db.models import Model
from django.db.models.query import QuerySet


class JsonContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        return kwargs


class JsonView(View):
    def options(self, request, *args, **kwargs):
        return JsonResponse(data={'Allow': ', '.join(self._allowed_methods())})


class JsonResponseMixin:
    encoder = DjangoJSONEncoder
    safe = True
    content_type = 'application/json'
    response_class = JsonResponse
    json_dumps_params = None

    def purge_context(self, context):
        if 'view' in context:
            del context['view']

        if 'form' in context:
            del context['form']

        return context

    def render_to_json_response(self, context, **response_kwargs):
        response_kwargs.setdefault('content_type', self.content_type)
        context = self.purge_context(context)

        return self.response_class(
            data={key: (serialize('json', [value]) if isinstance(value, Model) else serialize('json', value) if isinstance(value, QuerySet) else value) for key, value in context.items()},
            encoder=self.encoder,
            safe=self.safe,
            json_dumps_params=self.json_dumps_params,
            **response_kwargs
        )


class JsonDataView(JsonResponseMixin, JsonContextMixin, JsonView):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        return self.render_to_json_response(context)

