# File Descriptions in the Repository

## Directory -> `__configs__`
- Customization files, styles and other files for the UI.
- **install-deps.py**:  Script to automatically install libraries/run scripts for all user nodes (ComfyUI).
- **gradio-tunneling.py**: Script replacing the original script (gradio-tunneling) - to create a tunnel~ (ComfyUI).

## Directory -> `CSS`

- **download-result.css**: Styles for the download results widget.
- **auto-cleaner.css**: Styles for the auto-cleaner widget.
- **main-widgets.css**: Main styles for widgets.

## Directory -> `JS`

- **main-widgets.js**: Main JavaScript file for widget functionality.

## Directory -> `modules`

- **CivitaiAPI.py**: Module for interacting with the Civitai API.
- **webui_utils.py**: Utilities for working with the WebUI - setting the timer and folder paths.
- **json_utils.py**: Utilities for handling JSON data.
- **TunnelHub.py**: Module for managing tunnels.
- **widget_factory.py**: Factory for creating ipywidgets.
- **Manager.py**: Adding quick functions for downloading and cloning git repositories: `m_download` & `m_clone`.

- **__season.py**: A special module for beautiful display of the encounter message - setup.py.

## Directory -> `scripts`

- **_models-data.py**: Model data - url, name
- **_xl-models-data.py**: Model data [XL] - url, name
- **launch.py**: Main script to launch the WebUI.
- **auto-cleaner.py**: Script for automatically cleaning up unnecessary files.
- **download-result.py**: Script for processing download results.
- **setup.py**: Downloading files for work.

#### Subdirectory -> `en/ru`

- **downloading-{lang}.py**: The main script for downloading data.
- **widgets-{lang}.py**: Script for creating and displaying main widgets.

#### Subdirectory -> `UIs`

- Downloading the WebUI repository, downloading its config files and installing extensions/nodes.