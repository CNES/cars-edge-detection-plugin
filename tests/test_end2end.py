#!/usr/bin/env python
# coding: utf8
#
# Copyright (c) 2025 Centre National d'Etudes Spatiales (CNES).
#
# This file is part of CARS
# (see https://github.com/CNES/cars).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Depth map generation end2end test file
"""

from __future__ import absolute_import

import os
import tempfile

# Third party imports
import pytest
from cars.core.utils import safe_makedirs

from cars_edge_detection_plugin.pipelines.edge_detection import (
    edge_detection_pipeline,
)

# CARS Tests imports
from .helpers import absolute_data_path, assert_same_images
from .helpers import cars_copy2 as copy2
from .helpers import generate_input_json, temporary_dir

NB_WORKERS = 4


@pytest.mark.end2end_tests
def test_end2end_gizeh_inputs():
    """
    End to end processing

    Test pipeline with a real-world image
    """

    with tempfile.TemporaryDirectory(dir=temporary_dir()) as directory:

        input_json = absolute_data_path(
            "input/data_gizeh_crop/configfile_crop.json"
        )

        # Run pipeline
        _, input_conf = generate_input_json(
            input_json,
            directory,
            "multiprocessing",
            orchestrator_parameters={
                "nb_workers": NB_WORKERS,
                "max_ram_per_worker": 500,
            },
        )

        conf_applications = {
            "depth_map_generation": {"model": "Ruicheng/moge-2-vitb-normal"}
        }

        input_conf["edge_detection"]["applications"] = conf_applications
        input_conf["edge_detection"]["advanced"][
            "save_intermediate_data"
        ] = True

        pipeline = edge_detection_pipeline.EdgeDetection(input_conf)
        pipeline.run()

        out_dir = os.path.join(input_conf["output"]["directory"])

        intermediate_output_dir = "intermediate_data"
        ref_output_dir = "ref_output"

        safe_makedirs(absolute_data_path(intermediate_output_dir))

        to_check = [
            (
                os.path.join(out_dir, "edge_detection/one/edges.tif"),
                "end2end_gizeh_crop_edges.tif",
            ),
            (
                os.path.join(
                    out_dir, "dump_dir/depth_map_generation/one/normals.tif"
                ),
                "end2end_gizeh_crop_normals.tif",
            ),
            (
                os.path.join(
                    out_dir, "dump_dir/depth_map_generation/one/tile_id.tif"
                ),
                "end2end_gizeh_crop_tile_id.tif",
            ),
            (
                os.path.join(
                    out_dir, "dump_dir/depth_map_generation/one/depth.tif"
                ),
                "end2end_gizeh_crop_depth.tif",
            ),
        ]

        for out_file_path, ref_file_name in to_check:
            copy2(
                out_file_path,
                absolute_data_path(
                    os.path.join(
                        intermediate_output_dir,
                        ref_file_name,
                    )
                ),
            )
        for out_file_path, ref_file_name in to_check:
            assert_same_images(
                out_file_path,
                absolute_data_path(
                    os.path.join(
                        ref_output_dir,
                        "data_gizeh_crop",
                        ref_file_name,
                    )
                ),
                rtol=1.0e-6,
                atol=1.0e-6,
            )
