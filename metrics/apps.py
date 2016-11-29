from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class MetricsConfig(AppConfig):
    name = "metrics"
    verbose_name = _("Metrics")
