# ~ download.py | by ANXETY ~

from webui_utils import handle_setup_timer, _set_webui_paths # WEBUI # ADDED _set_webui_paths
from CivitaiAPI import CivitAiAPI             # CivitAI API
from Manager import m_download                # Every Download
import json_utils as js                       # JSON

from IPython.display import clear_output
from IPython.utils import capture
from urllib.parse import urlparse
from IPython import get_ipython
from datetime import timedelta
from pathlib import Path
import subprocess
import requests
import zipfile
import shutil
import shlex
import time
import json
import sys
import re 
import os 
from tqdm import tqdm 


# Platform-aware downloading configuration
PLATFORM = os.environ.get('DETECTED_PLATFORM', 'local')

def get_download_config():
    """Get platform-specific download settings"""
    if PLATFORM == 'lightning':
        return {
            'base_path': '/teamspace/studios/this_studio',
            'temp_path': '/tmp/sdaigen',
            'max_concurrent': 2,        # Conservative for Lightning AI
            'chunk_size': 1024 * 1024,  # 1MB chunks
            'timeout': 300,
            'retries': 3,
            'verify_ssl': True,
            'use_aria2': False          # Avoid additional dependencies
        }
    elif PLATFORM == 'colab':
        return {
            'base_path': '/content',
            'temp_path': '/tmp',
            'max_concurrent': 4,
            'chunk_size': 8 * 1024 * 1024,  # 8MB chunks
            'timeout': 600,
            'retries': 2,
            'verify_ssl': True,
            'use_aria2': True
        }
    elif PLATFORM == 'kaggle':
        return {
            'base_path': '/kaggle/working',
            'temp_path': '/kaggle/tmp',
            'max_concurrent': 3,
            'chunk_size': 4 * 1024 * 1024,  # 4MB chunks
            'timeout': 450,
            'retries': 2,
            'verify_ssl': True,
            'use_aria2': False
        }
    else:
        return {
            'base_path': os.getcwd(),
            'temp_path': './temp',
            'max_concurrent': 4,
            'chunk_size': 8 * 1024 * 1024,
            'timeout': 600,
            'retries': 2,
            'verify_ssl': True,
            'use_aria2': False
        }

# Apply configuration
DOWNLOAD_CONFIG = get_download_config()

# Ensure directories exist
os.makedirs(DOWNLOAD_CONFIG['base_path'], exist_ok=True)
os.makedirs(DOWNLOAD_CONFIG['temp_path'], exist_ok=True)


CD = os.chdir
ipySys = get_ipython().system
ipyRun = get_ipython().run_line_magic

# Constants (updated to use the new DOWNLOAD_CONFIG paths where applicable)
HOME = Path(DOWNLOAD_CONFIG['base_path'])
VENV = Path(DOWNLOAD_CONFIG['base_path']) / 'venv' # Assuming venv is usually inside base_path
SCR_PATH = Path(HOME / 'ANXETY') # Assuming ANXETY scripts are always relative to HOME
SCRIPTS = SCR_PATH / 'scripts'
SETTINGS_PATH = SCR_PATH / 'settings.json'

LANG = js.read(SETTINGS_PATH, 'ENVIRONMENT.lang')
ENV_NAME = js.read(SETTINGS_PATH, 'ENVIRONMENT.env_name')
# Provide a default value for UI if 'WEBUI.current' is not found or is None
UI = js.read(SETTINGS_PATH, 'WEBUI.current', 'A1111') 
WEBUI = js.read(SETTINGS_PATH, 'WEBUI.webui_path', str(HOME / 'webui')) 


# Text Colors (\033)
class COLORS:
    R  =  "\033[31m"     # Red
    G  =  "\033[32m"     # Green
    Y  =  "\033[33m"     # Yellow
    B  =  "\033[34m"     # Blue
    lB =  "\033[36;1m"   # lightBlue
    X  =  "\033[0m"      # Reset

COL = COLORS


## =================== LIBRARIES | VENV ==================

def install_dependencies(commands):
    """Run a list of installation commands."""
    for cmd in commands:
        try:
            subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

