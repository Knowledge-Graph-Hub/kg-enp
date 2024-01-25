"""Ingest ENPKG CHeMBL identifiers and activity data,
transforming into KGX format."""

import os
import sys
from typing import Optional

from kgx.cli.cli_utils import transform
from koza.cli_runner import transform_source

from kg_enp.transform_utils.transform import Transform
from kg_enp.utils.robot_utils import initialize_robot, robot_convert

CHEMBL_CONFIGS = {
    "chembl_rdf.ttl": "chembl_rdf.yaml",
}

TRANSLATION_TABLE = "./kg_enp/transform_utils/translation_table.yaml"


class CHEMBLDataTransform(Transform):
    """This transform ingests the chembl_rdf.ttl file and transforms to KGX tsv format.

    The file is preprocessed to JSON before being parsed by Koza.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "enpkg_chembl_rdf"
        super().__init__(source_name, input_dir, output_dir)

        print("Setting up ROBOT...")
        self.robot_path = os.path.join(os.getcwd(), "robot")
        self.robot_params = initialize_robot(self.robot_path)
        print(f"ROBOT path: {self.robot_path}")
        self.robot_env = self.robot_params[1]
        print(f"ROBOT evironment variables: {self.robot_env['ROBOT_JAVA_ARGS']}")

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

        print(f"Preprocessing: {name} ({data_file}) to JSON")
        data_file_json = os.path.splitext(data_file)[0] + ".json"

        if not os.path.exists(data_file_json):
            if not robot_convert(
                robot_path=self.robot_path,
                input_path=data_file,
                output_path=data_file_json,
                robot_env=self.robot_env,
            ):
                sys.exit(f"Failed to convert {data_file}!")
        else:
            print(f"Found JSON ontology at {data_file_json}.")

        print(f"Transform: {name} using source in {config}")
        transform_source(
            source=config,
            output_dir=output,
            output_format="tsv",
            global_table=TRANSLATION_TABLE,
            local_table=None,
        )
