# ~ widgets.py | by ANXETY ~ (Corrected Version)

from widget_factory import WidgetFactory
from webui_utils import update_current_webui, SHARED_MODEL_BASE
import json_utils as js

import ipywidgets as widgets
from pathlib import Path
import os

# --- Constants and Platform Setup ---
PLATFORM = os.environ.get('DETECTED_PLATFORM', 'local')

# Correctly determine HOME path from settings if available
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
widgets_js = JS / 'main-widgets.js'
ENV_NAME = js.read(SETTINGS_PATH, 'ENVIRONMENT.env_name', 'local')

# --- Helper Functions ---
factory = WidgetFactory()

def create_expandable_button(text, url):
    return factory.create_html(f'''
    <a href="{url}" target="_blank" class="button button_api">
        <span class="icon">&lt;</span><span class="text">{text}</span>
    </a>''')

def read_model_data(file_path, data_key_in_file, prefixes=['none']):
    """Reads data from a Python file by executing it and extracting a dictionary."""
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

    return prefixes + list(data_dict.keys())

# --- Widget Definitions ---
HR = widgets.HTML('<hr>')
factory.load_css(widgets_css)
factory.load_js(widgets_js)

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

# Model
model_header = factory.create_header('Model Selection')
model_options = read_model_data(sd15_models_path, 'sd15_model_data')
model_widget = factory.create_dropdown(model_options, 'Model:', 'none')
model_num_widget = factory.create_text('Model Number:', '', 'Enter numbers, separated by commas')
inpainting_model_widget = factory.create_checkbox('Inpainting Models', False, ['inpaint'], layout={'width': 'auto'})
XL_models_widget = factory.create_checkbox('SDXL', False, ['sdxl'], layout={'width': 'auto'})
switch_model_widget = factory.create_hbox([inpainting_model_widget, XL_models_widget])

# VAE
vae_header = factory.create_header('VAE Selection')
vae_options = read_model_data(sd15_models_path, 'sd15_vae_data', ['none', 'ALL'])
vae_widget = factory.create_dropdown(vae_options, 'Vae:', 'none')
vae_num_widget = factory.create_text('Vae Number:', '', 'Enter numbers, separated by commas')

# LoRA
lora_header = factory.create_header('LoRA Selection')
lora_options = read_model_data(loras_data_path, 'lora_data.sd15_loras', ['none', 'ALL'])
lora_widget = factory.create_dropdown(lora_options, 'LoRA:', 'none')
lora_num_widget = factory.create_text('LoRA Number:', '', 'Enter numbers, separated by commas')
lora_strength_widget = factory.create_slider(0.7, 0, 1, 'LoRA Strength:', ['lora-strength'])

# Additional Config
additional_header = factory.create_header('Additionally')
latest_webui_widget = factory.create_checkbox('Update WebUI', True)
latest_extensions_widget = factory.create_checkbox('Update Extensions', True)
check_custom_nodes_deps_widget = factory.create_checkbox('Check Custom-Nodes Dependencies', True)
change_webui_widget = factory.create_dropdown(list(webui_selection.keys()), 'WebUI:', 'Forge', layout={'width': 'auto'})
detailed_download_widget = factory.create_dropdown(['off', 'on'], 'Detailed Download:', 'off', layout={'width': 'auto'})
choose_changes_widget = factory.create_hbox([latest_webui_widget, latest_extensions_widget, check_custom_nodes_deps_widget, change_webui_widget, detailed_download_widget], layout={'justify_content': 'space-between'})
controlnet_widget = factory.create_dropdown(read_model_data(sd15_models_path, 'controlnet_list', ['none', 'ALL']), 'ControlNet:', 'none')
controlnet_num_widget = factory.create_text('ControlNet Number:', '', 'Enter numbers, separated by commas')
commit_hash_widget = factory.create_text('Commit Hash:', '', 'Switch between branches or commits.')
commandline_arguments_widget = factory.create_text('Arguments:', webui_selection.get('Forge', ''))
theme_accent_widget = factory.create_dropdown(['anxety', 'blue', 'green', 'peach', 'pink', 'red', 'yellow'], 'Theme Accent:', 'anxety', layout={'width': 'auto', 'margin': '0 0 0 8px'})
additional_footer = factory.create_hbox([commandline_arguments_widget, theme_accent_widget])

