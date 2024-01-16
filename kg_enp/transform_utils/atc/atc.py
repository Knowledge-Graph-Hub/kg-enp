"""ATC is the Anatomical Therapeutic Chemical Classification.

We use it to categorize relationships among classes of drugs,
with codes provided by DrugCentral.
See details on source files here:
https://bioportal.bioontology.org/ontologies/ATC/?p=summary
"""
import gzip
import os
import shutil
from pathlib import Path
from typing import Optional, Union
import requests_cache

from koza.cli_runner import transform_source  # type: ignore

from kg_enp.transform_utils.transform import Transform

ATC_SOURCES = {
    "ATC_DATA": "atc.csv.gz",
}

ATC_CONFIGS = {
    "ATC_DATA": "atc-classes.yaml",
}

TRANSLATION_TABLE = Path(__file__).parents[1] / "translation_table.yaml"


class ATCTransform(Transform):
    """Ingests the ATC CSV file & transforms to KGX-format node and edge lists."""

    def __init__(self, input_dir: Optional[Path] = None, output_dir: Optional[Path] = None) -> None:
        """Instantiate the transform.

        :param input_dir: Path to input directory, defaults to None
        :param output_dir: Path to output directory, defaults to None
        """
        source_name = "atc"
        super().__init__(source_name, input_dir, output_dir)
        # Any data parsed via `requests` will be cached 
        # and consecutive executions will be quicker
        requests_cache.install_cache("atc_cache")

    def run(self, atc_file: Union[Optional[Path], Optional[str]] = None) -> None:
        """Set up the ATC for Koza and call the parse function."""
        if atc_file:
            for source in [atc_file]:
                k = str(source).split(".")[0]
                data_file = self.input_base_dir / source
                self.parse(k, data_file, k)
        else:
            for k in ATC_SOURCES.keys():
                name = ATC_SOURCES[k]
                data_file = self.input_base_dir / name
                self.parse(name, data_file, k)

    def parse(self, name: str, data_file: Optional[Path], source: str) -> None:
        """Transform ATC file with Koza. Need to decompress it first.

        :param name: Name of the resource
        :param data_file: Data file of resource.
        :param source: Source name.
        :raises ValueError: If the source is unrecognized.
        """
        print(f"Parsing {data_file}")
        config = Path(__file__).parent / ATC_CONFIGS[source]
        output = self.output_dir

        # Decompress
        outname = name[:-3]
        outpath = self.input_base_dir / outname
        with gzip.open(str(data_file), "rb") as data_file_gz:
            with open(outpath, "wb") as data_file_new:
                shutil.copyfileobj(data_file_gz, data_file_new)

        # If source is unknown then we aren't going to guess
        if source not in ATC_CONFIGS:
            raise ValueError(f"Source file {source} not recognized - not transforming.")
        else:
            transform_source(
                source=config,
                output_dir=output,
                output_format="tsv",
                global_table=TRANSLATION_TABLE,
                local_table=None,
            )

        os.remove(outpath)
