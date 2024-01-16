"""Download resources from YAML file."""

import yaml

from downloaders import BaseDownloader

from kghub_downloader.download_utils import download_from_yaml  # type: ignore

GRAPH_DATA_FILE = "enpkg.yaml"


def download(
    yaml_file: str, output_dir: str, snippet_only: bool, ignore_cache: bool = False
) -> None:
    """Download data files from list of URLs.

    DL based on config (default: download.yaml)
    into data directory (default: data/).

    This also parses the file enpkg.yaml to determine additional data
    to retrieve.

    :param yaml_file: A string pointing to the yaml file
    :param utilized to facilitate the downloading of data.
    :param output_dir: A string pointing to the location to download data to.
    :param snippet_only: Downloads only the first 5 kB of the source,for testing and file checks.
    :param ignore_cache: Ignore cache and download files even if they exist [false]
    :return: None.
    """
    download_from_yaml(
        yaml_file=yaml_file,
        output_dir=output_dir,
        snippet_only=snippet_only,
        ignore_cache=ignore_cache,
    )

    with open(GRAPH_DATA_FILE, "r") as infile:
        data = yaml.safe_load(infile)
        datasets = [dataset for dataset in data["graphs"] if "zenodo" in dataset]

    urls = []
    paths = []

    for dataset in datasets:
        urls.append(f"https://zenodo.org/api/records/{dataset['zenodo'][0]}/files-archive")
        paths.append(output_dir + "/" + dataset["dataset"] + ".zip")

    BaseDownloader(
        process_number=1, auto_extract=True, delete_original_after_extraction=True
    ).download(urls=urls, paths=paths)