def setup_venv(url):
    """Customize the virtual environment using the specified URL."""
    CD(HOME)
    fn = Path(url).name

    m_download(f"{url} {HOME} {fn}")

    # Install dependencies based on environment
    install_commands = []
    if ENV_NAME == 'Kaggle':
        install_commands.extend([
            'pip install ipywidgets jupyterlab_widgets --upgrade',
            'rm -f /usr/lib/python3.10/sitecustomize.py'
        ])

    install_commands.append('sudo apt-get -y install lz4 pv')
    install_dependencies(install_commands)

    # Unpack and clean
    ipySys(f"pv {fn} | lz4 -d | tar xf -")
    Path(fn).unlink()

    BIN = str(VENV / 'bin')
    PKG = str(VENV / 'lib/python3.10/site-packages')

    os.environ['PYTHONWARNINGS'] = 'ignore'

    sys.path.insert(0, PKG)
    # Fix: Safely get PYTHONPATH, defaulting to empty string if not set
    if PKG not in os.environ.get('PYTHONPATH', ''):
        os.environ['PYTHONPATH'] = PKG + ':' + os.environ.get('PYTHONPATH', '')

def install_packages(install_lib):
    """Install packages from the provided library dictionary."""
    for index, (package, install_cmd) in enumerate(install_lib.items(), start=1):
        print(f"\r[{index}/{len(install_lib)}] {COL.G}>>{COL.X} Installing {COL.Y}{package}{COL.X}..." + ' ' * 35, end='')
        try:
            result = subprocess.run(install_cmd, shell=True, capture_output=True)
            if result.returncode != 0:
                print(f"\n{COL.R}Error installing {package}{COL.X}")
        except Exception:
            pass

# Check and install dependencies
if not js.key_exists(SETTINGS_PATH, 'ENVIRONMENT.install_deps', True):
    install_lib = {
        ## Libs
        'aria2': "pip install aria2",
        'gdown': "pip install gdown",
        ## Tunnels
        'localtunnel': "npm install -g localtunnel",
        'cloudflared': "wget -qO /usr/bin/cl https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64; chmod +x /usr/bin/cl",
        'zrok': "wget -qO zrok_1.0.4_linux_amd64.tar.gz https://github.com/openziti/zrok/releases/download/v1.0.4/zrok_1.0.4_linux_amd64_amd64.tar.gz; tar -xzf zrok_1.0.4_linux_amd64.tar.gz -C /usr/bin; rm -f zrok_1.0.4_linux_amd64.tar.gz",
        'ngrok': "wget -qO ngrok-v3-stable-linux-amd64.tgz https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz; tar -xzf ngrok-v3-stable-linux-amd64.tgz -C /usr/bin; rm -f ngrok-v3-stable-linux-amd64.tgz"
    }

    print('💿 Installing the libraries will take a bit of time.')
    install_packages(install_lib)
    clear_output()
    js.update(SETTINGS_PATH, 'ENVIRONMENT.install_deps', True)

# Install VENV
current_ui = js.read(SETTINGS_PATH, 'WEBUI.current')
latest_ui = js.read(SETTINGS_PATH, 'WEBUI.latest')

# Determine whether to reinstall venv
venv_needs_reinstall = (
    not VENV.exists()  # venv is missing
    # Check category change (Classic <-> other)
    or (latest_ui == 'Classic') != (current_ui == 'Classic')
)

if venv_needs_reinstall:
    if VENV.exists():
        print("🗑️ Remove old venv...")
        shutil.rmtree(VENV)
        clear_output()

    if current_ui == 'Classic':
        venv_url = "https://huggingface.co/NagisaNao/ANXETY/resolve/main/python31112-venv-torch251-cu121-C-Classic.tar.lz4"
        py_version = '(3.11.12)'
    else:
        venv_url = "https://huggingface.co/NagisaNao/ANXETY/resolve/main/python31017-venv-torch251-cu121-C-fca.tar.lz4"
        py_version = '(3.10.17)'

    print(f"♻️ Installing VENV {py_version}, this will take some time...")
    setup_venv(venv_url)
    clear_output()

    # Update latest UI version...
    js.update(SETTINGS_PATH, 'WEBUI.latest', current_ui)

## ================ loading settings V5 ==================

def load_settings(path):
    """Load settings from a JSON file."""
    try:
        return {
            **js.read(path, 'ENVIRONMENT', {}),
            **js.read(path, 'WIDGETS', {}),
            **js.read(path, 'WEBUI', {})
        }
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading settings: {e}")
        return {}

# Load settings
settings = load_settings(SETTINGS_PATH)
locals().update(settings)

# Force update WEBUI paths based on current UI selection.
print(f"🔄 Ensuring WebUI paths are configured for {UI}...")
_set_webui_paths(UI) 

# Re-load settings after forcing _set_webui_paths to ensure the latest paths are used.
settings = load_settings(SETTINGS_PATH)
locals().update(settings)


