# download-tiles

[![PyPI](https://img.shields.io/pypi/v/download-tiles.svg)](https://pypi.org/project/download-tiles/)
[![Changelog](https://img.shields.io/github/v/release/simonw/download-tiles?include_prereleases&label=changelog)](https://github.com/simonw/download-tiles/releases)
[![Tests](https://github.com/simonw/download-tiles/workflows/Test/badge.svg)](https://github.com/simonw/download-tiles/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/download-tiles/blob/master/LICENSE)

Download map tiles and store them in an MBTiles database

## Installation

Install this tool using `pip`:

    $ pip install download-tiles

## Usage

This tool downloads tiles from a specified [TMS (Tile Map Server)](https://wiki.openstreetmap.org/wiki/TMS) server for a specified bounding box and range of zoom levels and stores those tiles in a MBTiles SQLite database. It is a command-line wrapper around the [Landez](https://github.com/makinacorpus/landez) Python libary.

**Please use this tool responsibly**. Consult the usage policies of the tile servers you are interacting with, for example the [OpenStreetMap Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/).

Running the following will download zoom levels 0-3 of OpenStreetMap, 85 tiles total, and store them in a SQLite database called `world.mbtiles`:

    download-tiles world.mbtiles

You can customize which tile and zoom levels are downloaded using command options:

`--zoom-levels` or `-z`

The different zoom levels to download. Specify a single number, e.g. `15`, or a range of numbers e.g. `0-4`. Be careful with this setting as you can easily go over the limits requested by the underlying tile server.

`--bbox` or `-b`

The bounding box to fetch. Should be specified as `min-lon,min-lat,max-lon,max-lat`. You can use [bboxfinder.com](http://bboxfinder.com/) to find these for different areas.

`--city` or `--country`

These options can be used instead of `--bbox`. The city or country specified will be looked up using the [Nominatum API](https://nominatim.org/release-docs/latest/api/Search/) and used to derive a bounding box.

`--show-bbox`

Use these to output the bounding box that was retrieved for the `--city` or `--country` without retrieving any tiles.

`--attribution`

Attribution string to bake into the `metadata` table. This will default to `© OpenStreetMap contributors` unless you use `--tiles-url` to specify an alternative tile server, in which case you should specify a custom attribution string.

`--tiles-url`

The tile server URL to use. This should include `{z}` and `{x}` and `{y}` specifiers, and can optionally include `{s}` for subdomains.

The default URL used here is for OpenStreetMap, `http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`

`--tiles-subdomains`

A comma-separated list of subdomains to use for the `{s}` parameter.

`--verbose`

Use this option to turn on verbose logging.

`--cache-dir`

Provide a directory to cache downloaded tiles between runs. This can be useful if you are worried you might not have used the correct options for the bounding box or zoom levels.

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd download-tiles
    python -mvenv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and tests:

    pip install -e '.[test]'

To run the tests:

    pytest
