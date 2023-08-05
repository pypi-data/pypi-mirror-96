# Next-generation NDS oscilloscope

`ndscope` is a tool for viewing time series data from the LIGO Network
Data Services (NDS).  Based on
[nds2-client](https://git.ligo.org/nds/nds2-client) and the
high-performance [pyqtgraph](http://pyqtgraph.org/) plotting library,
`ndscope` is a able to plot both online and offline data for many
channels simultaneously with intuitive mouse pan/zoom support.

![ndscope](ndscope.png)

### Features:

* online mode for raw and trend data
* mouse pan and zoom, with background auto-fetch of new data
* automatic transition to second/minute trend data at appropriate zoom levels
* triggering, for true oscilloscope behavior
* cursors and crosshair in both time and Y axes
* save layout templates in easy-to-use YAML format
* load templates from various legacy formats, including StripTool .stp, dataviewer .xml, and .txt
* enhanced "StripTool mode" with auto-backfill of past data
* NDS2 and NDS1 protocols supports

Left mouse click+drag for pan, and right mouse click+drag for zoom
(left/right for in/out in time, and up/down for in/out in Y).
Click+drag on axis to retrict pan/zoom to only that dimension.

## Issues

Please report issues to the [gitlab issue tracker](https://git.ligo.org/cds/ndscope/issues).

## Requirements

Package requirements for `ndscope` (Debian package names):

* [python3-pyqtgraph](http://pyqtgraph.org/)
* [python3-nds2-client](https://git.ligo.org/nds/nds2-client)
* python3-pyqt5
* [python3-gpstime](https://git.ligo.org/cds/gpstime)
* python3-dateutil
* python3-yaml
* python3-cairosvg
* python3-h5py

The following packages are used for development purposes:

* pyqt5-dev-tools
* qt5-designer
* python3-setuptools_scm
* pytest3-pytest

Pre-built binary packages are available via
[pip](https://pypi.org/projects/ndscope) and
[conda](https://anaconda.org/conda-forge/ndscope) and for the various
[IGWN supported operating
systems](https://computing.docs.ligo.org/guide/software/installation/).