# Fix: Retrieve DRIVE_PATH from settings, defaulting to HOME if not found
DRIVE_PATH = Path(settings.get('gdrive_path', str(HOME)))

# Populate model/asset directories from settings.json (paths set by webui_utils.py)
webui_settings = settings.get('WEBUI', {})

model_dir = Path(webui_settings.get('model_dir', str(HOME / 'models')))
vae_dir = Path(webui_settings.get('vae_dir', str(HOME / 'vae')))
lora_dir = Path(webui_settings.get('lora_dir', str(HOME / 'lora')))
embed_dir = Path(webui_settings.get('embed_dir', str(HOME / 'embeddings')))
extension_dir = Path(webui_settings.get('extension_dir', str(HOME / 'extensions')))
control_dir = Path(webui_settings.get('control_dir', str(HOME / 'ControlNet')))
upscale_dir = Path(webui_settings.get('upscale_dir', str(HOME / 'upscale_models')))
output_dir = Path(webui_settings.get('output_dir', str(HOME / 'outputs')))
config_dir = Path(webui_settings.get('config_dir', str(HOME / 'config')))
adetailer_dir = Path(webui_settings.get('adetailer_dir', str(HOME / 'adetailer')))
clip_dir = Path(webui_settings.get('clip_dir', str(HOME / 'clip')))
unet_dir = Path(webui_settings.get('unet_dir', str(HOME / 'unet')))
vision_dir = Path(webui_settings.get('vision_dir', str(HOME / 'vision')))
encoder_dir = Path(webui_settings.get('encoder_dir', str(HOME / 'encoder')))
diffusion_dir = Path(webui_settings.get('diffusion_dir', str(HOME / 'diffusion_models')))


# NEW: Platform-aware download functions (moved here to ensure they are defined before first use)
def download_file_platform_aware(url, destination, description="Downloading"):
    """Platform-aware file download with optimizations"""
    import requests
    from tqdm import tqdm

    config = DOWNLOAD_CONFIG

    try:
        # Create destination directory
        Path(destination).parent.mkdir(parents=True, exist_ok=True)

        # Download with platform-specific settings
        response = requests.get(
            url,
            stream=True,
            timeout=config['timeout'],
            verify=config['verify_ssl']
        )
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        with open(destination, 'wb') as file, tqdm(
            desc=description,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=config['chunk_size']):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))

        return True

    except Exception as e:
        print(f"Download failed: {e}")
        return False

def download_model_platform_aware(model_info):
    """Download model with platform-specific optimizations"""
    model_name = model_info['name']
    model_url = model_info['url']

    # Use platform-specific model directory
    destination = model_dir / model_name

    print(f"📥 Downloading {model_name} to {destination}")

    if download_file_platform_aware(model_url, destination, f"Downloading {model_name}"):
        print(f"✅ Successfully downloaded {model_name}")
        return True
    else:
        print(f"❌ Failed to download {model_name}")
        return False


## ======================== WEBUI ========================

if UI in ['A1111', 'SD-UX'] and not os.path.exists(Path(HOME) / '.cache/huggingface/hub/models--Bingsu--adetailer'): # Updated path
    print('🚚 Unpacking ADetailer model cache...')

    name_zip = 'hf_cache_adetailer'
    chache_url = 'https://huggingface.co/NagisaNao/ANXETY/resolve/main/hf_chache_adetailer.zip'

    zip_path = f"{HOME}/{name_zip}.zip"
    # Using the new platform-aware download function
    download_file_platform_aware(chache_url, Path(zip_path))
    ipySys(f"unzip -q -o {zip_path} -d /")
    ipySys(f"rm -rf {zip_path}")

    clear_output()

start_timer = js.read(SETTINGS_PATH, 'ENVIRONMENT.start_timer')

if not os.path.exists(WEBUI):
    start_install = time.time()
    print(f"⌚ Unpacking Stable Diffusion... | WEBUI: {COL.B}{UI}{COL.X}", end='')

    ipyRun('run', f"{SCRIPTS}/UIs/{UI}.py")
    handle_setup_timer(WEBUI, start_timer)		# Setup timer (for timer-extensions)

    install_time = time.time() - start_install
    minutes, seconds = divmod(int(install_time), 60)
    print(f"\r🚀 Unpacking {COL.B}{UI}{COL.X} is complete! {minutes:02}:{seconds:02} ⚡" + ' '*25)

