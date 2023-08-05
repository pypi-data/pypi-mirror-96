Unreleased changes
------------------


Version 0
---------
0.5.2 / 2021-02-23
~~~~~~~~~~~~~~~~~~
* Fixed ``runinfo``

0.5.1 / 2021-02-12
~~~~~~~~~~~~~~~~~~
* Forces IPv4 for the DB Webserver since IPv6 is not supported

0.5.0 / 2020-10-25
~~~~~~~~~~~~~~~~~~
* ``wtd``, ``runtable`` and ``runinfo`` command line utilities ported
  from km3pipe
* Lots of tiny improvements
* Automatic cookie deletion and retry when authentication fails (403)

0.4.2 / 2020-10-19
~~~~~~~~~~~~~~~~~~
* Helpers to convert det ID to OID and vice versa:
  ``tools.todetid`` and ``tools.todetoid``

0.4.1 / 2020-10-19
~~~~~~~~~~~~~~~~~~
* ``detx`` command line utility has been added

0.4.0 / 2020-10-18
~~~~~~~~~~~~~~~~~~
* ``tools.detx`` and ``tools.detx_for_run`` added
* ``tools.JSONDS`` added

0.3.0 / 2020-09-23
~~~~~~~~~~~~~~~~~~
* ``tools.StreamDS`` added
* the  ``streamds`` command line utility has been added
* the ``km3db`` command line utility has been added

0.2.0 / 2020-09-22
~~~~~~~~~~~~~~~~~~
* ``DBManager`` added

0.1.0 / 2020-09-21
~~~~~~~~~~~~~~~~~~
* Project generated using the cookiecutter template from
  https://git.km3net.de/templates/python-project
