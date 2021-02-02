from click.testing import CliRunner
from download_tiles.cli import cli
import pytest


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("cli, version ")


@pytest.mark.parametrize(
    "args,expected_error",
    [
        ("", "mbtiles argument is required"),
        ("--bbox 1", "bbox should be min-lon,min-lat,max-lon,max-lat"),
        ("--zoom-levels dog", "zoom-levels should be a single number or"),
        ("-z 10-7", "zoom-levels should be a low-high range"),
        ("-z 10-25", "Maximum zoom level is 24"),
        ("--tiles-url blah", "tiles-url should include {z}, {x}, {y}"),
    ],
)
def test_various_error_messages(args, expected_error):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, args)
        assert result.exit_code != 0
        assert expected_error in result.output


@pytest.mark.parametrize(
    "args,url_args,boundingbox,expected_bbox",
    [
        (
            "--country madagascar",
            "country=madagascar",
            ["-25.784021", "-11.732889", "42.9680076", "50.6727307"],
            "42.9680076,-25.784021,50.6727307,-11.732889",
        ),
        (
            "--city london",
            "city=london",
            ["51.2867601", "51.6918741", "-0.5103751", "0.3340155"],
            "-0.5103751,51.2867601,0.3340155,51.6918741",
        ),
    ],
)
def test_city_and_country(requests_mock, args, url_args, boundingbox, expected_bbox):
    requests_mock.get(
        "https://nominatim.openstreetmap.org/?{}&format=json&limit=1".format(url_args),
        json=[
            {
                "boundingbox": boundingbox,
            }
        ],
    )
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, args + " --show-bbox")
        assert result.exit_code == 0
        assert result.output.strip() == expected_bbox
