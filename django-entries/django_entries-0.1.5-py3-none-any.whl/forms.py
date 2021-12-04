from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from markdownify import markdownify as md

from .models import Entry


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ("title", "excerpt", "content")

    def __init__(self, *args, **kwargs):
        text = kwargs.pop("button_text", "Submit")
        submit_url = kwargs.pop("submit_url", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = submit_url
        self.helper.layout = Layout(
            Field("title"),
            Field("excerpt"),
            Field("content"),
            Submit(text, text),
        )

    def clean_content(self):
        """Removed bad tags, e.g. <script>"""
        content = self.cleaned_data["content"]
        cleaned = md(content, strip=["script"])
        return cleaned