else:
    print(f"🔧 Current WebUI: {COL.B}{UI}{COL.X}")
    print('🚀 Unpacking is complete. Pass. ⚡')

    timer_env = handle_setup_timer(WEBUI, start_timer)
    elapsed_time = str(timedelta(seconds=time.time() - timer_env)).split('.')[0]
    print(f"⌚️ Session duration: {COL.Y}{elapsed_time}{COL.X}")


## Changes extensions and WebUi
if latest_webui or latest_extensions:
    action = 'WebUI and Extensions' if latest_webui and latest_extensions else ('WebUI' if latest_webui else 'Extensions')
    print(f"⌚️ Update {action}...", end='')
    # Fix: Corrected indentation for git commands
    ipySys('git config --global user.email "you@example.com"')
    ipySys('git config --global user.name "Your Name"')

    ## Update Webui
    if latest_webui:
        CD(WEBUI)
        print("Updating WebUI repository...")
        subprocess.run(['git', 'stash', 'push', '--include-untracked'], check=False, capture_output=False) 
        subprocess.run(['git', 'pull', '--rebase'], check=False, capture_output=False) 
        subprocess.run(['git', 'stash', 'pop'], check=False, capture_output=False) 

    ## Update extensions
    if latest_extensions:
        print("Updating extensions...")
        for entry in os.listdir(f"{WEBUI}/extensions"):
            dir_path = f"{WEBUI}/extensions/{entry}"
            if os.path.isdir(dir_path):
                print(f"  Updating extension: {entry}")
                subprocess.run(['git', 'reset', '--hard'], cwd=dir_path, check=False)
                subprocess.run(['git', 'pull'], cwd=dir_path, check=False)

    print(f"\r✨ Update {action} Completed!")


# === FIXING EXTENSIONS ===
with capture.capture_output():
    # --- Umi-Wildcard ---
    ipySys(f"sed -i '521s/open=\\(False\\|True\\)/open=False/' {WEBUI}/extensions/Umi-AI-Wildcards/scripts/wildcard_recursive.py")    # Closed accordion by default


## Version switching
if commit_hash:
    print('🔄 Switching to the specified version...', end='')
    with capture.capture_output():
        CD(WEBUI)
        ipySys('git config --global user.email "you@example.com"')
        ipySys('git config --global user.name "Your Name"')
        ipySys('git reset --hard {commit_hash}')
        ipySys('git pull origin {commit_hash}')    # Get last changes in branch
    print(f"\r🔄 Switch complete! Current commit: {COL.B}{commit_hash}{COL.X}")


# Configuration
GD_BASE = str(DRIVE_PATH) 
SYMLINK_CONFIG = [
    {   # model
        'local_dir': model_dir, 
        'gdrive_subpath': 'Checkpoints',
    },
    {   # vae
        'local_dir': vae_dir, 
        'gdrive_subpath': 'VAE',
    },
    {   # lora
        'local_dir': lora_dir, 
        'gdrive_subpath': 'Lora',
    }
]

def create_symlink(src_path, gdrive_path, log=False):
    """Create symbolic link with content migration and cleanup"""
    try:
        src_exists = os.path.exists(src_path)
        is_real_dir = src_exists and os.path.isdir(src_path) and not os.path.islink(src_path)

        # Handle real directory migration
        if is_real_dir and os.path.exists(gdrive_path):
            for item in os.listdir(src_path):
                src_item = os.path.join(src_path, item)
                dst_item = os.path.join(gdrive_path, item)

                if os.path.exists(dst_item):
                    shutil.rmtree(dst_item) if os.path.isdir(dst_item) else os.remove(dst_item)
                shutil.move(src_item, dst_item)

            shutil.rmtree(src_path)
            if log:
                print(f"Moved contents from {src_path} to {gdrive_path}")

        # Cleanup existing path
        if os.path.exists(src_path) and not is_real_dir:
            if os.path.islink(src_path):
                os.unlink(src_path)
            else:
                os.remove(src_path)

        # Create new symlink
        if not os.path.exists(src_path):
            os.symlink(gdrive_path, src_path)
            if log:
                print(f"Created symlink: {src_path} → {gdrive_path}")

    except Exception as e:
        print(f"Error processing {src_path}: {str(e)}")

# Get XL or 1.5 models list
## model_list | vae_list | controlnet_list
model_files = '_xl-models-data.py' if XL_models else '_models-data.py'
with open(f"{SCRIPTS}/{model_files}") as f:
    exec(f.read())

# New: Load _loras-data.py to make lora_data available
try:
    with open(f"{SCRIPTS}/_loras-data.py") as f:
        lora_data_content = f.read()
    exec(lora_data_content, globals(), globals()) 
