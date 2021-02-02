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
