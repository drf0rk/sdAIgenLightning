# ~ download.py | by ANXETY ~ (All-in-One Fix)

from webui_utils import handle_setup_timer
from CivitaiAPI import CivitAiAPI
from Manager import m_download
import json_utils as js

from IPython.display import clear_output
from pathlib import Path
import subprocess
import shlex
import time
import json
import sys
import re
import os

# --- Setup & Constants ---
DOWNLOADER_VERSION = "2025.06.09.8_final_patch"
CD = os.chdir
HOME = Path(js.read(os.path.join(Path.home(), 'ANXETY', 'settings.json'), 'ENVIRONMENT.home_path', str(Path.home())))
SCR_PATH = HOME / 'ANXETY'
SCRIPTS = SCR_PATH / 'scripts'
SETTINGS_PATH = SCR_PATH / 'settings.json'

class COLORS: R,G,Y,B,lB,X = "\033[31m","\033[32m","\033[33m","\033[34m","\033[36;1m","\033[0m"
COL = COLORS

print(f"✨ Downloader Version: {DOWNLOADER_VERSION}")

# --- Load Settings ---
settings = js.read(SETTINGS_PATH)
env_settings = settings.get('ENVIRONMENT', {})
widget_settings = settings.get('WIDGETS', {})
webui_settings = settings.get('WEBUI', {})

# Explicitly load widget values
XL_models = widget_settings.get('XL_models', False)
inpainting_model = widget_settings.get('inpainting_model', False)
model_selections = widget_settings.get('model', ('none',))
vae_selections = widget_settings.get('vae', ('none',))
lora_selections = widget_settings.get('lora', ('none',))
controlnet_selections = widget_settings.get('controlnet', ('none',))
latest_webui = widget_settings.get('latest_webui', True)
latest_extensions = widget_settings.get('latest_extensions', True)

# Path Definitions
model_dir = Path(webui_settings.get('model_dir'))
vae_dir = Path(webui_settings.get('vae_dir'))
lora_dir = Path(webui_settings.get('lora_dir'))
control_dir = Path(webui_settings.get('control_dir'))
extension_dir = Path(webui_settings.get('extension_dir'))
WEBUI_PATH = Path(webui_settings.get('webui_path'))

# --- Data Loading ---
model_files_path = SCRIPTS / ('_xl-models-data.py' if XL_models else '_models-data.py')
with open(model_files_path, 'r', encoding='utf-8') as f: exec(f.read(), globals())

loras_data_path = SCRIPTS / '_loras-data.py'
with open(loras_data_path, 'r', encoding='utf-8') as f: exec(f.read(), globals())

model_list = sdxl_models_data if XL_models else sd15_model_data
vae_list = sdxl_vae_data if XL_models else sd15_vae_data
lora_list_to_use = lora_data.get('sdxl_loras', {}) if XL_models else lora_data.get('sd15_loras', {})

# --- Download Logic ---
def handle_submodels(selections, model_dict, dst_dir, inpainting=False):
    download_list = []
    if not isinstance(selections, (list, tuple)): return download_list
    
    cleaned_selections = [re.sub(r'^\d+\.\s*', '', sel) for sel in selections]
    
    for selection_name in cleaned_selections:
        if selection_name in ['none']: continue
        if selection_name == 'ALL':
            for model_group in model_dict.values():
                if isinstance(model_group, list):
                    for item in model_group:
                         download_list.append(f"\"{item['url']}\" \"{dst_dir}\" \"{item.get('name')}\"")
            continue
        
        if selection_name in model_dict:
            model_group = model_dict[selection_name]
            if isinstance(model_group, list):
                 for model_info in model_group:
                    name = model_info.get('name') or os.path.basename(model_info['url'])
                    if not inpainting and "inpainting" in name.lower():
                        continue
                    download_list.append(f"\"{model_info['url']}\" \"{dst_dir}\" \"{name}\"")
    return download_list

# --- Main Execution ---
if latest_webui or latest_extensions:
    action = 'WebUI and Extensions' if latest_webui and latest_extensions else ('WebUI' if latest_webui else 'Extensions')
    print(f"⌚️ Updating {action}...")
    subprocess.run(['git', 'config', '--global', 'user.email', 'you@example.com'], capture_output=True)
    subprocess.run(['git', 'config', '--global', 'user.name', 'Your Name'], capture_output=True)
    if latest_webui:
        subprocess.run(['git', '-C', str(WEBUI_PATH), 'pull'], capture_output=True)
    if latest_extensions:
        for entry in os.listdir(str(extension_dir)):
            dir_path = os.path.join(str(extension_dir), entry)
            if os.path.isdir(dir_path) and os.path.exists(os.path.join(dir_path, '.git')):
                subprocess.run(['git', '-C', str(dir_path), 'pull'], capture_output=True)
    print(f"✨ Update {action} Completed!")

print('📦 Processing download selections...')
line_entries = []
line_entries.extend(handle_submodels(model_selections, model_list, model_dir, inpainting_model))
line_entries.extend(handle_submodels(vae_selections, vae_list, vae_dir))
line_entries.extend(handle_submodels(lora_selections, lora_list_to_use, lora_dir))
line_entries.extend(handle_submodels(controlnet_selections, controlnet_list, control_dir))

download_line = ', '.join(line_entries)

if download_line:
    print("Starting downloads...")
    m_download(download_line, log=True)
else:
    print("No models selected for download.")

print('\r🏁 Download processing complete!')