except FileNotFoundError:
    print(f"Error: _loras-data.py not found at {SCRIPTS}/_loras-data.py. Please ensure it is downloaded.")
    lora_data = {"sd15_loras": {}, "sdxl_loras": {}} 
except Exception as e:
    print(f"Error loading _loras-data.py: {e}")
    lora_data = {"sd15_loras": {}, "sdxl_loras": {}} 

# Determine which lora list to use based on XL_models setting
lora_list_to_use = lora_data.get('sdxl_loras', {}) if XL_models else lora_data.get('sd15_loras', {})
if not isinstance(lora_list_to_use, dict):
    lora_list_to_use = {}

print('📦 Downloading models and stuff...', end='')

extension_repo = []
PREFIX_MAP = {
    'model': (model_dir, '$ckpt'), 
    'vae': (vae_dir, '$vae'),     
    'lora': (lora_dir, '$lora'),   
    'embed': (embed_dir, '$emb'), 
    'extension': (extension_dir, '$ext'), 
    'adetailer': (adetailer_dir, '$ad'), 
    'control': (control_dir, '$cnet'), 
    'upscale': (upscale_dir, '$ups'), 
    # Other
    'clip': (clip_dir, '$clip'),
    'unet': (unet_dir, '$unet'),
    'vision': (vision_dir, '$vis'),
    'encoder': (encoder_dir, '$enc'),
    'diffusion': (diffusion_dir, '$diff'),
    'config': (config_dir, '$cfg')
}
for dir_path, _ in PREFIX_MAP.values():
    os.makedirs(dir_path, exist_ok=True)

def _center_text(text, terminal_width=45):
    padding = (terminal_width - len(text)) // 2
    return f"{' ' * padding}{text}{' ' * padding}"

def format_output(url, dst_dir, file_name, image_url=None, image_name=None):
    """Formats and prints download details with colored text."""
    info = '[NONE]'
    if file_name:
        info = _center_text(f"[{file_name.rsplit('.', 1)[0]}]")
    if not file_name and 'drive.google.com' in url:
      info = _center_text('[GDrive]')

    sep_line = '───' * 20

    print()
    print(f"{COL.G}{sep_line}{COL.lB}{info}{COL.G}{sep_line}{COL.X}")
    print(f"{COL.Y}{'URL:':<12}{COL.X}{url}")
    print(f"{COL.Y}{'SAVE DIR:':<12}{COL.B}{dst_dir}")
    print(f"{COL.Y}{'FILE NAME:':<12}{COL.B}{file_name}{COL.X}")
    if 'civitai' in url and image_url:
        print(f"{COL.G}{'[Preview]:<12}'}{COL.X}{image_name} → {image_url}")
    print()

def _clean_url(url):
    url_cleaners = {
        'huggingface.co': lambda u: u.replace('/blob/', '/resolve/').split('?')[0],
        'github.com': lambda u: u.replace('/blob/', '/raw/')
    }
    for domain, cleaner in url_cleaners.items():
        if domain in url:
            return cleaner(url)
    return url

def _extract_filename(url):
    # Modified to be more robust for URLs with query parameters or fragments
    if match := re.search(r'\[(.*?)\]', url):
        return match.group(1)
    
    parsed_url = urlparse(url)
    base_name = Path(parsed_url.path).name
    
    # If it's a direct Civitai download API URL, try to get filename from headers
    if 'civitai.com/api/download/models' in url:
        try:
            head_response = requests.head(url, allow_redirects=True, timeout=5)
            if 'content-disposition' in head_response.headers:
                fname_match = re.search(r'filename\*?=(?:UTF-8\'\')?([^;]+)', head_response.headers['content-disposition'])
                if fname_match:
                    return requests.utils.unquote(fname_match.group(1))
        except requests.exceptions.RequestException:
            pass # Continue to fallback if HEAD request fails

    # Fallback to simple path extraction if no explicit filename or Civitai API header
    if base_name:
        return base_name.split('?')[0].split('#')[0] # Remove query params and fragments
    
    return None


def _unpack_zips():
    """Recursively extract and delete all .zip files in PREFIX_MAP directories."""
    for dir_path, _ in PREFIX_MAP.values():
        for zip_file in Path(dir_path).rglob('*.zip'):
            with zipfile.ZipFile(zip_file, 'r') as zf:
                zf.extractall(zip_file.with_suffix(''))
            zip_file.unlink()

# Download Core

