# ~ widgets.py | by ANXETY ~ (All-in-One Fix)

from widget_factory import WidgetFactory
from webui_utils import update_current_webui
import json_utils as js
import ipywidgets as widgets
from pathlib import Path
import os
import re

# --- Constants and Platform Setup ---
try:
    HOME = Path(js.read(os.path.join(Path.home(), 'ANXETY', 'settings.json'), 'ENVIRONMENT.home_path', str(Path.home())))
except Exception:
    HOME = Path.home()

SCR_PATH = HOME / 'ANXETY'
SETTINGS_PATH = SCR_PATH / 'settings.json'
SCRIPTS = SCR_PATH / 'scripts'
CSS = SCR_PATH / 'CSS'
JS = SCR_PATH / 'JS'
widgets_css = CSS / 'main-widgets.css'
ENV_NAME = js.read(SETTINGS_PATH, 'ENVIRONMENT.env_name', 'local')

# --- Helper Functions ---
factory = WidgetFactory()

def read_model_data(file_path, data_key_in_file, prefixes=['none']):
    """Reads data from a file, extracts a dictionary, and returns a numbered list of its keys."""
    local_vars = {}
    if not file_path.exists():
        print(f"Warning: Data file not found at {file_path}. Skipping.")
        return prefixes
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            exec(f.read(), {}, local_vars)
        except Exception as e:
            print(f"Error executing data file {file_path}: {e}")
            return prefixes
    data_dict = local_vars
    for key_part in data_key_in_file.split('.'):
        data_dict = data_dict.get(key_part, {})
        if not isinstance(data_dict, dict):
            return prefixes
    names = list(data_dict.keys())
    numbered_names = [f"{i+1}. {name}" for i, name in enumerate(names)]
    return prefixes + numbered_names

# --- Widget Definitions ---
factory.load_css(widgets_css)

# Data file paths
sd15_models_path = SCRIPTS / '_models-data.py'
sdxl_models_path = SCRIPTS / '_xl-models-data.py'
loras_data_path = SCRIPTS / '_loras-data.py'

# WebUI selection
webui_selection = {
    'A1111': "--xformers --no-half-vae", 'ComfyUI': "--use-sage-attention --dont-print-server",
    'Forge': "--disable-xformers --opt-sdp-attention --cuda-stream --pin-shared-memory",
    'Classic': "--persistent-patches --cuda-stream --pin-shared-memory",
    'ReForge': "--xformers --cuda-stream --pin-shared-memory", 'SD-UX': "--xformers --no-half-vae"
}

# --- Create Widgets ---
model_header = factory.create_header('Model Selection (Ctrl+Click for multiple)')
model_options = read_model_data(sd15_models_path, 'sd15_model_data')
model_widget = factory.create_select_multiple(model_options, 'Models:', ('none',))
inpainting_model_widget = factory.create_checkbox('Inpainting Models', False, ['inpaint'], layout={'width': 'auto'})
XL_models_widget = factory.create_checkbox('SDXL', False, ['sdxl'], layout={'width': 'auto'})
switch_model_widget = factory.create_hbox([inpainting_model_widget, XL_models_widget])

vae_header = factory.create_header('VAE Selection')
vae_options = read_model_data(sd15_models_path, 'sd15_vae_data', ['none', 'ALL'])
vae_widget = factory.create_select_multiple(vae_options, 'VAEs:', ('none',))

lora_header = factory.create_header('LoRA Selection')
lora_options = read_model_data(loras_data_path, 'lora_data.sd15_loras', ['none', 'ALL'])
lora_widget = factory.create_select_multiple(lora_options, 'LoRAs:', ('none',))

controlnet_header = factory.create_header('ControlNet Selection')
controlnet_options = read_model_data(sd15_models_path, 'controlnet_list', ['none', 'ALL'])
controlnet_widget = factory.create_select_multiple(controlnet_options, 'ControlNets:', ('none',))

