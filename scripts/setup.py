# ~ setup.py | by ANXETY ~

# VERY EARLY SYS.PATH MODIFICATION FOR CRITICAL IMPORTS
import sys
from pathlib import Path
import os

_HOME_EARLY = Path.home()
_ANXETY_PATH_EARLY = _HOME_EARLY / 'ANXETY'
_MODULES_PATH_EARLY = _ANXETY_PATH_EARLY / 'modules'
_SCRIPTS_PATH_EARLY = _ANXETY_PATH_EARLY / 'scripts'

# Ensure the directories exist and are added to sys.path at the highest priority
_MODULES_PATH_EARLY.mkdir(parents=True, exist_ok=True)
_SCRIPTS_PATH_EARLY.mkdir(parents=True, exist_ok=True)

if str(_MODULES_PATH_EARLY) not in sys.path:
    sys.path.insert(0, str(_MODULES_PATH_EARLY))
if str(_SCRIPTS_PATH_EARLY) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_PATH_EARLY))
# END VERY EARLY SYS.PATH MODIFICATION


from IPython.display import display, HTML, clear_output
from urllib.parse import urljoin
from tqdm import tqdm
import nest_asyncio
import importlib
import argparse
import asyncio
import aiohttp
import time
import json


# Platform detection added for Lightning AI compatibility
# The definitions of os and Path are now imported at the very top via the early sys.path modification
# So we can proceed with using them directly without re-importing.

def detect_platform():
    try:
        import google.colab
        return 'colab'
    except ImportError:
        pass

    if os.path.exists('/kaggle'):
        return 'kaggle'

    if (
        os.environ.get('LIGHTNING_CLOUD_PROJECT_ID') or
        os.environ.get('LIGHTNING_AI') or
        os.path.exists('/teamspace') or
        'lightning' in os.environ.get('PWD', '').lower() or
        'studios' in os.environ.get('PWD', '').lower() or
        'lightning' in str(Path.home()).lower()
    ):
        return 'lightning'

    return 'local'

CURRENT_PLATFORM = detect_platform()
print(f"Setup script detected platform: {CURRENT_PLATFORM}")

# Constants
platform = os.environ.get('DETECTED_PLATFORM', 'local')
if platform == 'lightning':
    HOME = Path('/teamspace/studios/this_studio')
    if not HOME.exists():
        HOME = Path.home() / 'workspace'
        HOME.mkdir(parents=True, exist_ok=True)
elif platform == 'colab':
    HOME = Path.home()
elif platform == 'kaggle':
    HOME = Path('/kaggle/working')
else:
    HOME = Path.cwd()
SCR_PATH = HOME / 'ANXETY'
SETTINGS_PATH = SCR_PATH / 'settings.json'

# Removed setup_module_folder_early and global import of json_utils.js
# All necessary json operations are now inlined or use built-in json module

nest_asyncio.apply()  # Async support for Jupyter


# ===================== UTILITIES (JSON/FILE OPERATIONS) =====================

# Inlined key_exists logic (previously from json_utils)
def key_exists(filepath, key=None, value=None):
    """Check key/value in JSON file."""
    if not filepath.exists():
        return False
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return False

    if key:
        keys = key.split('.')
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return False
        return (data == value) if value else True
    return False

# This function is now the primary way to save/update settings for setup.py
def save_data_to_json_nested(filepath, key_path, value):
    """Save value to a JSON file at a nested key path, creating parent dictionaries as needed."""
    try:
        if Path(filepath).exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
        else:
            data = {}
    except json.JSONDecodeError:
        data = {} # Handle corrupted JSON

    keys = key_path.split('.')
    current_data = data
    for i, k in enumerate(keys):
        if i == len(keys) - 1: # Last key
            current_data[k] = value
        else:
            if k not in current_data or not isinstance(current_data[k], dict):
                current_data[k] = {}
            current_data = current_data[k]
    
    Path(filepath).parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)


