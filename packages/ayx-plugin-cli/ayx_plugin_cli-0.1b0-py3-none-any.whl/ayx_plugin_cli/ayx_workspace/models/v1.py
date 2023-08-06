# Copyright (C) 2021 Alteryx, Inc. All rights reserved.
#
# Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Pydantic models for managing workspace settings."""
import json
from pathlib import Path
from typing import Dict, List, Union

from ayx_plugin_cli.ayx_workspace.constants import (
    AYX_WORKSPACE_JSON_PATH,
    BackendLanguage,
)
from ayx_plugin_cli.exceptions import WorkspaceVersionError
from ayx_plugin_cli.version import version as cli_version

from pydantic import BaseModel


class InputAnchorV1(BaseModel):
    """Input anchor settings model."""

    label: str
    allow_multiple: bool
    optional: bool


class OutputAnchorV1(BaseModel):
    """Output anchor settings model."""

    label: str
    allow_multiple: bool = False
    optional: bool = False


class ToolConfigurationV1(BaseModel):
    """Designer tool configuration settings model."""

    long_name: str
    description: str
    version: str
    search_tags: List[str]
    icon_path: Path
    input_anchors: Dict[str, InputAnchorV1]
    output_anchors: Dict[str, OutputAnchorV1]


class PythonToolSettingsV1(BaseModel):
    """Python tool settings model."""

    tool_module: str
    tool_class_name: str


class UiSettingsV1(BaseModel):
    """UI tool settings model."""

    pass


class ToolSettingsV1(BaseModel):
    """Top level tool settings model."""

    backend: Union[PythonToolSettingsV1]
    ui: UiSettingsV1
    configuration: ToolConfigurationV1


class PythonSettingsV1(BaseModel):
    """Python SDK settings model."""

    python_version: str
    requirements_local_path: Path
    requirements_thirdparty_path: Path


class ManifestV1(BaseModel):
    """Tool manifest JSON model."""

    version: str
    entry_point: Path
    tool_package: str
    tool_name: str

    def save(self, path: Path) -> None:
        """Save manifest to file."""
        with open(path, mode="w") as output_file:
            output_file.write(self.json(indent=4))


class AyxWorkspaceV1(BaseModel):
    """Top level workspace settings model."""

    name: str
    tool_category: str
    package_icon_path: Path
    author: str
    company: str
    copyright: str
    description: str
    ayx_cli_version: str
    backend_language: BackendLanguage
    backend_language_settings: Union[PythonSettingsV1]
    tools: Dict[str, ToolSettingsV1]
    tool_version: str

    @classmethod
    def load(cls, path: Path = AYX_WORKSPACE_JSON_PATH) -> "AyxWorkspaceV1":
        """Load the workspace object from a file."""
        with open(str(path)) as f:
            raw_workspace = json.load(f)

        cls._validate_workspace_version(raw_workspace)
        return AyxWorkspaceV1(**raw_workspace)

    @staticmethod
    def _validate_workspace_version(raw_workspace: Dict) -> None:
        if "ayx_cli_version" not in raw_workspace:
            raise WorkspaceVersionError(
                "ayx_cli_version not found in ayx_workspace.json. "
                "If this workspace was built with AyxPythonSdk, please rebuild using ayx_cli."
            )
        elif raw_workspace["ayx_cli_version"] != cli_version:
            raise WorkspaceVersionError(
                "This workspace was created with an incompatible version of ayx_cli."
            )

    def save(self, path: Path = AYX_WORKSPACE_JSON_PATH) -> None:
        """Save the object to a file."""
        with open(str(path), "w+") as f:
            f.write(self.json(indent=4))
