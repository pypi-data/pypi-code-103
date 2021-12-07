from django.db.models import QuerySet
from django.core.exceptions import ImproperlyConfigured
from django.http.response import Http404
from django.utils.translation import gettext as _

from django_generic_json_views.base import JsonContextMixin, JsonResponseMixin, JsonView


class JsonMultipleObjectMixin(JsonContextMixin):
    allow_empty = True
    queryset = None
    model = None
    context_object_name = None
    ordering = None

    def get_queryset(self):
        if self.queryset is not None:
            queryset = self.queryset

            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            ) 

        ordering = self.get_ordering()

        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)

            queryset.order_by(*ordering)

        return queryset

    def get_ordering(self):
        return self.ordering

    def get_allow_empty(self):
        return self.allow_empty

    def get_context_object_name(self, object_list):
        if self.context_object_name:
            return self.context_object_name
        elif hasattr(object_list, 'model'):
            return '%s_list' % object_list.model._meta.model_name
        else:
            return None

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        context_object_name = self.get_context_object_name(queryset)
        context = {'object_list': queryset}

        if context_object_name is not None:
            context[context_object_name] = queryset

        context.update(kwargs)

        return super().get_context_data(**context)


class JsonBaseListView(JsonMultipleObjectMixin, JsonView):
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            if not self.object_list:
                raise Http404(
                    _('Empty list and "%(class_name)s".allow_empty is False.')
                    % {'class_name': self.__class__.__name__}
                )
        
        context = self.get_context_data()

        return self.render_to_json_response(context)


class JsonListView(JsonResponseMixin, JsonBaseListView):
    """
    A view for getting multiple objects, with a json response.
    """
