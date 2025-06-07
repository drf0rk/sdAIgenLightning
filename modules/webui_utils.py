""" WebUI Utils Module | by ANXETY """

import json_utils as js    # JSON

from pathlib import Path
import os


# Constants
HOME = Path.home()
SCR_PATH = HOME / 'ANXETY'
SETTINGS_PATH = SCR_PATH / 'settings.json'

WEBUI_PATHS = {
    'A1111': (
        'Stable-diffusion', 'VAE', 'Lora',
        'embeddings', 'extensions', 'ESRGAN', 'outputs'
    ),
    'ComfyUI': (
        'checkpoints', 'vae', 'loras',
        'embeddings', 'custom_nodes', 'upscale_models', 'output'
    ),
    'Classic': (
        'Stable-diffusion', 'VAE', 'Lora',
        'embeddings', 'extensions', 'ESRGAN', 'output'
    )
}

DEFAULT_UI = 'A1111'

# New: Define a centralized base directory for all shared models
SHARED_MODEL_BASE = HOME / 'sd_models_shared'


def update_current_webui(current_value):
    """Update the current WebUI value and save settings."""
    current_stored = js.read(SETTINGS_PATH, 'WEBUI.current')
    latest_value = js.read(SETTINGS_PATH, 'WEBUI.latest', None)

    if latest_value is None or current_stored != current_value:
        js.save(SETTINGS_PATH, 'WEBUI.latest', current_stored)
        js.save(SETTINGS_PATH, 'WEBUI.current', current_value)

    js.save(SETTINGS_PATH, 'WEBUI.webui_path', str(HOME / current_value))
    _set_webui_paths(current_value)

def _set_webui_paths(ui):
    """Configure paths for specified UI, fallback to A1111 for unknown UIs"""
    selected_ui = ui if ui in WEBUI_PATHS else DEFAULT_UI
    webui_root = HOME / ui
    
    # NEW: All model-related paths will now point to subdirectories under SHARED_MODEL_BASE
    models_root = SHARED_MODEL_BASE 
    os.makedirs(models_root, exist_ok=True) # Ensure shared base exists

    # Get path components for selected UI (these are now mostly logical names)
    paths = WEBUI_PATHS[selected_ui]
    checkpoint_subdir, vae_subdir, lora_subdir, embed_subdir, extension_subdir, upscale_subdir, output_subdir = paths

    # Adjust subdirectory names for shared storage based on UI type, ensuring consistent naming
    # These effectively standardize paths under SHARED_MODEL_BASE
    actual_checkpoint_subdir = 'checkpoints' if is_comfy else 'Stable-diffusion'
    actual_vae_subdir = 'vae'
    actual_lora_subdir = 'loras' if is_comfy else 'Lora'
    actual_embed_subdir = 'embeddings'
    actual_control_subdir = 'controlnet' if is_comfy else 'ControlNet'
    actual_upscale_subdir = 'upscale_models' if is_comfy else 'ESRGAN'
    actual_adetailer_subdir = 'ultralytics' if is_comfy else 'adetailer'
    actual_clip_subdir = 'clip' if is_comfy else 'text_encoder'
    actual_unet_subdir = 'unet' if is_comfy else 'unet' # Unet dir for both
    actual_vision_subdir = 'clip_vision'
    actual_encoder_subdir = 'text_encoders' if is_comfy else 'text_encoder'
    actual_diffusion_subdir = 'diffusion_models'

    path_config = {
        'model_dir': str(models_root / actual_checkpoint_subdir),
        'vae_dir': str(models_root / actual_vae_subdir),
        'lora_dir': str(models_root / actual_lora_subdir),
        'embed_dir': str(models_root / actual_embed_subdir),
        'control_dir': str(models_root / actual_control_subdir),
        'upscale_dir': str(models_root / actual_upscale_subdir),
        'adetailer_dir': str(models_root / actual_adetailer_subdir),
        'clip_dir': str(models_root / actual_clip_subdir),
        'unet_dir': str(models_root / actual_unet_subdir),
        'vision_dir': str(models_root / actual_vision_subdir),
        'encoder_dir': str(models_root / actual_encoder_subdir),
        'diffusion_dir': str(models_root / actual_diffusion_subdir),
        
        # Extensions and outputs usually remain UI-specific
        'extension_dir': str(webui_root / extension_subdir),
        'output_dir': str(webui_root / output_subdir),
        'config_dir': str(webui_root / ('user/default' if is_comfy else '')) # ComfyUI has a specific user/default config path
    }

    # Ensure all new shared directories exist
    for key, path_str in path_config.items():
        if '_dir' in key and 'extension_dir' not in key and 'output_dir' not in key and 'config_dir' not in key:
            Path(path_str).mkdir(parents=True, exist_ok=True)
            
    js.update(SETTINGS_PATH, 'WEBUI', path_config)

def handle_setup_timer(webui_path, timer_webui):
    """Manage timer persistence for WebUI instances."""
    timer_file = Path(webui_path) / 'static' / 'timer.txt'
    timer_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with timer_file.open('r') as f:
            timer_webui = float(f.read())
    except FileNotFoundError:
        pass

    with timer_file.open('w') as f:
        f.write(str(timer_webui))

    return timer_webui
