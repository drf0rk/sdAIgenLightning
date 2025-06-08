# ~ setup.py | by ANXETY ~ (GitHub Commit & File List Update)

import sys
from pathlib import Path
import os

# VERY EARLY SYS.PATH MODIFICATION FOR CRITICAL IMPORTS
_HOME_EARLY = Path.home()
_ANXETY_PATH_EARLY = _HOME_EARLY / 'ANXETY'
_MODULES_PATH_EARLY = _ANXETY_PATH_EARLY / 'modules'
_SCRIPTS_PATH_EARLY = _ANXETY_PATH_EARLY / 'scripts'
_MODULES_PATH_EARLY.mkdir(parents=True, exist_ok=True)
_SCRIPTS_PATH_EARLY.mkdir(parents=True, exist_ok=True)
if str(_MODULES_PATH_EARLY) not in sys.path: sys.path.insert(0, str(_MODULES_PATH_EARLY))
if str(_SCRIPTS_PATH_EARLY) not in sys.path: sys.path.insert(0, str(_SCRIPTS_PATH_EARLY))

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

# --- Constants ---
HOME = Path.home()
SCR_PATH = HOME / 'ANXETY'
SETTINGS_PATH = SCR_PATH / 'settings.json'

nest_asyncio.apply()

# --- GitHub API Fetcher ---
async def get_latest_commit_info(session, user, repo, branch):
    """Fetches the latest commit information from the GitHub API."""
    api_url = f"https://api.github.com/repos/{user}/{repo}/commits/{branch}"
    try:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                commit = data.get('commit', {})
                return {
                    'sha': data.get('sha', 'N/A')[:7],
                    'message': commit.get('message', 'N/A').split('\n')[0],
                    'author': commit.get('author', {}).get('name', 'N/A'),
                    'date': commit.get('author', {}).get('date', 'N/A'),
                }
            else:
                return {'error': f"Failed to fetch commit data, Status: {response.status}"}
    except Exception as e:
        return {'error': f"Exception during API call: {e}"}


# --- File Download Logic ---
def generate_file_list(structure, base_url, base_path):
    """Generate flat list of (url, path) from nested structure"""
    items = []
    def walk(struct, path_parts):
        for key, value in struct.items():
            current_path = [*path_parts, key] if key else path_parts
            if isinstance(value, dict):
                walk(value, current_path)
            else:
                url_path = '/'.join(current_path)
                for file in value:
                    full_url = f"{base_url}/{url_path}/{file}" if url_path else f"{base_url}/{file}"
                    file_path = base_path.joinpath(*current_path, file)
                    items.append((full_url, file_path))
    walk(structure, [])
    return items

async def download_file(session, url, path):
    """Download and save single file with error handling"""
    try:
        # Add a cache-busting query parameter
        cache_buster_url = f"{url}?t={int(time.time())}"
        async with session.get(cache_buster_url) as resp:
            resp.raise_for_status()
            content = await resp.read()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            return (True, path, None)
    except aiohttp.ClientResponseError as e:
        return (False, path, f"HTTP error {e.status}")
    except Exception as e:
        return (False, path, f"Error: {e}")

async def download_files_async(scr_path, lang, user, repo, branch, log_errors):
    """Main download executor with error logging and file list return."""
    # To ensure a clean pull, we can optionally clear the old scripts
    shutil.rmtree(scr_path / 'scripts', ignore_errors=True)
    shutil.rmtree(scr_path / 'modules', ignore_errors=True)
    
    files_structure = {
        'CSS': ['main-widgets.css', 'download-result.css', 'auto-cleaner.css'],
        'JS': ['main-widgets.js'],
        'modules': ['json_utils.py', 'webui_utils.py', 'widget_factory.py', 'TunnelHub.py', 'CivitaiAPI.py', 'Manager.py', '__season.py'],
        'scripts': {
            'UIs': ['A1111.py', 'ComfyUI.py', 'Forge.py', 'Classic.py', 'ReForge.py', 'SD-UX.py'],
            lang: [f"widgets-{lang}.py", f"downloading-{lang}.py"],
            '': ['launch.py', 'auto-cleaner.py', 'download-result.py', '_models-data.py', '_xl-models-data.py', '_loras-data.py']
        }
    }
    base_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}"
    file_list = generate_file_list(files_structure, base_url, scr_path)
    
    downloaded_files = []
    errors = []
    
    async with aiohttp.ClientSession() as session:
        tasks = [download_file(session, url, path) for url, path in file_list]
        for future in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading repository files", unit="file"):
            success, path, error = await future
            if success:
                downloaded_files.append(str(path.relative_to(HOME)))
            else:
                errors.append((path, error))
    
    clear_output()
    if log_errors and errors:
        print("\nErrors occurred during download:")
        for path, error in errors:
            print(f"Path: {path}, Error: {error}")
            
    return downloaded_files

# --- Main Execution ---
async def main_async():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--lang', type=str, default='en')
    parser.add_argument('-b', '--branch', type=str, default='main')
    parser.add_argument('-f', '--fork', type=str, default='anxety-solo/sdAIgen')
    parser.add_argument('-L', '--log', action='store_true')
    args, _ = parser.parse_known_args()

    user, repo = args.fork.split('/')
    
    # Import necessary modules after path setup
    from __season import display_info
    import json_utils as js
    
    commit_info = {}
    async with aiohttp.ClientSession() as session:
        commit_info = await get_latest_commit_info(session, user, repo, args.branch)

    downloaded_files = await download_files_async(SCR_PATH, args.lang, user, repo, args.branch, args.log)
    
    # Setup modules folder
    if str(SCR_PATH / 'modules') not in sys.path:
        sys.path.insert(0, str(SCR_PATH / 'modules'))
    
    display_info(
        env=os.environ.get('DETECTED_PLATFORM', 'local'),
        scr_folder=str(SCR_PATH),
        branch=args.branch,
        fork=args.fork,
        commit_info=commit_info,
        downloaded_files=downloaded_files
    )

if __name__ == '__main__':
    asyncio.run(main_async())
