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
"""Task generator for top level workspace files."""
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Generator

from ayx_plugin_cli.ayx_workspace.constants import (
    AYX_CLI_UI_TEMPLATE,
    AYX_CLI_WORKSPACE_FILES_PATH,
    AYX_WORKSPACE_FILES,
    AYX_WORKSPACE_JSON_PATH,
    WORKSPACE_CONFIG_DIR,
)
from ayx_plugin_cli.ayx_workspace.models.v1 import (
    AyxWorkspaceV1,
    BackendLanguage,
)

from doit.action import CmdAction


def task_initialize_workspace() -> Generator[Dict, None, None]:
    """Initialize a workspace directory."""
    yield {
        "name": "configuration",
        "title": lambda task: "Create configuration directory",
        "actions": [(create_config_directory, [WORKSPACE_CONFIG_DIR])],
        "targets": [WORKSPACE_CONFIG_DIR],
    }

    yield {
        "name": ".gitignore",
        "title": lambda task: "Create .gitignore",
        "actions": [
            (
                copy_with_exists_check,
                [AYX_CLI_WORKSPACE_FILES_PATH / ".gitignore", Path(".gitignore")],
            )
        ],
        "targets": [Path(".gitignore")],
    }

    yield {
        "name": "README.md",
        "title": lambda task: "Create README.md",
        "actions": [
            (
                copy_with_exists_check,
                [AYX_CLI_WORKSPACE_FILES_PATH / "README.md", Path("README.md")],
            )
        ],
        "targets": [Path("README.md")],
    }

    backend_actions = []
    try:
        import ayx_python_sdk  # noqa: F401
    except ImportError:
        backend_actions.append(f"{sys.executable} -m pip install ayx-plugin-sdk")

    backend_actions.append(CmdAction(initialize_backend(AyxWorkspaceV1.load())))

    yield {
        "name": "initialize_backend",
        "title": lambda task: "Initialize backend",
        "actions": backend_actions,
        "file_dep": [AYX_WORKSPACE_JSON_PATH],
        "targets": [
            str(path.resolve()) for path in AYX_WORKSPACE_FILES[BackendLanguage.Python]
        ],
    }

    yield {
        "name": "ui",
        "title": lambda task: "Initialize UI",
        "actions": [(initialize_ui, [Path("ui")])],
    }


def create_config_directory(path: Path) -> None:
    """Create the configuration directory."""
    path.mkdir(exist_ok=False)
    _write_package_icon(path / "default_package_icon.png")


def _write_package_icon(path: Path) -> None:
    src = AYX_CLI_WORKSPACE_FILES_PATH / "default_package_icon.png"
    dest = path

    shutil.copy(src, dest)


def copy_with_exists_check(src: Path, dest: Path) -> None:
    """Copy a file, skipping creation if the destination path exists already."""
    if dest.exists():
        return

    shutil.copy(src, dest)


def initialize_backend(workspace_info: AyxWorkspaceV1) -> str:
    """Initialize the backend workspace using ayx_workspace.json."""
    if workspace_info.backend_language == BackendLanguage.Python:
        return f"ayx_python_sdk init-workspace --workspace-directory {os.getcwd()} --y"
    else:
        raise NotImplementedError(
            f"{workspace_info.backend_language} is not a supported backend."
        )


def initialize_ui(path: Path) -> None:
    """Initialize the UI directory."""
    shutil.copytree(AYX_CLI_UI_TEMPLATE, path)
