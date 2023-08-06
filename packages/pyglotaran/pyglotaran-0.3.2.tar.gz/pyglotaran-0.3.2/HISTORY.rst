=======
History
=======

0.3.1 (2021-02-23)
------------------

* Added compatibility for numpy 1.20 and raised minimum required numpy version to 1.20 (#555)
* Fixed excessive memory consumption in result creation due to full SVD computation (#574)
* Added feature parameter history (#557)
* Moved setup logic to ``setup.cfg`` (#560)

0.3.0 (2021-02-11)
------------------

* Significant code refactor with small API changes to parameter relation specification (see docs)
* Replaced lmfit with scipy.optimize

0.2.0 (2020-12-02)
------------------

* Large refactor with significant improvements but also small API changes (see docs)
* Removed doas plugin

0.1.0 (2020-07-14)
------------------

* Package was renamed to ``pyglotaran`` on PyPi

0.0.8 (2018-08-07)
------------------

* Changed ``nan_policiy`` to ``omit``

0.0.7 (2018-08-07)
------------------

* Added support for multiple shapes per compartement.

0.0.6 (2018-08-07)
------------------

* First release on PyPI, support for Windows installs added.
* Pre-Alpha Development