def save_environment_to_json(SETTINGS_PATH, data):
    """Save environment data to a JSON file."""
    existing_data = {}

    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, 'r') as json_file:
                existing_data = json.load(json_file)
        except json.JSONDecodeError:
            existing_data = {} # Handle corrupted settings.json

    existing_data.update(data)

    with open(SETTINGS_PATH, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

def get_start_timer():
    """Get the start timer from settings or default to current time minus 5 seconds."""
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, 'r') as f:
                settings = json.load(f)
                return settings.get('ENVIRONMENT', {}).get('start_timer', int(time.time() - 5))
        except json.JSONDecodeError:
            return int(time.time() - 5) # Default if JSON is corrupt
    return int(time.time() - 5)


## ======================= MODULES =======================

def clear_module_cache(modules_folder):
    """Clear the module cache for modules in the specified folder."""
    for module_name in list(sys.modules.keys()):
        module = sys.modules[module_name]
        if hasattr(module, '__file__') and module.__file__ and module.__file__.startswith(str(modules_folder)):
            del sys.modules[module_name]
    importlib.invalidate_caches()

def setup_module_folder(scr_folder):
    """Set up the module folder by clearing the cache and adding it to sys.path.
    This function is kept for consistency with how modules are cleared/reloaded later.
    The initial path addition is now handled by `setup_module_folder_early`.
    """
    clear_module_cache(scr_folder)
    # The path should already be there from setup_module_folder_early, but this ensures it.
    modules_folder = scr_folder / 'modules'
    modules_folder.mkdir(parents=True, exist_ok=True)
    if str(modules_folder) not in sys.path:
        sys.path.append(str(modules_folder))


# ===================== ENVIRONMENT SETUP =====================

def detect_environment():
    """Detect runtime environment."""
    envs = {'COLAB_GPU': 'Google Colab', 'KAGGLE_URL_BASE': 'Kaggle'}
    for var, name in envs.items():
        if var in os.environ:
            return name
    # The original detect_environment function did not recognize Lightning AI.
    # The new environment_setup will handle the platform detection and optimization.
    # This original function is effectively bypassed if the new environment_setup is used.
    # For safety, I'll update it to include lightning detection.
    if (
        os.environ.get('LIGHTNING_CLOUD_PROJECT_ID') or
        os.environ.get('LIGHTNING_AI') or
        os.path.exists('/teamspace') or
        'lightning' in os.environ.get('PWD', '').lower() or
        'studios' in os.environ.get('PWD', '').lower() or
        'lightning' in str(Path.home()).lower()
    ):
        return 'Lightning AI' # Returning "Lightning AI" as a distinct environment

    raise EnvironmentError(f"Unsupported environment. Supported: {', '.join(envs.values())}")

def get_fork_info(fork_arg):
    """Parse fork argument into user/repo."""
    if not fork_arg:
        return 'anxety-solo', 'sdAIgen'
    parts = fork_arg.split('/', 1)
    return parts[0], (parts[1] if len(parts) > 1 else 'sdAIgen')

def create_environment_data(env, scr_folder, lang, fork_user, fork_repo, branch):
    """Create a dictionary with environment data."""
    install_deps = key_exists(SETTINGS_PATH, 'ENVIRONMENT.install_deps', True)
    start_timer = get_start_timer()

    return {
        'ENVIRONMENT': {
            'lang': lang,
            'fork': f"{fork_user}/{fork_repo}",
            'branch': branch,
            'env_name': env,
            'install_deps': install_deps,
            'home_path': str(HOME),
            'venv_path': str(HOME / 'venv'),
            'scr_path': str(scr_folder),
            'start_timer': start_timer,
            'public_ip': ''
        }
    }

