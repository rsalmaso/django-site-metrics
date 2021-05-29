# Copyright (C) 2016-2021, Raffaele Salmaso <raffaele@salmaso.org>
# Copyright (C) 2009-2021, Kyle Fuller and Mariusz Felisiak
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY KYLE FULLER ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL KYLE FULLER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from time import mktime

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Count
from django.utils.text import format_lazy
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from . import settings
from .utils import get_verbose_name


class Modules:
    """
    Set of :class:`.Module`.
    """

    def load(self):
        """
        Import and instanciate modules defined in
        ``settings.TRAFFIC_MODULES``.
        """
        from importlib import import_module

        self._modules = ()
        for module_path in settings.TRAFFIC_MODULES:
            try:
                dot = module_path.rindex(".")
            except ValueError:
                raise ImproperlyConfigured(f"{module_path} isn't a traffic module")
            traffic_module = module_path[:dot]
            traffic_classname = module_path[dot + 1 :]

            try:
                mod = import_module(traffic_module)
            except ImportError as err:
                raise ImproperlyConfigured(f"Error importing module {traffic_module}: '{err}'")

            try:
                traffic_class = getattr(mod, traffic_classname)
            except AttributeError:
                raise ImproperlyConfigured(
                    f"Traffic module '{traffic_module}' does not define a '{traffic_classname}' class"
                )

            self._modules += (traffic_class(),)

    @property
    def modules(self):
        """
        Get loaded modules, load them if isn"t already made.
        """
        if not hasattr(self, "_modules"):
            self.load()
        return self._modules

    def table(self, queries):
        """
        Get a list of modules" counters.
        """
        return tuple([(module.verbose_name_plural, [module.count(qs) for qs in queries]) for module in self.modules])

    def graph(self, days):
        """
        Get a list of modules" counters for all the given days.
        """
        return tuple(
            [
                {
                    "data": [(mktime(day.timetuple()) * 1000, module.count(qs)) for day, qs in days],
                    "label": str(gettext(module.verbose_name_plural)),
                }
                for module in self.modules
            ]
        )


modules = Modules()


class Module:
    """
    Base module class.
    """

    def __init__(self):
        self.module_name = self.__class__.__name__

        if not hasattr(self, "verbose_name"):
            self.verbose_name = get_verbose_name(self.module_name)

        if not hasattr(self, "verbose_name_plural"):
            self.verbose_name_plural = format_lazy("{}{}", self.verbose_name, "s")

    def count(self, qs):
        raise NotImplementedError("'count' isn't defined.")


class Error(Module):
    verbose_name = _("Error")
    verbose_name_plural = _("Errors")

    def count(self, qs):
        return qs.filter(status_code__gte=400).count()


class Error404(Module):
    verbose_name = _("Error 404")
    verbose_name_plural = _("Errors 404")

    def count(self, qs):
        return qs.filter(status_code=404).count()


class Hit(Module):
    verbose_name = _("Hit")
    verbose_name_plural = _("Hits")

    def count(self, qs):
        return qs.count()


class Search(Module):
    verbose_name = _("Search")
    verbose_name_plural = _("Searches")

    def count(self, qs):
        return qs.search().count()


class Secure(Module):
    verbose_name = _("Secure")
    verbose_name_plural = _("Secure")

    def count(self, qs):
        return qs.filter(is_secure=True).count()


class Unsecure(Module):
    verbose_name = _("Unsecure")
    verbose_name_plural = _("Unsecure")

    def count(self, qs):
        return qs.filter(is_secure=False).count()


class UniqueVisit(Module):
    verbose_name = _("Unique Visit")
    verbose_name_plural = _("Unique Visits")

    def count(self, qs):
        return qs.exclude(referer__startswith=settings.BASE_URL).count()


class UniqueVisitor(Module):
    verbose_name = _("Unique Visitor")
    verbose_name_plural = _("Unique Visitor")

    def count(self, qs):
        return qs.aggregate(Count("ip", distinct=True))["ip__count"]


class User(Module):
    verbose_name = _("User")
    verbose_name_plural = _("User")

    def count(self, qs):
        return qs.exclude(user__isnull=False).count()


class UniqueUser(Module):
    verbose_name = _("Unique User")
    verbose_name_plural = _("Unique User")

    def count(self, qs):
        return qs.aggregate(Count("user", distinct=True))["user__count"]