additional_header = factory.create_header('Additional Settings')
latest_webui_widget, latest_extensions_widget = factory.create_checkbox('Update WebUI', True), factory.create_checkbox('Update Extensions', True)
change_webui_widget = factory.create_dropdown(list(webui_selection.keys()), 'WebUI:', 'Forge', layout={'width': 'auto'})
commandline_arguments_widget = factory.create_text('Arguments:', webui_selection.get('Forge', ''))

save_button = factory.create_button('Save & Close', ['button', 'button_save'])
GDrive_button = factory.create_button('', layout={'width': '48px', 'height': '48px'}, class_names=['gdrive-btn'])
if ENV_NAME != 'Google Colab': GDrive_button.layout.display = 'none'

# --- Layout Assembly ---
model_col = factory.create_vbox([model_header, model_widget, switch_model_widget])
vae_col = factory.create_vbox([vae_header, vae_widget])
lora_col = factory.create_vbox([lora_header, lora_widget])
cnet_col = factory.create_vbox([controlnet_header, controlnet_widget])
download_box = factory.create_vbox([model_col, vae_col, lora_col, cnet_col], class_names=['container'])
additional_box = factory.create_vbox([additional_header, factory.create_hbox([latest_webui_widget, latest_extensions_widget, change_webui_widget]), commandline_arguments_widget], class_names=['container'])
WIDGET_LIST = factory.create_vbox([factory.create_hbox([download_box, GDrive_button]), additional_box, save_button], class_names=['mainContainer'])
factory.display(WIDGET_LIST)

# --- Callbacks ---
def on_xl_toggle(change, widget):
    is_xl = change.new
    model_path = sdxl_models_path if is_xl else sd15_models_path
    model_key = 'sdxl_models_data' if is_xl else 'sd15_model_data'
    vae_key = 'sdxl_vae_data' if is_xl else 'sd15_vae_data'
    lora_key = 'lora_data.sdxl_loras' if is_xl else 'lora_data.sd15_loras'
    cnet_key = 'controlnet_list'
    model_widget.options = read_model_data(model_path, model_key)
    vae_widget.options = read_model_data(model_path, vae_key, ['none', 'ALL'])
    lora_widget.options = read_model_data(loras_data_path, lora_key, ['none', 'ALL'])
    controlnet_widget.options = read_model_data(model_path, cnet_key, ['none', 'ALL'])
    model_widget.value, vae_widget.value, lora_widget.value, controlnet_widget.value = ('none',), ('none',), ('none',), ('none',)

def on_webui_change(change, widget):
    commandline_arguments_widget.value = webui_selection.get(change.new, '')

# --- Settings ---
SETTINGS_KEYS = [
    'XL_models', 'model', 'inpainting_model', 'vae', 'lora', 'controlnet',
    'latest_webui', 'latest_extensions', 'change_webui', 'commandline_arguments'
]
def save_settings():
    widget_values = {}
    for key in SETTINGS_KEYS:
        widget_name = f"{key}_widget"
        if widget_name in globals():
            widget_values[key] = globals()[widget_name].value
    js.save(SETTINGS_PATH, 'WIDGETS', widget_values)
    js.save(SETTINGS_PATH, 'mountGDrive', getattr(GDrive_button, 'toggle', False))
    update_current_webui(change_webui_widget.value)

def load_settings():
    if js.key_exists(SETTINGS_PATH, 'WIDGETS'):
        widget_data = js.read(SETTINGS_PATH, 'WIDGETS')
        for key in SETTINGS_KEYS:
            if key in widget_data and f"{key}_widget" in globals():
                globals()[f"{key}_widget"].value = widget_data.get(key)
    GDrive_button.toggle = js.read(SETTINGS_PATH, 'mountGDrive', False)
    GDrive_button.add_class('active') if GDrive_button.toggle else GDrive_button.remove_class('active')

def on_save_click(button):
    save_settings()
    factory.close(list(WIDGET_LIST.children), ['hide'], delay=0.8)

# --- Initialisation ---
factory.connect_widgets([(XL_models_widget, 'value')], on_xl_toggle)
factory.connect_widgets([(change_webui_widget, 'value')], on_webui_change)
save_button.on_click(on_save_click)
load_settings()
