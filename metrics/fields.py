from django import forms
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _


class StringField(models.TextField):
    description = _("String")


class URLField(StringField):
    default_validators = [validators.URLValidator()]
    description = _("URL")

    def formfield(self, **kwargs):
        defaults = {"form_class": forms.URLField}
        defaults.update(kwargs)
        return models.Field.formfield(self, **defaults)
