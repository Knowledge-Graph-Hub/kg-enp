"""Ingest ENPKG CHeMBL identifiers and activity data,
transforming into KGX format."""

import os
from typing import Optional

from kgx.transformer import Transformer
from rdflib import Graph

# from koza.cli_runner import transform_source

from kg_enp.transform_utils.transform import Transform
from kg_enp.utils.robot_utils import initialize_robot, robot_convert

CHEMBL_CONFIGS = {
    "chembl_rdf.ttl": "chembl_rdf.yaml",
}

TRANSLATION_TABLE = "./kg_enp/transform_utils/translation_table.yaml"


class CHEMBLDataTransform(Transform):
    """This transform ingests the chembl_rdf.ttl file and transforms to KGX tsv format.

    The file is preprocessed from ttl being parsed by Koza.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "enpkg_chembl_rdf"
        super().__init__(source_name, input_dir, output_dir)

    def run(self, data_file: Optional[list] = None) -> None:
        """Method is called and performs needed transformations.
        Args:
            data_file: list of data files to parse
        Returns:
            None.
        """
        if data_file:
            for entry in data_file:
                k = entry.split(".")[0]
                entry = os.path.join(self.input_base_dir, entry)
                self.parse(k, entry, k)
        else:
            for entry in CHEMBL_CONFIGS:
                name = CHEMBL_CONFIGS[entry]
                entry = os.path.join(self.input_base_dir, entry)
                self.parse(name, entry, name)

    def parse(self, name: str, data_file: str, source: str) -> None:
        """Processes the data_file.
        Args:
            name: Name of the source
            data_file: data file to parse
            source: Source name
        Returns:
             None.
        """

        config = os.path.join("kg_enp/transform_utils/chembl_data/", source)
        output = self.output_dir
        data_file_nt = os.path.splitext(data_file)[0] + ".nt"
        data_file_kgx = os.path.splitext(data_file)[0] + ".tsv"

        if not os.path.exists(data_file_nt):
            print(f"Preprocessing: {data_file} to {data_file_nt}")
            g = Graph()
            g.parse(data_file)
            g.serialize(destination=data_file_nt, format="nt")
        else:
            print(f"Preprocessed file exists: {data_file_nt}")

        print(f"Transform: {data_file_nt} to {data_file_kgx}")
        kgxt = Transformer()
        inputs = {
            "filename": [data_file_nt],
            "format": "nt",
            "compression": None,
            "provided_by": "enpkg_chembl_rdf",
        }
        outputs = {
            "filename": data_file_kgx,
            "format": "tsv",
            "compression": None,
            "provided_by": "enpkg_chembl_rdf",
        }
        kgxt.transform(inputs, outputs)

        # transform_source(
        #     source=config,
        #     output_dir=output,
        #     output_format="tsv",
        #     global_table=TRANSLATION_TABLE,
        #     local_table=None,
        # )