def _process_download_link(link):
    """Processes a download link, splitting prefix, URL, and filename."""
    link_original = link # Keep original link for filename extraction if needed
    link = _clean_url(link)
    
    prefix = None
    url_part = link
    filename = None

    # Check for explicit filename in brackets FIRST
    if match := re.search(r'\[(.*?)\]', link_original):
        filename = match.group(1)
        url_part = re.sub(r'\[.*?\]', '', link_original).strip() # Remove filename part from URL

    # Then check for prefix (e.g., "model:http://...")
    if ':' in url_part:
        possible_prefix, remaining_url = url_part.split(':', 1)
        if possible_prefix in PREFIX_MAP:
            prefix = possible_prefix
            url_part = remaining_url.strip()

    # If filename wasn't extracted from brackets, try from URL itself
    if filename is None:
        filename = _extract_filename(url_part)

    return prefix, url_part, filename


def download(line):
    """Downloads files from comma-separated links, processes prefixes, and unpacks zips post-download."""
    # Use re.split to robustly handle commas and spaces as separators
    for link_entry in filter(None, re.split(r',\s*', line)):
        prefix, url_to_download, filename_for_download = _process_download_link(link_entry)

        if prefix:
            target_dir_path, _ = PREFIX_MAP[prefix]
            if prefix == 'extension':
                # For extensions, add to repo list for cloning later
                extension_repo.append((url_to_download, filename_for_download))
            else:
                # For models/VAEs/LoRAs etc., proceed with manual_download
                try:
                    manual_download(url_to_download, target_dir_path, filename_for_download, prefix)
                except Exception as e:
                    print(f"\n> Download error for prefixed link '{link_entry}': {e}")
        else:
            # This block should ideally not be hit if all links are properly prefixed
            # However, if it is hit, it means a raw "url dst_dir filename" or just "url" was passed
            parts = link_entry.split()
            if len(parts) >= 3:
                # Format: "url dst_dir filename" (legacy/manual input)
                manual_download(parts[0], Path(parts[1]), parts[2])
            elif len(parts) == 2:
                # Format: "url filename" (assuming default model_dir)
                manual_download(parts[0], model_dir, parts[1])
            elif len(parts) == 1:
                # Format: "url" (assuming default model_dir and derive filename)
                manual_download(parts[0], model_dir, _extract_filename(parts[0]))
            else:
                print(f"\n> Skipping invalid link format (no prefix, not 'url [dir] file'): '{link_entry}'")

    _unpack_zips()

def manual_download(url, dst_dir, file_name=None, prefix=None):
    clean_url_for_display = url 
    image_url, image_name = None, None

    if 'civitai' in url:
        api = CivitAiAPI(civitai_token)
        if not (data := api.validate_download(url, file_name)):
            return

        model_type = data.model_type
        # Prioritize data.model_name for file_name if available, otherwise use provided file_name
        # This fixes the corruption as data.model_name should be clean
        file_name = data.model_name if data.model_name else file_name 
        clean_url_for_display, url = data.clean_url, data.download_url          
        image_url, image_name = data.image_url, data.image_name     

        # Download preview images
        if image_url and image_name:
            # Ensure m_download receives correct destination Path object
            m_download(f"{image_url} {str(dst_dir)} {image_name}")

    elif any(s in url for s in ('github', 'huggingface.co')):
        # Ensure file_name has an extension if it's missing and we're dealing with a common URL type
        if file_name and '.' not in file_name:
            # Use original clean_url_for_display to get extension before any modifications
            url_ext = Path(urlparse(clean_url_for_display).path).suffix
            if url_ext:
                file_name += url_ext

    # Formatted info output
    format_output(clean_url_for_display, dst_dir, file_name, image_url, image_name)

    # Downloading
    # Ensure dst_dir is passed as a string path to m_download
    m_download(f"{url} {str(dst_dir)} {file_name or ''}", log=True)


''' SubModels - Added URLs '''

# Separation of merged numbers
def _parse_selection_numbers(num_str, max_num):
    """Split a string of numbers into unique integers, considering max_num as the upper limit."""
    num_str = num_str.replace(',', ' ').strip()
    unique_numbers = set()
    max_length = len(str(max_num))

    for part in num_str.split():
        if not part.isdigit():
            continue

        # Check if the entire part is a valid number
        part_int = int(part)
        if part_int <= max_num:
            unique_numbers.add(part_int)
            continue  # No need to split further

        # Split the part into valid numbers starting from the longest possible
        current_position = 0
        part_len = len(part)
        while current_position < part_len:
            found = False
            # Try lengths from max_length down to 1
            for length in range(min(max_length, part_len - current_position), 0, -1):
                substring = part[current_position:current_position + length]
                if substring.isdigit():
                    num = int(substring)
                    if num <= max_num and num != 0:
                        unique_numbers.add(num)
                        current_position += length
                        found = True
                        break
            if not found:
                # Move to the next character if no valid number found
                current_position += 1

    return sorted(unique_numbers)

