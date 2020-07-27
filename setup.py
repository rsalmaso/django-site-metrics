#!/usr/bin/env python3
import io

import metrics
from setuptools import setup


def read(filename):
    data = ""
    with io.open(filename, "rU", encoding="utf-8") as fp:
        data = fp.read()
    return data


setup(
    name="django-site-metrics",
    version=metrics.__version__,
    description=read("docs/description.rst"),
    long_description=read("docs/long_description.rst"),
    long_description_content_type="text/x-rst",
    author=metrics.__author__,
    author_email=metrics.__email__,
    url="https://bitbucket.org/rsalmaso/django-site-metrics/",
    download_url="https://pypi.org/project/django-site-metrics/",
    packages=[
        "metrics",
        "metrics.migrations",
        "metrics.templatetags",
        "metrics.management",
        "metrics.management.commands",
    ],
    package_data={
        "metrics": [
            "templates/admin/metrics/*.html",
            "templates/admin/metrics/request/*.html",
            "templates/metrics/plugins/*.html",
            "static/metrics/js/*.js",
            "locale/*/LC_MESSAGES/*.*",
        ]
    },
    install_requires=["django >= 2.2", "python-dateutil"],
    license=metrics.__licence__,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
    ],
)
