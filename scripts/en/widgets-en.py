import os
import sys
import ast
from IPython.display import display

# Define paths relative to the script location
# This makes the script more portable
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.abspath(os.path.join(SCRIPTS_DIR, '../../modules'))
sys.path.append(MODULES_DIR)

# Correctly import from ipywidgets and widget_factory
from ipywidgets import widgets, Layout
from widget_factory import WidgetFactory


# =================================================================================
# == HELPER FUNCTION TO READ AND COMBINE DATA FROM NEW SCRIPT FILES
# =================================================================================
def read_and_combine_data(file_map):
    """
    Reads multiple data files, executes them, and combines keys from specified dictionaries.
    Example file_map:
    {
        "sd15_models_file.py": ["sd15_model_data", "sd15_vae_data"],
        "loras_file.py": ["lora_data"]
    }
    """
    all_options = []
    
    for file_path, dict_names in file_map.items():
        # Correct the path to be absolute based on the scripts directory
        absolute_file_path = os.path.abspath(os.path.join(SCRIPTS_DIR, '..', file_path))
        
        try:
            with open(absolute_file_path, 'r', encoding='utf-8') as f:
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
            print(f"Warning: Data file not found at {absolute_file_path}. Skipping.")
        except Exception as e:
            print(f"Error reading {absolute_file_path}: {e}")
            
    # Remove duplicates and sort
    return sorted(list(set(all_options)))

# =================================================================================
# == MAIN WIDGET CREATION
# =================================================================================

# Create a factory instance
factory = WidgetFactory()

# --- Define File Paths ---
# Paths are relative to the 'scripts' directory where this file should be
SD15_MODELS_FILE = '_sd15_models-data.py'
SDXL_MODELS_FILE = '_sdxl_models-data.py'
LORAS_FILE = '_loras-data.py'

# --- Read and Combine Data for Widgets ---
model_map = {
    SD15_MODELS_FILE: ["sd15_model_data"],
    SDXL_MODELS_FILE: ["sdxl_models_data"]
}
model_options = read_and_combine_data(model_map)

lora_map = {
    LORAS_FILE: ["lora_data"]
}
lora_options = read_and_combine_data(lora_map)

vae_map = {
    SD15_MODELS_FILE: ["sd15_vae_data"],
    SDXL_MODELS_FILE: ["sdxl_vae_data"]
}
vae_options = read_and_combine_data(vae_map)

# --- Create Widgets using the combined data ---
# Use the first item in the list as a safe default, or provide a placeholder if the list is empty

# Model Widgets
model_header = factory.create_header('Model Selection')
model_default = model_options[0] if model_options else None
model_widget = factory.create_dropdown(model_options, 'Model:', model_default, 'No models found')
model_num_widget = factory.create_text('Model Number:', '', 'Enter model numbers for download.')
inpainting_model_widget = factory.create_checkbox('Inpainting Models', False, class_names=['inpaint'], layout={'width': '25%'})

# LoRA Widgets
lora_header = factory.create_header('LoRA Selection')
lora_default = lora_options[0] if lora_options else None
lora_widget = factory.create_dropdown(lora_options, 'LoRA:', lora_default, 'No LoRAs found')
lora_num_widget = factory.create_text('LoRA Number:', '', 'Enter LoRA numbers for download.')
lora_strength_widget = factory.create_slider(0.7, 0, 1, 'LoRA Strength:', class_names=['lora-strength'])

# VAE Widgets
vae_header = factory.create_header('VAE Selection')
vae_default = vae_options[0] if vae_options else None
vae_widget = factory.create_dropdown(vae_options, 'VAE:', vae_default, 'No VAEs found')

# ControlNet Widgets
controlnet_header = factory.create_header('ControlNet Selection')
controlnet_options = ['Canny', 'Depth', 'Lineart', 'Normalbae', 'Openpose', 'Scribble', 'Seg', 'Softedge', 'Tile']
controlnet_widget = factory.create_multiselect(controlnet_options, 'ControlNet Models:', ['Canny', 'Depth'])

# Additional Options
additional_options_header = factory.create_header('Additional Options')
resolution_widget = factory.create_text('Resolution:', '512x768', 'e.g. 512x768')
config_name_widget = factory.create_text('Config Name:', '', 'e.g. my-config')
save_config_widget = factory.create_button('Save Config', 'success', 'floppy-o', class_names=['save-button'])

# Display all widgets
display(
    model_header, model_widget, model_num_widget, inpainting_model_widget,
    lora_header, lora_widget, lora_num_widget, lora_strength_widget,
    vae_header, vae_widget,
    controlnet_header, controlnet_widget,
    additional_options_header, resolution_widget, config_name_widget, save_config_widget
)