def handle_submodels(selection, num_selection, model_dict, dst_dir, inpainting_model=False): # Removed base_url parameter
    selected = []
    if selection == "ALL":
        selected = sum(model_dict.values(), [])
    elif selection in model_dict:
        selected.extend(model_dict[selection])

    if num_selection:
        max_num = len(model_dict)
        for num in _parse_selection_numbers(num_selection, max_num):
            if 1 <= num <= max_num:
                name = list(model_dict.keys())[num - 1]
                selected.extend(model_dict[name])

    unique_models = {}
    for model in selected:
        name = model.get('name') or os.path.basename(model['url'])
        if not inpainting_model and "inpainting" in name:
            continue
        unique_models[name] = {
            'url': model['url'],
            'dst_dir': model.get('dst_dir', dst_dir),
            'name': name
        }

    # --- START OF MODIFICATION ---
    # Return a list of explicitly formatted download strings, not a comma-separated string to concatenate
    formatted_download_entries = []
    for m in unique_models.values():
        filename = m['name'] if m['name'] else _extract_filename(m['url'])
        # Add prefix to the URL if it corresponds to a known type (e.g., model, vae, lora)
        # Assuming `model_dict` is passed with consistent types
        # This part requires a bit of inference about the type, or we just rely on `_process_download_link` later
        # For simplicity, we'll format it as "url dst_dir filename" for now, and let `download` handle prefixes if needed.
        formatted_download_entries.append(f"{m['url']} {m['dst_dir']} {filename}")

    return formatted_download_entries # Return list of strings
    # --- END OF MODIFICATION ---

# Initialize line as an empty list to collect individual download entries
line_entries = [] 
line_entries.extend(handle_submodels(model, model_num, model_list, str(model_dir)))
line_entries.extend(handle_submodels(vae, vae_num, vae_list, str(vae_dir)))
line_entries.extend(handle_submodels(controlnet, controlnet_num, controlnet_list, str(control_dir)))

# New: Load _loras-data.py to make lora_data available
try:
    with open(f"{SCRIPTS}/_loras-data.py") as f:
        lora_data_content = f.read()
    exec(lora_data_content, globals(), globals()) 
except FileNotFoundError:
    print(f"Error: _loras-data.py not found at {SCRIPTS}/_loras-data.py. Please ensure it is downloaded.")
    lora_data = {"sd15_loras": {}, "sdxl_loras": {}} 
except Exception as e:
    print(f"Error loading _loras-data.py: {e}")
    lora_data = {"sd15_loras": {}, "sdxl_loras": {}} 

# Determine which lora list to use based on XL_models setting
lora_list_to_use = lora_data.get('sdxl_loras', {}) if XL_models else lora_data.get('sd15_loras', {})
if not isinstance(lora_list_to_use, dict):
    lora_list_to_use = {}

line_entries.extend(handle_submodels(lora, lora_num, lora_list_to_use, str(lora_dir)))


''' File.txt - added urls '''

def _process_lines(lines):
    """Processes text lines, extracts valid URLs with tags/filenames, and ensures uniqueness."""
    current_tag = None
    processed_entries = set()  # Store (tag, clean_url) to check uniqueness
    result_urls = []

    for line in lines:
        clean_line = line.strip().lower()

        # Update the current tag when detected
        for prefix, (_, short_tag) in PREFIX_MAP.items():
            if (f"# {prefix}".lower() in clean_line) or (short_tag and short_tag.lower() in clean_line):
                current_tag = prefix
                break

        if not current_tag:
            continue

        # Normalise the delimiters and process each URL
        normalized_line = re.sub(r'[\s,]+', ',', line.strip())
        for url_entry in normalized_line.split(','):
            url = url_entry.split('#')[0].strip()
            if not url.startswith('http'):
                continue

            clean_url = re.sub(r'\[.*?\]', '', url)
            entry_key = (current_tag, clean_url)    # Uniqueness is determined by a pair (tag, URL)

            if entry_key not in processed_entries:
                filename = _extract_filename(url_entry)
                
                # --- START OF MODIFICATION ---
                # Ensure the filename is not None, and construct the path with dst_dir
                # This will be in the format "url dst_dir filename"
                target_dir = PREFIX_MAP.get(current_tag, (model_dir, ''))[0] # Fallback to model_dir
                if filename:
                    formatted_url = f"{clean_url} {target_dir} {filename}"
                else:
                    # If no explicit filename, rely on manual_download to derive it
                    formatted_url = f"{clean_url} {target_dir}" 
                # --- END OF MODIFICATION ---

                result_urls.append(formatted_url)
                processed_entries.add(entry_key)

    return result_urls # Return list of strings


