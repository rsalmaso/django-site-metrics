.. _settings:

========
Settings
========

``METRICS_IGNORE_AJAX``
=======================

Default: ``False``

If this is set to ``True``, then ajax requests will not be recorded. To
determine if a request was ajax, we use ``HttpRequest.is_ajax()``, see
Django documentation for more information.

``METRICS_IGNORE_IP``
=====================

Default: ``None``

Any requests from a IP Address in this list will not be recorded.

``METRICS_LOG_IP``
=====================

Default: ``True``

If set to False, ip addresses are replaced with METRICS_IP_DUMMY.

``METRICS_IP_DUMMY``
=====================

Default: ``1.1.1.1``

Used dummy address, if METRICS_LOG_IP is set to False.

``METRICS_ANONYMOUS_IP``
========================

Default: ``False``

If set to True, last octet of the ip is set to 1.

``METRICS_LOG_USER``
=====================

Default: ``True``

If set to False, user are not logged (set to None).

``METRICS_IGNORE_USERNAME``
===========================

Default: ``None``

Any requests from users in this list will not be recorded.

``METRICS_IGNORE_PATHS``
===========================

Default: ``None``

Any requests which match these paths will not be recorded. This setting should
be a tuple filled with regex paths.

Example:

.. code-block:: python

    METRICS_IGNORE_PATHS = (
        r'^admin/',
    )

``METRICS_IGNORE_USER_AGENTS``
==============================

Default: ``None``

Any request with a user agent that matches any pattern in this list will not be
recorded.

Example:

.. code-block:: python

    METRICS_IGNORE_USER_AGENTS = (
        r'^$',  # don't record requests with no user agent string set.
        r'Googlebot',
        r'Baiduspider',
    )

``METRICS_TRAFFIC_MODULES``
=================================

Default:

.. code-block:: python

    (
        'metrics.traffic.UniqueVisitor',
        'metrics.traffic.UniqueVisit',
        'metrics.traffic.Hit',
    )

These are all the items in the traffic graph and table on the overview page. If you wish to remove or add a item you can override this setting and set what you want to see. There are also many more options you can add from the following list;

- ``'metrics.traffic.Ajax'``: To show the amount of requests made from javascript.
- ``'metrics.traffic.NotAjax'``: To show the amount of requests that are NOT made from javascript.
- ``'metrics.traffic.Error'``: To show the amount of error's, this includes error 500 and page not found.
- ``'metrics.traffic.Error404'``: To show the amount of page not found.
- ``'metrics.traffic.Hit'``: To show the total amount of requests.
- ``'metrics.traffic.Search'``: To display requests from search engines.
- ``'metrics.traffic.Secure'``: To show the amount of requests over SSL.
- ``'metrics.traffic.Unsecure'``: To show the amount of requests NOT over SSL.
- ``'metrics.traffic.UniqueVisit'``: To show visits based from outsider referrals.
- ``'metrics.traffic.UniqueVisitor'``: To show the amount of requests made from unique visitors based upon IP address.
- ``'metrics.traffic.User'``: To show the amount of requests made from a valid user account.
- ``'metrics.traffic.UniqueUser'``: To show the amount of users.

``METRICS_PLUGINS``
===================

Default:

.. code-block:: python

    (
        'metrics.plugins.TrafficInformation',
        'metrics.plugins.LatestRequests',
        'metrics.plugins.TopPaths',
        'metrics.plugins.TopErrorPaths',
        'metrics.plugins.TopReferrers',
        'metrics.plugins.TopSearchPhrases',
        'metrics.plugins.TopBrowsers',
    )

These are all the plugins you can see on the overview page. If you wish to remove or add a plugin you can override this setting and set what you want to see. Here is a list of all the plugins and what they do;

- ``'metrics.plugins.TrafficInformation'``: This is a plugin to show a table of the traffic modules.
- ``'metrics.plugins.LatestRequests'``: The last 5 requests.
- ``'metrics.plugins.TopPaths'``: A list of all the paths (not including errors).
- ``'metrics.plugins.TopErrorPaths'``: A list of the paths which error, this can be useful for finding bugs.
- ``'metrics.plugins.TopReferrers'``: Shows a list of top referrals to your site.
- ``'metrics.plugins.TopSearchPhrases'``: Shows a list of all the search phrases used to find your site.
- ``'metrics.plugins.TopBrowsers'``: Shows a graph of the top browsers accessing your site.
- ``'metrics.plugins.ActiveUsers'``: Shows a list of active users in the last
  5 minutes. This may not be a good idea to use on a large website with lots of
  active users as it will generate a long list.

``METRICS_BASE_URL``
====================

Default: ``'http://%s' % Site.objects.get_current().domain``

This setting should only be set if you use SSL or do not use django.contrib.sites. This is the base url for detecting referral from within the same site.

``METRICS_ONLY_ERRORS``
=====================================

Default: ``False``

If this is set to True, django-site-metrics will ONLY store error returning request/responses. This can be useful to use django-site-metrics purely as a error detection system.

``METRICS_VALID_METHOD_NAMES``
==============================

Default: ('get', 'post', 'put', 'delete', 'head', 'options', 'trace')

Any request which is not in this tuple/list will not be recorded.
