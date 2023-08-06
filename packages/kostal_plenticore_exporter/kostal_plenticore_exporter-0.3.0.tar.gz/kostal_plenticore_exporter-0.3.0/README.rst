=====================================
Kostal Plenticore Prometheus Exporter
=====================================

This is a Prometheus exporter for the `Kostal Plenticore <https://www.kostal-solar-electric.com/en-gb/products>`_ series of inverters.
It exports the metrics exposed by the inverter in `Prometheus <https://prometheus.io>`_ format.
This way it can be ingested into Prometheus and used for `Grafana <https://grafana.com/>`_ dashboards or to trigger notifications in case of failure events.

Usage
=====

Run the ``kostal-plenticore-exporter`` passing it the IP address of the inverter and the password of the operator user.
As command line arguments can be seen by other users on the system, the password should be passed via environment
variable::

    PASSWORD="my super secret" kostal-plenticore-exporter 192.168.1.3

The metrics will be default be exposed at `<http://localhost:9876/>`_.
See ``kostal-plenticore-exporter --help`` for all metrics available.

Alternatively, you can also invoke the Python module: ``python3 -m kostal_plenticore_exporter --help``.

License
=======

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see `<http://www.gnu.org/licenses/>`_.
