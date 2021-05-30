# Changelog for django-site-metrics

## dev

* Drop support for Django < 3.2.

## 0.1.3

* Fixes handling naive datetimes in the admin's requests overview.
* Fixed url() deprecation warnings for Django >= 3.1.
* Add support for django >= 3.1 native JSONField
* Update isort and flake8 rules, reformat code with recent black (21.5b) and update code style.
* Remove deprecated django.utils.http.quote import
* Switch Request.id to BigAutoField
* Support for Python 3.6, 3.7, 3.8, 3.9.
* Support for Django >= 2.2.