# API Tokens
civitai_token_widget = factory.create_text('CivitAI Token:', 'ff14ef326fa02885e8202e4d44fc9a13', 'Enter your CivitAi API token.')
huggingface_token_widget = factory.create_text('HuggingFace Token:', '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')
ngrok_token_widget = factory.create_text('Ngrok Token:', '2tjxIXifSaGR3dMhkvhk6sZqbGo_6ZfBZLZHMbtAjfRmfoDW5')
zrok_token_widget = factory.create_text('Zrok Token:', '')

# Custom Download
custom_download_header_popup = factory.create_html('''<div class="header" style="cursor: pointer;" onclick="toggleContainer()">Custom Download</div>...''') # Truncated
empowerment_widget = factory.create_checkbox('Empowerment', True, ['empowerment'])
prefilled_empowerment_text = """
# Pre-loaded Embeddings (will be downloaded automatically)
embed:https://huggingface.co/Remphanstar/Rojos/resolve/main/bastard_unrestricted_D_15-20.bin?download=true[bastard_unrestricted_D_15-20.bin]
embed:https://huggingface.co/Remphanstar/Rojos/resolve/main/bastard_unrestricted_C_5-15.bin?download=true[bastard_unrestricted_C_5-15.bin]
embed:https://huggingface.co/Remphanstar/Rojos/resolve/main/bastard_unrestricted_C2_10-15.bin?download=true[bastard_unrestricted_C2_10-15.bin]
embed:https://huggingface.co/Remphanstar/Rojos/resolve/main/bastard_unrestricted_B_5-10.bin?download=true[bastard_unrestricted_B_5-10.bin]
embed:https://huggingface.co/Remphanstar/Rojos/resolve/main/bastard_unrestricted_A_0-5.bin?download=true[bastard_unrestricted_A_0-5.bin]
"""
empowerment_output_widget = factory.create_textarea('', prefilled_empowerment_text, 'Use special tags...')
Model_url_widget = factory.create_text('Model:')
Vae_url_widget = factory.create_text('Vae:')
LoRA_url_widget = factory.create_text('LoRA:')
Embedding_url_widget = factory.create_text('Embedding:')
Extensions_url_widget = factory.create_text('Extensions:')
ADetailer_url_widget = factory.create_text('ADetailer:')
custom_file_urls_widget = factory.create_text('File (txt):')

# Buttons
save_button = factory.create_button('Save', ['button', 'button_save'])
GDrive_button = factory.create_button('', layout={'width': '48px', 'height': '48px'}, class_names=['gdrive-btn'])
if ENV_NAME != 'Google Colab': GDrive_button.layout.display = 'none'

# --- Layout Assembly ---
model_col = factory.create_vbox([model_header, model_widget, model_num_widget, switch_model_widget])
vae_col = factory.create_vbox([vae_header, vae_widget, vae_num_widget])
lora_col = factory.create_vbox([lora_header, lora_widget, lora_num_widget, lora_strength_widget])
left_box = factory.create_vbox([model_col, vae_col, lora_col])
right_box = factory.create_vbox([
    additional_header, choose_changes_widget, HR,
    controlnet_widget, controlnet_num_widget, commit_hash_widget,
    factory.create_hbox([civitai_token_widget, create_expandable_button('Get', 'https://civitai.com/user/account')]),
    factory.create_hbox([huggingface_token_widget, create_expandable_button('Get', 'https://huggingface.co/settings/tokens')]),
    factory.create_hbox([ngrok_token_widget, create_expandable_button('Get', 'https://dashboard.ngrok.com/get-started/your-authtoken')]),
    factory.create_hbox([zrok_token_widget, create_expandable_button('Register', 'https://colab.research.google.com/drive/1d2sjWDJi_GYBUavrHSuQyHTDuLy36WpU')]),
    HR, additional_footer
])
top_container = factory.create_hbox([factory.create_vbox([left_box, right_box], class_names=['container']), GDrive_button])
custom_dl_container = factory.create_vbox([custom_download_header_popup, empowerment_widget, empowerment_output_widget, Model_url_widget, Vae_url_widget, LoRA_url_widget, Embedding_url_widget, Extensions_url_widget, ADetailer_url_widget, custom_file_urls_widget], class_names=['container', 'container_cdl'])
WIDGET_LIST = factory.create_vbox([top_container, custom_dl_container, save_button], class_names=['mainContainer'])
factory.display(WIDGET_LIST)

