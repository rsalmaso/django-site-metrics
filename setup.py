#!/usr/bin/env python
import metrics
from setuptools import setup

setup(
    name='django-site-metrics',
    version=metrics.__version__,
    description=open('docs/description.rst').read(),
    long_description=open('docs/long_description.rst').read(),
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
        'django >= 1.4',
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
    ]
)
