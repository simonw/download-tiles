from setuptools import setup
import os

VERSION = "0.3"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="download-tiles",
    description="Download map tiles and store them in an MBTiles database",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/download-tiles",
    project_urls={
        "Issues": "https://github.com/simonw/download-tiles/issues",
        "CI": "https://github.com/simonw/download-tiles/actions",
        "Changelog": "https://github.com/simonw/download-tiles/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["download_tiles"],
    entry_points="""
        [console_scripts]
        download-tiles=download_tiles.cli:cli
    """,
    install_requires=["click", "requests", "landez==2.5.0"],
    extras_require={"test": ["pytest", "requests-mock"]},
    tests_require=["download-tiles[test]"],
    python_requires=">=3.6",
)