# Replacing the environment_setup function entirely as per comprehensive_patches.md
def environment_setup():
    """Universal environment setup - works on all platforms"""
    import os
    from pathlib import Path

    # Universal platform detection
    def detect_platform_internal():
        """Detect current platform reliably"""
        try:
            import google.colab
            return 'colab'
        except ImportError:
            pass

        # Check for Kaggle
        if os.path.exists('/kaggle'):
            return 'kaggle'

        # Check for Lightning AI - comprehensive detection
        lightning_indicators = [
            os.environ.get('LIGHTNING_CLOUD_PROJECT_ID'),
            os.environ.get('LIGHTNING_AI'),
            os.path.exists('/teamspace'),
            'lightning' in os.environ.get('PWD', '').lower() or # Ensure exact match on 'lightning' in PWD for stricter detection
            'studios' in os.environ.get('PWD', '').lower() or # Ensure exact match on 'studios' in PWD
            'lightning' in str(Path.home()).lower()
        ]

        if any(lightning_indicators):
            return 'lightning'

        return 'local'

    # Set platform and export to environment
    platform = detect_platform_internal()
    os.environ['DETECTED_PLATFORM'] = platform
    print(f"🔍 Detected platform: {platform}")

    # Platform-specific base path setup
    if platform == 'lightning':
        # Lightning AI paths
        base_path = Path('/teamspace/studios/this_studio')
        if not base_path.exists():
            base_path = Path.home() / 'workspace'

        # Ensure base path exists
        base_path.mkdir(parents=True, exist_ok=True)

        # Create all required directories
        required_dirs = [
            'models', 'outputs', 'extensions', 'embeddings',
            'lora', 'vae', 'controlnet', 'config', 'logs',
            'temp', '.cache', 'ANXETY', 'ANXETY/scripts', 'sd_models_shared' # Added sd_models_shared
        ]

        for dir_name in required_dirs:
            dir_path = base_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)

        # Set Lightning AI optimizations
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
        os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
        os.environ['TMPDIR'] = str(base_path / 'temp') # Updated to use base_path
        os.environ['TEMP'] = str(base_path / 'temp') # Updated to use base_path

        # Create temp directory
        (base_path / 'temp').mkdir(parents=True, exist_ok=True) # Ensure it's under base_path

        return str(base_path)

    elif platform == 'colab':
        # Google Colab setup
        base_path = Path('/content')
        return str(base_path)

    elif platform == 'kaggle':
        # Kaggle setup
        base_path = Path('/kaggle/working')
        base_path.mkdir(parents=True, exist_ok=True)
        return str(base_path)

    else:
        # Local/other platforms
        base_path = Path.cwd()
        return str(base_path)


# Replacing the Google Drive Mount Section entirely as per comprehensive_patches.md
def setup_storage():
    """Platform-aware storage setup"""
    platform = os.environ.get('DETECTED_PLATFORM', 'local')

    if platform == 'colab':
        try:
            from google.colab import drive
            drive.mount('/content/drive')
            return Path('/content/drive/MyDrive')
        except Exception as e:
            print(f"Drive mount failed: {e}")
            return HOME

    elif platform == 'lightning':
        # Use persistent storage for Lightning AI
        persistent_path = HOME / 'persistent' # Using HOME here as it's already set to studio base_path
        persistent_path.mkdir(parents=True, exist_ok=True)
        return persistent_path

    elif platform == 'kaggle':
        # Kaggle doesn't have persistent storage
        return HOME

    else:
        return HOME

DRIVE_PATH = setup_storage() # Assigning the result of setup_storage to DRIVE_PATH
# Fix: Save DRIVE_PATH to settings.json so other scripts can access it
save_data_to_json_nested(SETTINGS_PATH, 'ENVIRONMENT.gdrive_path', str(DRIVE_PATH))


## ======================= DOWNLOAD LOGIC =====================

