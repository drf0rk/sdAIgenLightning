import os
import sys
import ast
from IPython.display import display, HTML

# --- Define Absolute Base Path ---
# This makes file lookups robust and independent of the current working directory.
try:
    # This works when run from the notebook via %run, assuming ANXETY is in the current dir
    BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), 'ANXETY'))
except NameError:
    # Fallback for other execution contexts
    BASE_DIR = "/teamspace/studios/this_studio/ANXETY"

MODULES_DIR = os.path.join(BASE_DIR, 'modules')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
if MODULES_DIR not in sys.path:
    sys.path.append(MODULES_DIR)

# Correctly import from ipywidgets and widget_factory
from ipywidgets import widgets, Layout
from widget_factory import WidgetFactory

# =================================================================================
# == HELPER FUNCTION TO READ AND COMBINE DATA FROM THE CORRECTED SCRIPT FILES
# =================================================================================
def read_and_combine_data(file_map):
    """
    Reads multiple data files, executes them, and combines keys from specified dictionaries.
    """
    all_options = []
    
    for file_path, dict_names in file_map.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            local_scope = {}
            exec(content, local_scope)
            
            for dict_name in dict_names:
                data_dict = local_scope.get(dict_name)
                if isinstance(data_dict, dict):
                    # Handle nested dictionaries like in lora_data {"sd15_loras": {...}}
                    is_nested = any(isinstance(v, dict) for v in data_dict.values())
                    if is_nested:
                        for sub_dict_key, sub_dict in data_dict.items():
                            if isinstance(sub_dict, dict):
                                all_options.extend(list(sub_dict.keys()))
                    else:
                        all_options.extend(list(data_dict.keys()))
        except FileNotFoundError:
            print(f"Warning: Data file not found at {file_path}. Skipping.")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    # Remove duplicates and sort alphabetically
    return sorted(list(set(all_options)))

# =================================================================================
# == MAIN WIDGET CREATION
# =================================================================================

# Create a factory instance
factory = WidgetFactory()

# --- Define Absolute File Paths to your data scripts ---
SD15_DATA_FILE = os.path.join(SCRIPTS_DIR, '_models-data.py')
SDXL_DATA_FILE = os.path.join(SCRIPTS_DIR, '_xl-models-data.py')
LORAS_FILE = os.path.join(SCRIPTS_DIR, '_loras-data.py')

# --- Read and Combine Data for Widgets ---
model_map = { SD15_DATA_FILE: ["sd15_model_data"], SDXL_DATA_FILE: ["sdxl_models_data"] }
model_options = read_and_combine_data(model_map)

lora_map = { LORAS_FILE: ["lora_data"] }
lora_options = read_and_combine_data(lora_map)

vae_map = { SD15_DATA_FILE: ["sd15_vae_data"], SDXL_DATA_FILE: ["sdxl_vae_data"] }
vae_options = read_and_combine_data(vae_map)

controlnet_map = { SD15_DATA_FILE: ["sd15_controlnet_list"], SDXL_DATA_FILE: ["sdxl_controlnet_list"] }
controlnet_options = read_and_combine_data(controlnet_map)

# --- Create Widgets using the combined data ---
# Model Widgets
model_header = factory.create_header('Model Selection')
model_default = model_options[0] if model_options else None
model_widget = factory.create_dropdown(model_options, 'Model:', model_default)

# LoRA Widgets
lora_header = factory.create_header('LoRA Selection')
lora_default = lora_options[0] if lora_options else None
lora_widget = factory.create_dropdown(lora_options, 'LoRA:', lora_default)
lora_strength_widget = widgets.FloatSlider(
    value=0.7, min=0.0, max=1.0, step=0.05, description='LoRA Strength:',
    style={'description_width': 'initial'}, layout=Layout(width='100%')
)
lora_strength_widget.add_class('lora-strength')

# VAE Widgets
vae_header = factory.create_header('VAE Selection')
vae_default = vae_options[0] if vae_options else None
vae_widget = factory.create_dropdown(vae_options, 'VAE:', vae_default)

# ControlNet Widgets
controlnet_header = factory.create_header('ControlNet Selection')
controlnet_default = [controlnet_options[0]] if controlnet_options else []
controlnet_widget = widgets.SelectMultiple(
    options=controlnet_options, value=controlnet_default, description='ControlNet Models:',
    style={'description_width': 'initial'}, layout=Layout(width='100%'), rows=8
)

# Download Options
download_header = factory.create_header('Download Options')
# *** THIS IS THE CORRECTED CODE FOR THE BUTTONS ***
# The factory.create_button only accepts (description, button_style)
download_button = factory.create_button('Download Selected', 'primary')
config_name_widget = factory.create_text('Config Name:', placeholder='e.g. my-config')
save_config_widget = factory.create_button('Save Config', 'success')
# Manually add classes if needed, as the factory doesn't handle it for buttons
download_button.add_class('download-button')
save_config_widget.add_class('save-button')
# *** END OF CORRECTION ***


# Display all widgets
display(
    model_header, model_widget,
    lora_header, lora_widget, lora_strength_widget,
    vae_header, vae_widget,
    controlnet_header, controlnet_widget,
    download_header, download_button,
    config_name_widget, save_config_widget
)
