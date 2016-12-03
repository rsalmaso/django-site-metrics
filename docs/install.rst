.. _install:

==============================
Installing django-site-metrics
==============================

You can install django-site-metrics from the following;

Via tar.gz / zip archive
========================

You can download the latest version in a archive created directly from the git repository via the following links:

    * tar.gz: https://github.com/rsalmaso/django-site-metrics/tarball/master
    * zip: https://github.com/rsalmaso/django-site-metrics/zipball/master

Once you have downloaded and extracted django-site-metrics, you can use the following command to install.

.. code-block:: bash

    $ python setup.py install

Via mercurial repository
========================

Mercurial is one of the best ways to download django-site-metrics, it allows you to easily pull the latest version, just by typing ``hg pull -u`` within the django-site-metrics directory. To download mercurial or how to use it. See: https://www.mercurial-scm.org/ .

You can use the following command to clone the hg repository:

.. code-block:: bash

    $ hg clone https://bitbucket.org/rsalmaso/django-site-metrics
    $ ln -s django-site-metrics/metrics <PYTHONPATH>

.. note:

    In the last command you will need to change <PYTHONPATH> to a path in your PYTHONPATH, a path which Python has recognized to have python modules within.

Via git repository
==================

Otherwise you can use Git to download django-site-metrics, as hg just type ``git fetch && git merge`` within the django-site-metrics directory. To download git or how to use it. See: https://git-scm.com/ .

You can use the following command to clone the git repository:

.. code-block:: bash

    $ git clone git://github.com/rsalmaso/django-site-metrics.git
    $ ln -s django-site-metrics/metrics <PYTHONPATH>

.. note:

    In the last command you will need to change <PYTHONPATH> to a path in your PYTHONPATH, a path which Python has recognized to have python modules within.

Using a package-management tool
===============================

This is one of the easiest ways to install django-site-metrics. There are two different package-management tools which you could use:

pip
---

pip is one of the more popular package-management systems for python. You can find documentation, and how to install `pip itself here`_.  Once you have pip installed and running, simply type:

.. code-block:: bash

    $ pip install django-site-metrics

easy_install
------------

Another option is to use easy_install, first you need to install easy_install. You can find documentation and how to install `easy_install here`_. Once you have easy_install up and running, just type:

.. code-block:: bash

    $ easy_install django-site-metrics

.. _pip itself here: http://pypi.python.org/pypi/pip/
.. _easy_install here: http://peak.telecommunity.com/DevCenter/EasyInstall
