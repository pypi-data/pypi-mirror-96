# dtn-tvg-util

A Python module providing functions for the representation of DTNs based on time-varying network graphs. Supports Python 2.7 and Python 3.4+.

## Requirements

* Python 2.7 or 3.4+
* a build toolchain for your platform plus the `python-dev` package to install the Python dependencies
* to place Ring Road ground stations, `libgeos-dev` and `libgdal-dev`

## Getting Started

For just using this module, install it via `pip`:

```
pip install dtn-tvg-util
```

For the development setup, you should first create a virtual environment and install with `pip install -e`

```
python3 -m venv --without-pip .venv
curl -sS https://bootstrap.pypa.io/get-pip.py | .venv/bin/python
source .venv/bin/activate
pip install -e .
```

Some example tools can be found in `tvgutil.tools`. These scripts allow to generate and convert time-varying graph representations of Ring Road [1] scenarios.

For using the Ring Road scenario generators, you have to install some further dependencies:

```
pip install "dtn-tvg-util[ring_road]"
# OR
pip install -e ".[ring_road]"
```

For ground station placement (via `tvgutil/tools/create_gs_list.py`), also install the `gs_placement` extras by adding `[ring_road,gs_placement]` to the `pip install` command.

## Testing

Unit tests for the core functionality are provided in `test/`. They are based on the Python `unittest` package. Use a test runner of your choice to execute them, e.g. `pytest` or `nose`.

```
pip install nose
python -m nose test
```

## License

This code is licensed under the MIT license. See [LICENSE](LICENSE) for details.

## References

[1] Ring Road Networks (RRN) are Disruption-tolerant Networks (DTN) for communication, based on the deployment of low-cost LEO satellites. For more information, see the following paper: *S. C. Burleigh and E. J. Birrane, “Toward a Communications Satellite Network for Humanitarian Relief,” in International Conference on Wireless Technologies for Humanitarian Relief, Amritapuri, India, 2011.*
