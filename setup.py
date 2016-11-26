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
    name='django-site-metrics',
    version=metrics.__version__,
    description=read('docs/description.rst'),
    long_description=read('docs/long_description.rst'),
    author=metrics.__author__,
    author_email=metrics.__email__,
    url='https://bitbucket.org/rsalmaso/django-site-metrics/',
    download_url='https://bitbucket.org/rsalmaso/django-site-metrics/get/{0}.tar.gz'.format(metrics.__version__),
    packages=[
        'metrics',
        'metrics.migrations',
        'metrics.templatetags',
        'metrics.management',
        'metrics.management.commands',
    ],
    package_data={'metrics': [
        'templates/admin/metrics/*.html',
        'templates/admin/metrics/metrics/*.html',
        'templates/metrics/plugins/*.html',
        'static/metrics/js/*.js',
        'locale/*/LC_MESSAGES/*.*',
    ]},
    install_requires=[
        'django >= 1.8',
        'python-dateutil',
    ],
    license=metrics.__licence__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
