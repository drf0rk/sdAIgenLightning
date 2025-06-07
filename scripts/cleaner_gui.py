import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from pathlib import Path
import shutil
import os
import sys

# Assume json_utils is available since setup.py should have added modules to sys.path
try:
    import json_utils as js
except ImportError:
    # Fallback if json_utils isn't imported for some reason
    class FallbackJsonUtils:
        def read(self, *args, **kwargs):
            return {}
    js = FallbackJsonUtils()
    print("Warning: json_utils not found, using fallback for settings.")


# Constants (read from settings.json or derive)
SETTINGS_PATH = Path.home() / 'ANXETY' / 'settings.json'

# Attempt to load settings to get paths
try:
    settings = js.read(SETTINGS_PATH)
    HOME_PATH = Path(settings.get('ENVIRONMENT', {}).get('home_path', str(Path.home())))
    SCR_PATH = Path(settings.get('ENVIRONMENT', {}).get('scr_path', str(Path.home() / 'ANXETY')))
    WEBUI_PATH = Path(settings.get('WEBUI', {}).get('webui_path', str(HOME_PATH / 'webui')))
    VENV_PATH = Path(settings.get('ENVIRONMENT', {}).get('venv_path', str(HOME_PATH / 'venv')))
    SHARED_MODEL_BASE = Path(HOME_PATH / 'sd_models_shared') # Consistent with webui_utils.py
except Exception as e:
    # Fallback for paths if settings.json cannot be read or is incomplete
    print(f"Warning: Could not load full settings for cleaner paths ({e}). Using default derived paths.")
    HOME_PATH = Path.home()
    SCR_PATH = HOME_PATH / 'ANXETY'
    WEBUI_PATH = HOME_PATH / 'webui' # Fallback
    VENV_PATH = HOME_PATH / 'venv'
    SHARED_MODEL_BASE = HOME_PATH / 'sd_models_shared'


def delete_folder(path, description):
    """Deletes a folder if it exists, with confirmation and feedback."""
    if path.exists():
        clear_output(wait=True)
        print(f"🗑️ Attempting to delete: {description} ({path})...")
        try:
            shutil.rmtree(path)
            print(f"✅ Successfully deleted: {description}")
        except Exception as e:
            print(f"❌ Error deleting {description} ({path}): {e}")
    else:
        clear_output(wait=True)
        print(f"ℹ️ {description} ({path}) does not exist. Skipping.")

def delete_anxiety_folder(button):
    delete_folder(SCR_PATH, "ANXETY folder")

def delete_script_generated_folders(button):
    clear_output(wait=True)
    print("🗑️ Initiating deletion of all major script-generated content...")
    
    folders_to_delete = [
        SCR_PATH, # The ANXETY folder
        SHARED_MODEL_BASE, # The shared models folder
        VENV_PATH, # The Python virtual environment
        WEBUI_PATH # The currently installed WebUI (e.g., ReForge)
    ]

    for folder in folders_to_delete:
        delete_folder(folder, f"'{folder.name}' folder")
    
    print("\nCleanup attempt complete.")

# --- GUI Setup ---
output_area = widgets.Output()

header = widgets.HTML("<h3>🧹 sdAIgen Cleanup Utility</h3>")

anxiety_button = widgets.Button(description="Delete ANXETY Folder", button_style='danger')
anxiety_button.on_click(delete_anxiety_folder)

script_generated_button = widgets.Button(description="Delete All Script-Generated Content", button_style='danger')
script_generated_button.on_click(delete_script_generated_folders)

warning_html = widgets.HTML("""
    <p style="color: red; font-weight: bold;">
        WARNING: These actions are irreversible and will delete files. Use with extreme caution.
    </p>
    <p style="color: yellow;">
        "Delete All Script-Generated Content" will remove:
        <ul>
            <li>Your `ANXETY` scripts and settings.</li>
            <li>All models in your `sd_models_shared` folder.</li>
            <li>Your Python virtual environment (`venv`).</li>
            <li>Your selected WebUI installation (e.g., `ReForge`).</li>
        </ul>
        This will effectively revert your environment to a clean state, requiring a full re-setup from the first cell.
    </p>
""")

display(header, warning_html, anxiety_button, script_generated_button, output_area)

# Redirect print statements to the output_area (for the GUI buttons)
def custom_print_to_output_area(*args, **kwargs):
    with output_area:
        built_in_print(*args, **kwargs)

# Save original print function
built_in_print = print
sys.stdout = custom_print_to_output_area
sys.stderr = custom_print_to_output_area
