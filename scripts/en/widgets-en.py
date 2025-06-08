# ~ widgets.py | by ANXETY ~

from widget_factory import WidgetFactory        # WIDGETS
from webui_utils import update_current_webui    # WEBUI
import json_utils as js                         # JSON

import ipywidgets as widgets
from pathlib import Path
import os


# Constants
HOME = Path.home()
SCR_PATH = Path(HOME / 'ANXETY')
SETTINGS_PATH = SCR_PATH / 'settings.json'
ENV_NAME = js.read(SETTINGS_PATH, 'ENVIRONMENT.env_name')

SCRIPTS = SCR_PATH / 'scripts'

CSS = SCR_PATH / 'CSS'
JS = SCR_PATH / 'JS'
widgets_css = CSS / 'main-widgets.css'
widgets_js = JS / 'main-widgets.js'


## ======================= WIDGETS =======================

def create_expandable_button(text, url):
    return factory.create_html(f'''
    <a href="{url}" target="_blank" class="button button_api">
        <span class="icon"><</span>
        <span class="text">{text}</span>
    </a>
    ''')

def read_model_data(file_path, data_type):
    """Reads model, VAE, or ControlNet data from the specified file."""
    type_map = {
        'model': ('model_list', ['none']),
        'vae': ('vae_list', ['none', 'ALL']),
        'cnet': ('controlnet_list', ['none', 'ALL'])
    }
    key, prefixes = type_map[data_type]
    local_vars = {}

    with open(file_path, 'r') as f:
        exec(f.read(), local_vars)
    
    data_list = local_vars.get(key, {})
    return prefixes + list(data_list.keys())

def display_widgets(is_new_ui):
    global factory
    factory = WidgetFactory()
    
    # Paths to data files
    models_data_path = SCRIPTS / '_models-data.py'
    xl_models_data_path = SCRIPTS / '_xl-models-data.py'

    # Read data from files
    model_options = read_model_data(models_data_path, 'model')
    vae_options = read_model_data(models_data_path, 'vae')
    cnet_options = read_model_data(models_data_path, 'cnet')
    xl_model_options = read_model_data(xl_models_data_path, 'model')
    
    # Combine SD1.5 and SDXL models
    combined_model_options = model_options + xl_model_options[1:] # Exclude 'none' from xl list

    # Create widgets
    Model_header = factory.create_header('Model')
    Model_widget = factory.create_dropdown(combined_model_options, 'Checkpoint:', '1. AcornMoarMindBreak by Remphanstar [SD1.5]')
    Model_num_widget = factory.create_text('Model Number:', '', 'Enter the corresponding number(s) of the models to download, separated by commas.')
    Model_url_widget = factory.create_text('Model URL:', '', 'Enter a direct link to the model.')
    Inpainting_model_widget = factory.create_checkbox('Inpainting Model', False, class_names=['inpaint'], layout={'width': '25%'})
    
    Vae_header = factory.create_header('VAE')
    Vae_widget = factory.create_dropdown(vae_options, 'VAE:', 'none')
    Vae_url_widget = factory.create_text('VAE URL:', '', 'Enter a direct link to the VAE.')

    LoRA_header = factory.create_header('LoRA')
    LoRA_widget = factory.create_dropdown(['none'], 'LoRA:', 'none')
    LoRA_strength_widget = widgets.FloatSlider(value=0.7, min=0, max=1, step=0.05, description='Strength:', readout_format='.2f', style = {'description_width': 'initial'}, layout={'width': '100%'})
    LoRA_strength_widget.add_class('lora-strength')
    LoRA_url_widget = factory.create_text('LoRA URL:', '', 'Enter a direct link to the LoRA.')
    
    Embedding_header = factory.create_header('Embedding')
    Embedding_url_widget = factory.create_text('Embedding URL:', '', 'Enter a direct link to the embedding.')
    
    ControlNet_header = factory.create_header('ControlNet')
    ControlNet_widget = widgets.SelectMultiple(options=cnet_options, value=['none'], description='ControlNet Models:', disabled=False, style={'description_width': 'initial'}, layout={'width': '100%'})
    ControlNet_widget.add_class('cnet-checkbox')
    Extensions_url_widget = factory.create_text('Extensions URL:', '', 'Enter a direct link to the extension.')
    
    ADetailer_header = factory.create_header('ADetailer')
    ADetailer_url_widget = factory.create_text('ADetailer URL:', '', 'Enter a direct link to the ADetailer model.')
    
    Custom_header = factory.create_header('Custom Download')
    custom_file_urls_widget = factory.create_textarea('', '🔗 Enter any other direct download links here, one link per line.')
    
    # Layout and display
    left_box = widgets.VBox([Model_header, Model_widget, Model_num_widget, Model_url_widget, Inpainting_model_widget, Vae_header, Vae_widget, Vae_url_widget, LoRA_header, LoRA_widget, LoRA_strength_widget, LoRA_url_widget, Embedding_header, Embedding_url_widget])
    right_box = widgets.VBox([ControlNet_header, ControlNet_widget, Extensions_url_widget, ADetailer_header, ADetailer_url_widget, Custom_header, custom_file_urls_widget])
    
    main_box = widgets.HBox([left_box, right_box])
    
    # Conditionally add API buttons if not new UI
    if not is_new_ui:
        API_header = factory.create_header('API Information')
        sd_API_button = create_expandable_button('SD-WebUI API', 'https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API')
        civitai_API_button = create_expandable_button('Civitai API', 'https://github.com/civitai/civitai/wiki/REST-API-Reference')
        api_box = widgets.VBox([API_header, sd_API_button, civitai_API_button])
        main_box = widgets.HBox([left_box, right_box, api_box])
        
    display(main_box)

