from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http.response import Http404
from django.utils.translation import gettext as _

from django_generic_json_views.base import JsonView, JsonContextMixin, JsonResponseMixin


class JsonSingleObjectMixin(JsonContextMixin):
    model = None
    queryset = None
    slug_field = 'slug'
    context_object_name = None
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    query_pk_and_slug = False

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)

        if pk is not None:
            queryset = queryset.filter(pk=pk)

        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        if pk is None and slug is None:
            self.handle_error(
                'AttributeError', 
                'Generic json detail view %s must be called with either an object '
                'pk or a slug in the URLconf.' % self.__class__.__name__
            )

        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                _('No %(verbose_name)s found matching the query')
                % {'verbose_name': queryset.model._meta.verbose_name}
            )

        return obj

    def get_queryset(self):
        if self.queryset is None:
            if self.model:
                return self.model._default_manager.all()
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.model, %(cls)s.queryset, or override "
                    "%(cls)s.get_queryset()." % {
                        'cls': self.__class__.__name__
                    }
                )

        return self.queryset.all()

    def get_slug_field(self):
        return self.slug_field

    def get_context_object_name(self, obj):
        if self.context_object_name:
            return self.context_object_name
        elif isinstance(obj, models.Model):
            return obj._meta.model_name
        else:
            return None

    def get_context_data(self, **kwargs):
        context = {}

        if hasattr(self, 'object'):
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)

            if context_object_name:
                context[context_object_name] = self.object

        context.update(kwargs)

        return super().get_context_data(**context)


class JsonBaseDetailView(JsonSingleObjectMixin, JsonView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        return self.render_to_json_response(context)


class JsonDetailView(JsonResponseMixin, JsonBaseDetailView):
    """
    Return a detail json object of an object.
    """
