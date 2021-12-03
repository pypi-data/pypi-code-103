from django.contrib import admin
from django.db import models
from django import forms


class CodesInliner(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput()}
    }
    extra = 0
