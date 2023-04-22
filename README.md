django-site-metrics
===================

django-site-metrics is a statistics module for django. It stores requests in a database for admins to see, it can also be used to get statistics on who is online etc.

As well as a site statistics module, with the `active_users` template tag and manager method you can also use django-site-metrics to show who is online in a certain time.

    Request.objects.active_users(minutes=15)

To find the request overview page, please click on Requests inside the admin, then “Overview” on the top right, next to “add request”.

django-site-metrics is a "fork" of [django-request](https://github.com/django-request/django-request/), which focus only on postgresql support and is able to use a separate database.

Installation
------------

- Put `'metrics'` in your `INSTALLED_APPS` setting.
- Run the command `manage.py migrate`.
- Add `metrics.middleware.RequestMiddleware` to `MIDDLEWARE`. If you use `django.contrib.auth.middleware.AuthenticationMiddleware`, place the `RequestMiddleware` after it. If you use `django.contrib.flatpages.middleware.FlatpageFallbackMiddleware` place `metrics.middleware.RequestMiddleware` before it else flatpages will be marked as error pages in the admin panel.
- Add `REQUEST_BASE_URL` to your settings with the base URL of your site (e.g.
  `https://www.my.site/`). This is used to calculate unique visitors and top
  referrers. `REQUEST_BASE_URL` defaults to
  `'http://%s' % Site.objects.get_current().domain`.

Detailed documentation
----------------------

For a detailed documentation of django-site-metrics, or how to install django-site-metrics please see: [django-site-metrics](https://django-site-metrics.readthedocs.org/en/latest/) or the docs/ directory.
