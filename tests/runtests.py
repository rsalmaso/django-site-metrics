#!/usr/bin/env python3

# Copyright (C) 2007-2021, Raffaele Salmaso <raffaele@salmaso.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import atexit
import copy
import os
from pathlib import Path
import shutil
import sys
import tempfile

import django
from django.apps import apps
from django.conf import settings
from django.db import connections
from django.test import TestCase, TransactionTestCase
from django.test.runner import default_test_processes
from django.test.utils import get_runner
from django.utils.log import DEFAULT_LOGGING

import metrics

PROJECT_DIR = Path(__file__).resolve().parent
RUNTESTS_DIR = PROJECT_DIR
TEMPLATE_DIR = RUNTESTS_DIR / "templates"
TMPDIR = tempfile.mkdtemp(prefix="metrics_")
# Set the TMPDIR environment variable in addition to tempfile.tempdir
# so that children processes inherit it.
tempfile.tempdir = os.environ["TMPDIR"] = TMPDIR

# Removing the temporary TMPDIR.
atexit.register(shutil.rmtree, TMPDIR)


SUBDIRS_TO_SKIP = [
    # "django",
]


ALWAYS_INSTALLED_APPS = [
    "django.contrib.auth.apps.AuthConfig",
    "django.contrib.contenttypes.apps.ContentTypesConfig",
    "django.contrib.sessions.apps.SessionsConfig",
    "django.contrib.messages.apps.MessagesConfig",
    "django.contrib.sites.apps.SitesConfig",
    "django.contrib.staticfiles.apps.StaticFilesConfig",
    "django.contrib.admin.apps.AdminConfig",
    "metrics.apps.MetricsConfig",
]


ALWAYS_MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]


def get_installed():
    return [app_config.name for app_config in apps.get_app_configs()]


def teardown(state):
    # Restore the old settings.
    for key, value in state.items():
        setattr(settings, key, value)
    # Discard the multiprocessing.util finalizer that tries to remove a
    # temporary directory that's already removed by this script's
    # atexit.register(shutil.rmtree, TMPDIR) handler. Prevents
    # FileNotFoundError at the end of a test run on Python 3.6+ (#27890).
    from multiprocessing.util import _finalizer_registry

    _finalizer_registry.pop((-100, 0), None)


def get_test_modules():
    modules = []
    discovery_paths = [
        (None, str(RUNTESTS_DIR)),
    ]

    for modpath, dirpath in discovery_paths:
        for f in os.listdir(dirpath):
            if (
                "." in f
                or os.path.basename(f) in SUBDIRS_TO_SKIP
                or os.path.isfile(f)
                or not os.path.exists(os.path.join(dirpath, f, "__init__.py"))
            ):
                continue
            modules.append((modpath, f))
    return modules


def setup(verbosity, test_labels, parallel):
    if verbosity >= 1:
        msg = "Testing against django-site-metrics installed in '%s'" % os.path.dirname(metrics.__file__)
        max_parallel = default_test_processes() if parallel == 0 else parallel
        if max_parallel > 1:
            msg += " with up to %d processes" % max_parallel
        print(msg)

    # Force declaring available_apps in TransactionTestCase for faster tests.
    def no_available_apps(self):
        raise Exception("Please define available_apps in TransactionTestCase and its subclasses.")

    TransactionTestCase.available_apps = property(no_available_apps)
    TestCase.available_apps = None

    state = {
        "INSTALLED_APPS": settings.INSTALLED_APPS,
        "ROOT_URLCONF": getattr(settings, "ROOT_URLCONF", ""),
        "TEMPLATES": settings.TEMPLATES,
        "LANGUAGE_CODE": settings.LANGUAGE_CODE,
        "STATIC_URL": settings.STATIC_URL,
        "STATIC_ROOT": settings.STATIC_ROOT,
        "MIDDLEWARE": settings.MIDDLEWARE,
    }

    # Redirect some settings for the duration of these tests.
    settings.INSTALLED_APPS = ALWAYS_INSTALLED_APPS
    settings.ROOT_URLCONF = "urls"
    settings.STATIC_URL = "/static/"
    settings.STATIC_ROOT = os.path.join(TMPDIR, "static")
    settings.TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [TEMPLATE_DIR],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]
    settings.LANGUAGE_CODE = "en"
    settings.SITE_ID = 1
    settings.MIDDLEWARE = ALWAYS_MIDDLEWARE
    settings.MIGRATION_MODULES = {
        # This lets us skip creating migrations for the test models as many of
        # them depend on one of the following contrib applications.
        "auth": None,
        "contenttypes": None,
        "sessions": None,
    }
    log_config = copy.deepcopy(DEFAULT_LOGGING)
    # Filter out non-error logging so we don't have to capture it in lots of
    # tests.
    log_config["loggers"]["django"]["level"] = "ERROR"
    settings.LOGGING = log_config
    settings.SILENCED_SYSTEM_CHECKS = [
        "fields.W342",  # ForeignKey(unique=True) -> OneToOneField
    ]

    # Load all the ALWAYS_INSTALLED_APPS.
    django.setup()

    # Load all the test model apps.
    test_modules = get_test_modules()

    # Reduce given test labels to just the app module path
    test_labels_set = set()
    for label in test_labels:
        bits = label.split(".")[:1]
        test_labels_set.add(".".join(bits))

    installed_app_names = set(get_installed())
    for modpath, module_name in test_modules:
        if modpath:
            module_label = ".".join([modpath, module_name])
        else:
            module_label = module_name
        # if the module (or an ancestor) was named on the command line, or
        # no modules were named (i.e., run all), import
        # this module and add it to INSTALLED_APPS.
        if not test_labels:
            module_found_in_labels = True
        else:
            module_found_in_labels = any(
                # exact match or ancestor match
                module_label == label or module_label.startswith(label + ".")
                for label in test_labels_set
            )

        if module_found_in_labels and module_label not in installed_app_names:
            if verbosity >= 2:
                print("Importing application %s" % module_name)
            settings.INSTALLED_APPS.append(module_label)

    apps.set_installed_apps(settings.INSTALLED_APPS)

    return state


