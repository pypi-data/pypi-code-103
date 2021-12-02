from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

ITEMS_PER_PAGE = (
    (10, '10'),
    (25, '25'),
    (50, '50'),
    (100, '100'),
    (250, '250'),
    (500, '500'),
)

FILTER_BY = (
    ("run", 'Run Number'),
    ("experiment", 'Experiment Reference (RB)'),
    ("batch_runs", 'Batch Run'),
)

SHOW_OR_HIDE = (('default', 'Select action to apply to selected runs'), ('hide', 'Hide'))


class SearchOptionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    pagination = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'id': "select_per_page",
                'title': "The number of reduction jobs that should be shown per page",
                'name': "per_page",
                'onchange': 'update_page()'
            }),
        choices=ITEMS_PER_PAGE,
    )

    helper = FormHelper()
    helper.layout = Layout('pagination')


class RunsListOptionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    per_page = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'id': "pagination_select",
                'title': "The number of reduction jobs that should be shown per page",
                'name': "per_page"
            }),
        choices=ITEMS_PER_PAGE,
    )

    filter = forms.ChoiceField(
        widget=forms.Select(attrs={
            'id': "filter_select",
            'title': "Filter by Runs or by Experiments",
            'name': "filter"
        }),
        choices=FILTER_BY,
    )

    helper = FormHelper()
    helper.layout = Layout('filter', 'per_page')


class FailedQueueOptionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

    per_page = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'id': "select_per_page",
                'title': "The number of reduction jobs that should be shown per page",
                'name': "per_page",
                'onchange': "this.form.submit()",
            }),
        choices=ITEMS_PER_PAGE,
    )

    run_action = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'id': "runAction",
                'title': "Select action to apply to selected runs",
                'name': "runAction",
                'placeholder': "Placeholder",
            }),
        choices=SHOW_OR_HIDE,
    )
