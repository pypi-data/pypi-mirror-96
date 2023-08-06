# Copyright (C) 2019-2021 HERE Europe B.V.
# SPDX-License-Identifier: MIT

"""HERE Map Widget for Jupyter - use HERE Maps API for
JavaScript in your Jupyter Notebook.
This widget enables you to use the HERE Map View in Jupyter Notebook
to make analysis ofgeospatial data easier and more interactive.
"""

from ._version import __version__, version_info
from .configs import *
from .map import *


def _jupyter_nbextension_paths():
    """Called by Jupyter Notebook Server to detect if it is a valid nbextension and
    to install the widget

    Returns
    =======
    section: The section of the Jupyter Notebook Server to change.
        Must be 'notebook' for widget extensions
    src: Source directory name to copy files from. Webpack outputs generated files
        into this directory and Jupyter Notebook copies from this directory during
        widget installation
    dest: Destination directory name to install widget files to. Jupyter Notebook copies
        from `src` directory into <jupyter path>/nbextensions/<dest> directory
        during widget installation
    require: Path to importable AMD JavaScript module inside the
        <jupyter path>/nbextensions/<dest> directory
    """
    return [
        {
            "section": "notebook",
            "src": "nbextension",
            "dest": "map-widget-for-jupyter",
            "require": "map-widget-for-jupyter/extension",
        }
    ]


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "map-widget-for-jupyter"}]