# --- Callbacks ---
def on_xl_toggle(change, widget):
    is_xl = change.new
    model_path = sdxl_models_path if is_xl else sd15_models_path
    model_key = 'sdxl_models_data' if is_xl else 'sd15_model_data'
    vae_key = 'sdxl_vae_data' if is_xl else 'sd15_vae_data'
    cnet_key = 'controlnet_list'
    lora_key = 'lora_data.sdxl_loras' if is_xl else 'lora_data.sd15_loras'
    
    model_widget.options = read_model_data(model_path, model_key)
    vae_widget.options = read_model_data(model_path, vae_key, ['none', 'ALL'])
    controlnet_widget.options = read_model_data(model_path, cnet_key, ['none', 'ALL'])
    lora_widget.options = read_model_data(loras_data_path, lora_key, ['none', 'ALL'])
    
    model_widget.value = 'none'
    vae_widget.value = 'none'
    lora_widget.value = 'none'
    controlnet_widget.value = 'none'

def on_webui_change(change, widget):
    is_comfy = change.new == 'ComfyUI'
    commandline_arguments_widget.value = webui_selection.get(change.new, '')
    latest_extensions_widget.layout.display = 'none' if is_comfy else ''
    check_custom_nodes_deps_widget.layout.display = '' if is_comfy else 'none'
    theme_accent_widget.layout.display = 'none' if is_comfy else ''
    Extensions_url_widget.description = 'Custom Nodes:' if is_comfy else 'Extensions:'

def on_empowerment_toggle(change, widget):
    is_empowered = change.new
    widgets_to_hide = [Model_url_widget, Vae_url_widget, LoRA_url_widget, Embedding_url_widget, Extensions_url_widget, ADetailer_url_widget]
    for w in widgets_to_hide:
        w.add_class('empowerment-text-field')
        w.remove_class('hidden') if not is_empowered else w.add_class('hidden')
    empowerment_output_widget.remove_class('hidden') if is_empowered else empowerment_output_widget.add_class('hidden')

# --- Settings Management ---
SETTINGS_KEYS = [
    'XL_models', 'model', 'model_num', 'inpainting_model', 'vae', 'vae_num', 'lora', 'lora_num', 'lora_strength',
    'latest_webui', 'latest_extensions', 'check_custom_nodes_deps', 'change_webui', 'detailed_download',
    'controlnet', 'controlnet_num', 'commit_hash', 'civitai_token', 'huggingface_token', 'zrok_token', 
    'ngrok_token', 'commandline_arguments', 'theme_accent', 'empowerment', 'empowerment_output', 'Model_url', 
    'Vae_url', 'LoRA_url', 'Embedding_url', 'Extensions_url', 'ADetailer_url', 'custom_file_urls'
]

def save_settings():
    widget_values = {key: globals().get(f"{key}_widget", type('obj', (object,), {'value': None})).value for key in SETTINGS_KEYS}
    js.save(SETTINGS_PATH, 'WIDGETS', widget_values)
    js.save(SETTINGS_PATH, 'mountGDrive', getattr(GDrive_button, 'toggle', False))
    update_current_webui(change_webui_widget.value)

def load_settings():
    if js.key_exists(SETTINGS_PATH, 'WIDGETS'):
        widget_data = js.read(SETTINGS_PATH, 'WIDGETS')
        for key in SETTINGS_KEYS:
            if key in widget_data:
                if f"{key}_widget" in globals():
                    globals()[f"{key}_widget"].value = widget_data[key]
    GDrive_button.toggle = js.read(SETTINGS_PATH, 'mountGDrive', False)
    GDrive_button.add_class('active') if GDrive_button.toggle else GDrive_button.remove_class('active')

def on_save_click(button):
    save_settings()
    factory.close([top_container, custom_dl_container, save_button], ['hide'], delay=0.8)

# --- Initialisation ---
factory.connect_widgets([(XL_models_widget, 'value')], on_xl_toggle)
factory.connect_widgets([(change_webui_widget, 'value')], on_webui_change)
factory.connect_widgets([(empowerment_widget, 'value')], on_empowerment_toggle)
save_button.on_click(on_save_click)
on_empowerment_toggle({'new': empowerment_widget.value}, empowerment_widget)
on_webui_change({'new': change_webui_widget.value}, change_webui_widget)
load_settings()