# These global variables will be set by the calling notebook cell
is_new_ui = False
change_webui_widget = None
GDrive_button = None

# Settings keys for saving/loading
SETTINGS_KEYS = [
    'Model', 'Vae', 'LoRA', 'LoRA_strength', 'ControlNet',
     'Inpainting_model',
      'Model_num', 'custom_output',
      'Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 'Extensions_url', 'ADetailer_url',
      'custom_file_urls'
]

def save_settings():
    """Save widget values to settings."""
    widgets_values = {key: globals()[f"{key}_widget"].value for key in SETTINGS_KEYS}
    js.save(SETTINGS_PATH, 'WIDGETS', widgets_values)

    # Save Status GDrive-btn
    js.save(SETTINGS_PATH, 'mountGDrive', True if GDrive_button.toggle else False)

    update_current_webui(change_webui_widget.value)  # Update Selected WebUI in setting.json

def load_settings():
    """Load widget values from settings."""
    if js.key_exists(SETTINGS_PATH, 'WIDGETS'):
        widget_data = js.read(SETTINGS_PATH, 'WIDGETS')
        for key in SETTINGS_KEYS:
            if key in widget_data:
                globals()[f"{key}_widget"].value = widget_data.get(key, '')

    # Load Status GDrive-btn
    GD_status = js.read(SETTINGS_PATH, 'mountGDrive') or False
    GDrive_button.toggle = (GD_status == True)
    if GDrive_button.toggle:
        GDrive_button.add_class('active')
    else:
        GDrive_button.remove_class('active')

def save_data(button):
    """Handle save button click."""
    save_settings()
    # factory.close()
    button.add_class('active')

def on_value_change(change):
    save_settings()

def init():
    # This function is called from the notebook
    global is_new_ui, change_webui_widget, GDrive_button
    is_new_ui = (ENV_NAME == 'Forge' or ENV_NAME == 'SD-UX')
    
    display_widgets(is_new_ui)
    
    change_webui_widget = factory.get_widget_by_class('change-webui')
    GDrive_button = factory.get_widget_by_class('gdrive-button')
    
    save_button = factory.get_widget_by_class('save-button')
    if save_button:
        save_button.on_click(save_data)
        
    load_settings()

    # for key in SETTINGS_KEYS:
    #     widget = globals().get(f"{key}_widget")
    #     if widget:
    #         widget.observe(on_value_change, names='value')

init()
