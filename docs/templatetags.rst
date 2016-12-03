.. _templatetags:

=============
Template tags
=============

active_users
============

This template tag will get a list of active users based on time,
if you do not supply a time to the tag, the default of 15 minutes
will be used. With the 'as' clause you can supply what context
variable you want the user list to be. There is also a 'in' clause,
after in you would specify a amount and a duration. Such as 2 hours,
of 10 minutes.

.. code-block:: html+django

    {% active_users in [amount] [duration] as [varname] %}
    {% active_users as [varname] %}
    {% active_users %}

Example usage:
--------------

.. code-block:: html+django

    {% load metrics_tag %}
    {% active_users in 10 minutes as user_list %}
    {% for user in user_list %}
        {{ user.username }}
    {% endfor %}
