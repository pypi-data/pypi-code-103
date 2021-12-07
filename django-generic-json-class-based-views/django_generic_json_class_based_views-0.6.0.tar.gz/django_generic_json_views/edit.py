from django.core.exceptions import ImproperlyConfigured
from django.forms import Form, models as model_forms

from django_generic_json_views.base import JsonContextMixin, JsonResponseMixin, JsonView
from django_generic_json_views.detail import JsonSingleObjectMixin, JsonBaseDetailView


class JsonFormMixin(JsonContextMixin):
    initial = {}
    form_class = None
    prefix = None

    def get_initial(self):
        return self.initial.copy()

    def get_prefix(self):
        return self.prefix

    def get_form_class(self):
        return self.form_class

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })

        return kwargs

    def form_valid(self, form):
        context = self.get_context_data(success=True)

        return self.render_to_json_response(context)

    def form_invalid(self, form):
        context = self.get_context_data(success=False)
        context.update({'errors': form.errors})

        return self.render_to_json_response(context)

    
class JsonModelFormMixin(JsonFormMixin, JsonSingleObjectMixin):
    fields = None

    def get_form_class(self):
        if self.fields is not None and self.form_class:
            raise ImproperlyConfigured(
                "Specifying both 'fields' and 'form_class' is not permitted." 
            )

        if self.form_class:
            return self.form_class
        else:
            if self.model is not None:
                model = self.model
            elif getattr(self, 'object', None) is not None:
                model = self.object.__class__
            else:
                model = self.get_queryset.model

        if self.fields is None:
            raise ImproperlyConfigured(
                'Using JsonModelFormMixin (base class of %s) without '
                "the 'fields' attribute is prohibited." 
                % self.__class__.__name__
            )

        return model_forms.modelform_factory(model, fields=self.fields)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        
        return kwargs

    def form_valid(self, form):
        self.object = form.save()

        return super().form_valid(form)


class JsonProcessFormView(JsonView):
    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def put(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class JsonBaseFormView(JsonFormMixin, JsonProcessFormView):
    """
    A base view for handling a json form.
    """


class JsonFormView(JsonResponseMixin, JsonBaseFormView):
    """
    A view for handling a json form.
    """


class JsonBaseCreateView(JsonModelFormMixin, JsonProcessFormView):
    def post(self, request, *args, **kwargs):
        self.object = None

        return super().post(request, *args, **kwargs)


class JsonCreateView(JsonResponseMixin, JsonBaseCreateView):
    """
    View for creating a new object, with a json response.
    """


class JsonBaseUpdateView(JsonModelFormMixin, JsonProcessFormView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        return super().post(request, *args, **kwargs)


class JsonUpdateView(JsonResponseMixin, JsonBaseUpdateView):
    """
    View for updating an object, with a json response.
    """


class JsonDeletionMixin:
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        context = self.get_context_data(success=True)

        return self.render_to_json_response(context)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class JsonBaseDeleteView(JsonDeletionMixin, JsonFormMixin, JsonBaseDetailView):
    form_class = Form

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object.delete()

        return super().form_valid(form)


class JsonDeleteView(JsonResponseMixin, JsonBaseDeleteView):
    """
    View for deleting an object, with a json response.
    """
