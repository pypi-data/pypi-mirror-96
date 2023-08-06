=========
Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.


0.3.0 - 2021-02-24
==================

Added
-----

* Add metrics `kostal_plenticore_string_voltage_volts` and `kostal_plenticore_string_current_amperes` for PV string voltage and current.


0.2.0 - 2020-12-21
==================

Added
-----

* Add metric `kostal_plenticore_battery_configured_minimum_charge_percent` exporting the configured minimum state-of-charge target.
* The exporter can also be invoked as a Python module: ``python3 -m kostal_plenticore_exporter --help``.

Fixed
-----

* Compatibility with Prometheus Client 0.7.

0.1.1 - 2020-12-21
==================

Fixed
-----

* Include changelog and license in source distribution.
* Loosen overly tight version dependencies to Click, Prometheus Client, and Pytest.


0.1.0 - 2020-12-20
==================

Added
-----

* Expose basic metrics of the Kostal Plenticore inverter.
