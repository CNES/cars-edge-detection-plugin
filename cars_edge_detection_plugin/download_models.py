#!/usr/bin/env python
# coding: utf8
#
# Copyright (c) 2026 Centre National d'Etudes Spatiales (CNES).
#
# This file is part of CARS Edge detection Plugin
# (see https://github.com/CNES/cars-edge-detection-plugin).
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
This file contains the model downloading script for the Edge detection plugin
"""

import argparse
import logging
import shutil
from pathlib import Path

from huggingface_hub import hf_hub_download
from huggingface_hub.utils import HfHubHTTPError, LocalEntryNotFoundError

logger = logging.getLogger(__name__)

MODEL_MAP = {
    "vitl-normal": "Ruicheng/moge-2-vitl-normal",
    "vitb-normal": "Ruicheng/moge-2-vitb-normal",
    "vits-normal": "Ruicheng/moge-2-vits-normal",
}


def main():
    """
    Main function of the model downloading script
    """
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Download a MoGe2 model into the plugin model directory."
    )

    parser.add_argument(
        "--model",
        type=str,
        default="vitl-normal",
        choices=["vitl-normal", "vitb-normal", "vits-normal"],
        help="Which MoGe2 model variant to download.",
    )

    args = parser.parse_args()

    model_key = args.model
    repo_id = MODEL_MAP[model_key]

    logger.info(f"Selected model: {model_key} (repo: {repo_id})")

    # Compute destination path relative to current file
    base_dir = Path(__file__).resolve().parent
    dest_dir = base_dir / "applications" / "depth_map_generation" / "models"
    dest_dir.mkdir(parents=True, exist_ok=True)

    output_file = dest_dir / f"moge-2-{model_key}.pt"

    # Attempt download
    logger.info("Downloading model. This may take a while...")
    try:
        downloaded_path = hf_hub_download(repo_id=repo_id, filename="model.pt")
    except LocalEntryNotFoundError:
        logger.error(
            f"Model file 'model.pt' not found in repository {repo_id}. "
            "Verify that this repository exposes a file named model.pt."
        )
        return 1
    except HfHubHTTPError as exception:
        logger.error(f"Network or HuggingFace Hub error: {exception}")
        logger.error(
            "Check your internet connection or repository accessibility."
        )
        return 1
    except Exception as exception:
        logger.error(f"Unexpected error during model download: {exception}")
        return 1

    # Move and rename
    try:
        shutil.copy(downloaded_path, output_file)
        logger.info("Model successfully downloaded")
    except Exception as exception:
        logger.error(f"Failed to save the downloaded model: {exception}")
        return 1

    return 0


if __name__ == "__main__":
    main()