def actual_test_processes(parallel):
    if parallel == 0:
        # This doesn't work before django.setup() on some databases.
        if all(conn.features.can_clone_databases for conn in connections.all()):
            return default_test_processes()
        else:
            return 1
    else:
        return parallel


def django_tests(
    verbosity,
    interactive,
    failfast,
    keepdb,
    reverse,
    test_labels,
    debug_sql,
    parallel,
    tags,
    exclude_tags,
):  # noqa: E501
    state = setup(verbosity, test_labels, parallel)
    extra_tests = []

    # Run the test suite, including the extra validation tests.
    if not hasattr(settings, "TEST_RUNNER"):
        settings.TEST_RUNNER = "django.test.runner.DiscoverRunner"
    TestRunner = get_runner(settings)

    test_runner = TestRunner(
        verbosity=verbosity,
        interactive=interactive,
        failfast=failfast,
        keepdb=keepdb,
        reverse=reverse,
        debug_sql=debug_sql,
        parallel=actual_test_processes(parallel),
        tags=tags,
        exclude_tags=exclude_tags,
    )
    failures = test_runner.run_tests(test_labels or get_installed(), extra_tests=extra_tests)
    teardown(state)
    return failures


if __name__ == "__main__":
    import argparse

    usage = "%prog [options] [model model model ...]"

    parser = argparse.ArgumentParser(description="Run the Fluo test suite.")
    parser.add_argument(
        "modules",
        nargs="*",
        metavar="module",
        help='Optional path(s) to test modules; e.g. "i18n" or "i18n.tests.TranslationTests.test_lazy_objects".',
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        default=1,
        type=int,
        choices=[0, 1, 2, 3],
        help="Verbosity level; 0=minimal output, 1=normal output, 2=all output",
    )
    parser.add_argument(
        "--noinput",
        action="store_false",
        dest="interactive",
        help="Tells Django to NOT prompt the user for input of any kind.",
    )
    parser.add_argument(
        "--failfast",
        action="store_true",
        dest="failfast",
        help="Tells Django to stop running the test suite after first failed test.",
    )
    parser.add_argument(
        "-k",
        "--keepdb",
        action="store_true",
        dest="keepdb",
        help="Tells Django to preserve the test database between runs.",
    )
    parser.add_argument(
        "--settings",
        help=(
            'Python path to settings module, e.g. "myproject.settings". If '
            "this isn't provided, either the DJANGO_SETTINGS_MODULE "
            'environment variable or "test_sqlite" will be used.'
        ),
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        help=(
            "Sort test suites and test cases in opposite order to debug "
            "test side effects not apparent with normal execution lineup."
        ),
    )
    parser.add_argument(
        "--debug-sql",
        action="store_true",
        dest="debug_sql",
        help="Turn on the SQL query logger within tests.",
    )
    parser.add_argument(
        "--parallel",
        dest="parallel",
        nargs="?",
        default=1,
        type=int,
        const=default_test_processes(),
        metavar="N",
        help="Run tests using up to N parallel processes.",
    )
    parser.add_argument(
        "--tag",
        dest="tags",
        action="append",
        help="Run only tests with the specified tags. Can be used multiple times.",
    )
    parser.add_argument(
        "--exclude-tag",
        dest="exclude_tags",
        action="append",
        help="Do not run tests with the specified tag. Can be used multiple times.",
    )

    options = parser.parse_args()

    # Allow including a trailing slash on app_labels for tab completion convenience
    options.modules = [os.path.normpath(labels) for labels in options.modules]

    if options.settings:
        os.environ["DJANGO_SETTINGS_MODULE"] = options.settings
    else:
        if "DJANGO_SETTINGS_MODULE" not in os.environ:
            os.environ["DJANGO_SETTINGS_MODULE"] = "settings.sqlite"
        options.settings = os.environ["DJANGO_SETTINGS_MODULE"]

    failures = django_tests(
        options.verbosity,
        options.interactive,
        options.failfast,
        options.keepdb,
        options.reverse,
        options.modules,
        options.debug_sql,
        options.parallel,
        options.tags,
        options.exclude_tags,
    )
    if failures:
        sys.exit(1)