def generate_file_list(structure, base_url, base_path):
    """Generate flat list of (url, path) from nested structure"""
    def walk(struct, path_parts):
        items = []
        for key, value in struct.items():
            current_path = [*path_parts, key] if key else path_parts
            if isinstance(value, dict):
                items.extend(walk(value, current_path))
            else:
                url_path = '/'.join(current_path)
                for file in value:
                    url = f"{base_url}/{url_path}/{file}" if url_path else f"{base_url}/{file}"
                    file_path = base_path / '/'.join(current_path) / file
                    items.append((url, file_path))
        return items

    return walk(structure, [])

async def download_file(session, url, path):
    """Download and save single file with error handling"""
    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            content = await resp.read()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            return (True, url, path, None)
    except aiohttp.ClientResponseError as e:
        return (False, url, path, f"HTTP error {e.status}: {e.message}")
    except Exception as e:
        return (False, url, path, f"Error: {str(e)}")

async def download_files_async(scr_path, lang, fork_user, fork_repo, branch, log_errors):
    """Main download executor with error logging"""
    files_structure = {
        'CSS': ['main-widgets.css', 'download-result.css', 'auto-cleaner.css'],
        'JS': ['main-widgets.js'],
        'modules': ['json_utils.py', 'webui_utils.py', 'widget_factory.py',
                   'TunnelHub.py', 'CivitaiAPI.py', 'Manager.py', '__season.py'],
        'scripts': {
            'UIs': ['A1111.py', 'ComfyUI.py', 'Forge.py', 'Classic.py', 'ReForge.py', 'SD-UX.py'],
            lang: [f"widgets-{lang}.py", f"downloading-{lang}.py"],
            '': ['launch.py', 'auto-cleaner.py', 'download-result.py',
                '_models-data.py', '_xl-models-data.py', '_loras-data.py'] # Added _loras-data.py
        }
    }

    base_url = f"https://raw.githubusercontent.com/{fork_user}/{fork_repo}/{branch}"
    file_list = generate_file_list(files_structure, base_url, scr_path)

    async with aiohttp.ClientSession() as session:
        tasks = [download_file(session, url, path) for url, path in file_list]

        errors = []
        futures = asyncio.as_completed(tasks)
        for future in tqdm(futures, total=len(tasks), desc="Downloading files", unit="file"):
            result = await future
            success, url, path, error = result
            if not success:
                errors.append((url, path, error))

        clear_output()

        if log_errors and errors:
            print("\nErrors occurred during download:")
            for url, path, error in errors:
                print(f"URL: {url}")
                print(f"Path: {path}")
                print(f"Error: {error}\n")


# ===================== MAIN EXECUTION =====================

async def main_async(args=None):
    """Entry point."""
    parser = argparse.ArgumentParser(description='ANXETY Download Manager')
    parser.add_argument('-l', '--lang', type=str, default='en', help='Language to be used (default: en)')
    parser.add_argument('-b', '--branch', type=str, default='main', help='Branch to download files from (default: main)')
    parser.add_argument('-f', '--fork', type=str, default=None, help='Specify project fork (user or user/repo)')
    parser.add_argument('-s', '--skip-download', action='store_true', help='Skip downloading files and just update the directory and modules')
    parser.add_argument('-L', '--log', action='store_true', help='Enable logging of download errors')

    args, _ = parser.parse_known_args(args)

    env = detect_environment() # Keep this call as is, as it's used for display_info
    user, repo = get_fork_info(args.fork)   # gitLogin , gitRepoName

    if not args.skip_download:
        await download_files_async(SCR_PATH, args.lang, user, repo, args.branch, args.log)    # download scripts files

    setup_module_folder(SCR_PATH)   # setup main dir -> modules

    env_data = create_environment_data(env, SCR_PATH, args.lang, user, repo, args.branch)
    save_environment_to_json(SETTINGS_PATH, env_data)

    # display info text | MODULES
    from __season import display_info

    display_info(
        env=env,
        scr_folder=str(SCR_PATH),
        branch=args.branch,
        lang=args.lang,
        fork=args.fork
    )

if __name__ == '__main__':
    asyncio.run(main_async())
