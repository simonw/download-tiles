from attr import attrib
import click
import landez
import logging
import re
import requests
import sqlite3
import sys
import urllib


DEFAULT_TILES_URL = "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
DEFAULT_ATTRIBUTION = "© OpenStreetMap contributors"


def parse_zoom_levels(ctx, param, value):
    r = re.compile(r"^(\d+)(?:\-(\d+))?$")
    match = r.match(value)
    if match is None:
        raise click.BadParameter(
            "zoom-levels should be a single number or a 3-7 number range"
        )
    low, high = match.groups()
    low = int(low)
    if high is None:
        high = low
    else:
        high = int(high)
    if high < low:
        raise click.BadParameter("zoom-levels should be a low-high range")
    if high > 24:
        raise click.BadParameter("Maximum zoom level is 24")
    return low, high


def parse_bbox(ctx, param, value):
    float_re = r"(\-?(?:\d+)(?:\.\d+)?)"
    r = re.compile(r"^()\s*,\s*()\s*,\s*()\s*,\s*()$".replace("()", float_re))
    match = r.match(value)
    if match is None:
        raise click.BadParameter("bbox should be min-lon,min-lat,max-lon,max-lat")
    min_lon, min_lat, max_lon, max_lat = map(float, match.groups())
    return min_lon, min_lat, max_lon, max_lat


def validate_tiles_url(ctx, param, value):
    if not value:
        return value
    fragments = "{z}", "{x}", "{y}"
    for fragment in fragments:
        if fragment not in value:
            raise click.BadParameter(
                "tiles-url should include {}".format(", ".join(fragments))
            )
    return value


@click.command()
@click.argument(
    "mbtiles", type=click.Path(dir_okay=False, file_okay=True), required=False
)
@click.option(
    "-z",
    "--zoom-levels",
    default="0-3",
    callback=parse_zoom_levels,
    help="Zoom levels - defaults to 0-3",
)
@click.option(
    "-b",
    "--bbox",
    default="-180.0,-90.0,180.0,90.0",
    callback=parse_bbox,
    help="Bounding box of tiles to retrieve: min-lon,min-lat,max-lon,max-lat",
)
@click.option(
    "--tiles-url",
    help="Tile URL server to use. Defaults to OpenStreetMap.",
    callback=validate_tiles_url,
)
@click.option(
    "--tiles-subdomains",
    help="Subdomains to use in the {s} parameter.",
    default="a,b,c",
    callback=lambda ctx, param, value: [v.strip() for v in value.split(",")],
)
@click.option(
    "--country",
    help="Country to find bounding box for",
)
@click.option(
    "--city",
    help="City to find bounding box for",
)
@click.option(
    "--show-bbox",
    is_flag=True,
    help="Show country or city bounding box without downloading tiles",
)
@click.option(
    "--user-agent",
    default="github.com/simonw/download-tiles",
    help="User-Agent header to send with tile requests",
)
@click.option(
    "--attribution",
    help="Attribution to write to the metadata table",
)
@click.option("--verbose", is_flag=True, help="Verbose mode - show detailed logs")
@click.option("--cache-dir", help="Folder to cache tiles between runs")
@click.version_option()
def cli(
    mbtiles,
    zoom_levels,
    bbox,
    tiles_url,
    tiles_subdomains,
    country,
    city,
    show_bbox,
    user_agent,
    attribution,
    verbose,
    cache_dir,
):
    """
    Download map tiles and store them in an MBTiles database.

    Please use this tool responsibly, and respect the OpenStreetMap tile usage policy:
    https://operations.osmfoundation.org/policies/tiles/
    """
    # mbtiles is required unless show_bbox is used
    if not mbtiles and not show_bbox:
        raise click.BadParameter("mbtiles argument is required")
    if country:
        bbox = lookup_bbox("country", country)
    elif city:
        bbox = lookup_bbox("city", city)
    if show_bbox:
        click.echo(",".join(map(str, bbox)))
        return
    if not attribution and not tiles_url:
        attribution = DEFAULT_ATTRIBUTION
    if verbose:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    kwargs = dict(
        tiles_url=tiles_url or DEFAULT_TILES_URL,
        tiles_headers={"User-Agent": user_agent},
        tiles_subdomains=tiles_subdomains,
        filepath=str(mbtiles),
    )
    if cache_dir:
        kwargs["cache"] = True
        kwargs["tiles_dir"] = cache_dir
    else:
        kwargs["cache"] = False
    mb = landez.MBTilesBuilder(**kwargs)
    mb.add_coverage(
        bbox=bbox, zoomlevels=list(range(zoom_levels[0], zoom_levels[1] + 1))
    )
    mb.run()

    if attribution:
        db = sqlite3.connect(str(mbtiles))
        with db:
            db.execute(
                "insert into metadata (name, value) values (:name, :value)",
                {"name": "attribution", "value": attribution},
            )


def lookup_bbox(parameter, value):
    url = "https://nominatim.openstreetmap.org/?{}={}&format=json&limit=1".format(
        parameter, urllib.parse.quote_plus(value)
    )
    results = requests.get(url).json()
    boundingbox = results[0]["boundingbox"]
    lat1, lat2, lon1, lon2 = map(float, boundingbox)
    min_lat = min(lat1, lat2)
    max_lat = max(lat1, lat2)
    min_lon = min(lon1, lon2)
    max_lon = max(lon1, lon2)
    return min_lon, min_lat, max_lon, max_lat
