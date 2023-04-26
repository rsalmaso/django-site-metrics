# Changelog for django-site-metrics

## dev

* Drop support for Django < 3.2.
* Fixes middleware crash on invalid IP addresses in ``REMOTE_ADDR``.
* Adds warning logging to middleware on invalid IP addresses in
  ``REMOTE_ADDR``.
* Restore `Request.is_ajax`
* Adds [htmx](https://htmx.org/) support to the ``REQUEST_IGNORE_AJAX``
  setting.
* Don't ignore [boosted htmx requests](https://htmx.org/attributes/hx-boost/)
  with ``REQUEST_IGNORE_AJAX``.
* Fix `format_html` call in `Request` admin
* Fix `Request.query_string` initialization from request.GET to preserve list parameters
* Fixed handling naive datetimes
* Allow `Request` `query_string` and `headers` fields to be blank (to allow `{}`)
* Breaking: rename `Request.query_string` to `Request.query_params`
* Remove old (pre-squash) migrations
* Set `Request.ip` as null by default
* Add `METRICS_REQUEST_PIPELINE` setting to customize a `Request` build from an
  `HttpRequest/HttpResponse` (as called from
  `metrics.middleware.RequestMiddleware.process_response`)
* Breaking: `LOG_IP`, `ANONYMOUS_IP`, and `LOG_USER` settings and custom
  `Request.save()` method are removed.
  Use the pipeline for better control over recorder data from http request.

## 0.1.3

* Fixes handling naive datetimes in the admin's requests overview.
* Fixed url() deprecation warnings for Django >= 3.1.
* Add support for django >= 3.1 native JSONField
* Update isort and flake8 rules, reformat code with recent black (21.5b) and update code style.
* Remove deprecated django.utils.http.quote import
* Switch Request.id to BigAutoField
* Support for Python 3.6, 3.7, 3.8, 3.9.
* Support for Django >= 2.2.