def process_file_downloads(file_urls, additional_lines=None):
    """Reads URLs from files/HTTP sources."""
    lines = []

    if additional_lines:
        lines.extend(additional_lines.splitlines())

    for source in file_urls:
        if source.startswith('http'):
            try:
                response = requests.get(_clean_url(source))
                response.raise_for_status()
                lines.extend(response.text.splitlines())
            except requests.RequestException:
                continue
        else:
            try:
                with open(source, 'r', encoding='utf-8') as f:
                    lines.extend(f.readlines())
            except FileNotFoundError:
                continue

    return _process_lines(lines)

# File URLs processing
urls_sources = (Model_url, Vae_url, LoRA_url, Embedding_url, Extensions_url, ADetailer_url)
file_urls = [f"{f}.txt" if not f.endswith('.txt') else f for f in custom_file_urls.replace(',', '').split()] if custom_file_urls else []

# --- START OF MODIFICATION ---
# Collect all file download entries into line_entries list
filtered_prefixed_urls = []
for idx, url_source in enumerate(urls_sources):
    if url_source:
        prefix_key = list(PREFIX_MAP.keys())[idx] 
        target_dir = PREFIX_MAP[prefix_key][0] 

        for single_url in url_source.replace(',', ' ').split():
            if single_url: 
                filename_from_url = _extract_filename(single_url)
                if filename_from_url:
                    clean_single_url = re.sub(r'\[.*?\]', '', single_url)
                    formatted_entry = f"{clean_single_url} {target_dir} {filename_from_url}"
                else:
                    formatted_entry = f"{single_url} {target_dir}"
                filtered_prefixed_urls.append(formatted_entry)

line_entries.extend(filtered_prefixed_urls)
line_entries.extend(process_file_downloads(file_urls, empowerment_output))

# Final string to pass to download function, joining all collected entries
line = ', '.join(line_entries)
# --- END OF MODIFICATION ---


if detailed_download == 'on':
    print(f"\n\n{COL.Y}# ====== Detailed Download ====== #\n{COL.X}")
    download(line)
    print(f"\n{COL.Y}# =============================== #\n{COL.X}")
else:
    with capture.capture_output():
        download(line)

print('\r🏁 Download Complete!' + ' '*15)


## Install of Custom extensions
def _clone_repository(repo, repo_name, extension_dir):
    """Clones the repository to the specified directory."""
    repo_name = repo_name or repo.split('/')[-1]
    command = f"cd {extension_dir} && git clone --depth 1 --recursive {repo} {repo_name} && cd {repo_name} && git fetch"
    ipySys(command)

extension_type = 'nodes' if UI == 'ComfyUI' else 'extensions'

if extension_repo:
    print(f"✨ Installing custom {extension_type}...", end='')
    with capture.capture_output():
        for repo, repo_name in extension_repo:
            _clone_repository(repo, repo_name, str(extension_dir)) # Updated to use extension_dir from settings
    print(f"\r📦 Installed '{len(extension_repo)}' custom {extension_type}!")


# === SPECIAL ===
## Sorting models `bbox` and `segm` | Only ComfyUI
if UI == 'ComfyUI':
    dirs = {'segm': '-seg.pt', 'bbox': None}
    for d in dirs:
        os.makedirs(os.path.join(str(adetailer_dir), d), exist_ok=True) # Updated to use adetailer_dir from settings

    for filename in os.listdir(str(adetailer_dir)): # Updated to use adetailer_dir from settings
        src = os.path.join(str(adetailer_dir), filename) # Updated to use adetailer_dir from settings

        if os.path.isfile(src) and filename.endswith('.pt'):
            dest_dir = 'segm' if filename.endswith('-seg.pt') else 'bbox'
            dest = os.path.join(str(adetailer_dir), dest_dir, filename) # Updated to use adetailer_dir from settings

            if os.path.exists(dest):
                os.remove(src)
            else:
                shutil.move(src, dest)


## List Models and stuff
ipyRun('run', f"{SCRIPTS}/download-result.py")
