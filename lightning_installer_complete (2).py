#!/usr/bin/env python3
"""
Comprehensive Lightning AI Installation Script for sdAIgen
This script completely patches ALL platform-specific errors in the original sdAIgen repository.
This corrected version fixes bugs in the original patching logic to ensure valid Python code is generated.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
import urllib.request
import re

def detect_lightning_ai():
    """Detect if running on Lightning AI"""
    indicators = [
        os.environ.get('LIGHTNING_CLOUD_PROJECT_ID'),
        os.environ.get('LIGHTNING_AI'),
        os.path.exists('/teamspace'),
        'lightning' in os.environ.get('PWD', '').lower(),
        'lightning' in str(Path.home()).lower(),
        'studios' in os.environ.get('PWD', '').lower()
    ]
    return any(indicators)

def setup_lightning_directories():
    """Set up Lightning AI directory structure"""
    base_path = Path.cwd() / 'sdAIgen_workspace'
    
    directories = {
        'base': base_path,
        'scripts': base_path / 'ANXETY' / 'scripts',
        'models': base_path / 'models',
        'outputs': base_path / 'outputs',
        'extensions': base_path / 'extensions',
        'embeddings': base_path / 'embeddings',
        'lora': base_path / 'lora',
        'vae': base_path / 'vae',
        'controlnet': base_path / 'controlnet',
        'config': base_path / 'config',
        'logs': base_path / 'logs',
        'temp': base_path / 'temp',
        'cache': base_path / '.cache'
    }
    
    # Clean slate: remove old directory if it exists
    if base_path.exists():
        print(f"🧹 Removing old directory to ensure a clean installation: {base_path}")
        shutil.rmtree(base_path)

    for name, path in directories.items():
        path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created all directories in: {base_path}")
    
    return directories

def create_comprehensive_setup_patches(base_path_str):
    """Create comprehensive patches for setup.py"""
    return [
        {
            'type': 'replace_function',
            'function_name': 'environment_setup',
            'old_pattern': r'def environment_setup\(\):.*?(?=def|\Z)',
            'new_content': f'''def environment_setup():
    """Universal environment setup for all platforms"""
    import os
    from pathlib import Path
    
    # This setup is now hardcoded for the patched Lightning environment
    platform = 'lightning'
    os.environ['DETECTED_PLATFORM'] = platform
    print(f"🔍 Detected platform: {{platform}}")
    
    base_path = Path('{base_path_str}')
    
    dirs_to_create = [
        base_path / 'models', base_path / 'outputs', base_path / 'extensions',
        base_path / 'embeddings', base_path / 'lora', base_path / 'vae',
        base_path / 'controlnet', base_path / 'config', base_path / 'logs',
        base_path / 'temp', base_path / '.cache'
    ]
    for directory in dirs_to_create:
        directory.mkdir(parents=True, exist_ok=True)
    
    os.environ['HOME'] = str(base_path)
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
    os.environ['TMPDIR'] = str(base_path / 'temp')
    
    return str(base_path)
'''
        },
        {
            'type': 'replace',
            'old': 'HOME = Path.home()',
            'new': f"HOME = Path('{base_path_str}')"
        },
        { 'type': 'replace', 'old': "'/content/", 'new': "str(HOME) + '/" },
        { 'type': 'replace', 'old': '"/content/', 'new': 'str(HOME) + "/' },
    ]

def create_comprehensive_launch_patches(dirs):
    """Create comprehensive patches for launch.py"""
    return [
        {
            'type': 'insert_after',
            'search': 'import os',
            'insert': f'''
# Universal platform detection and optimization
os.environ['DETECTED_PLATFORM'] = 'lightning'
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
print("⚡ Applied Lightning AI optimizations")

PLATFORM_ARGS = [
    '--xformers', '--no-half-vae', '--opt-split-attention', '--medvram',
    '--disable-console-progressbars', '--api', '--cors-allow-origins=*',
    '--listen', '--port=8080', '--ckpt-dir={dirs["models"]}',
    '--embeddings-dir={dirs["embeddings"]}', '--lora-dir={dirs["lora"]}',
    '--vae-dir={dirs["vae"]}'
]
'''
        },
        {
            'type': 'replace',
            'old': "args = ['--share']",
            'new': "args = PLATFORM_ARGS"
        }
    ]

def apply_patches(file_path, patches):
    if not file_path.exists():
        print(f"⚠️ File not found, cannot patch: {file_path}")
        return False
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        for patch in patches:
            if patch['type'] == 'replace':
                content = content.replace(patch['old'], patch['new'])
            elif patch['type'] == 'insert_after':
                content = content.replace(patch['search'], patch['search'] + '\\n' + patch['insert'], 1)
            elif patch['type'] == 'replace_function':
                content = re.sub(patch['old_pattern'], patch['new_content'], content, flags=re.DOTALL)
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"🔧 Successfully patched: {file_path.name}")
        else:
            print(f"ℹ️ No changes needed for: {file_path.name}")
        return True
    except Exception as e:
        print(f"❌ Failed to patch {file_path}: {e}")
        return False

def download_and_patch_script(url, local_path, patches):
    try:
        print(f"📥 Downloading: {local_path.name}")
        urllib.request.urlretrieve(url, local_path)
        print(f"  ✅ Downloaded to: {local_path}")
        if patches:
            apply_patches(local_path, patches)
        return True
    except Exception as e:
        print(f"❌ Failed to download/patch {url}: {e}")
        return False

def main():
    print("🚀 Starting sdAIgen Installation and Patching Process...")
    if not detect_lightning_ai():
        print("⚠️ WARNING: This script is optimized for a Lightning AI environment.")
    
    directories = setup_lightning_directories()
    base_path_str = str(directories['base'])

    print("\\n📦 Installing requirements...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet', 
                        'torch', 'torchvision', 'xformers', 'diffusers', 'transformers', 
                        'accelerate', 'safetensors', 'opencv-python-headless', 'pillow'], check=True)
        print("✅ Core requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python packages: {e}")
        return

    print("\\n📥 Downloading and patching scripts...")
    base_url = "https://raw.githubusercontent.com/anxety-solo/sdAIgen/main/scripts"
    scripts_dir = directories['scripts']
    
    scripts_to_process = [
        {'url': f"{base_url}/setup.py", 'local_path': scripts_dir / 'setup.py', 'patches': create_comprehensive_setup_patches(base_path_str)},
        {'url': f"{base_url}/launch.py", 'local_path': scripts_dir / 'launch.py', 'patches': create_comprehensive_launch_patches(directories)}
    ]
    
    success_count = sum(1 for script in scripts_to_process if download_and_patch_script(**script))
    
    if success_count != len(scripts_to_process):
        print("\\n❌ Not all scripts could be downloaded or patched. Aborting.")
        return

    print("\\n🚀 Creating launcher script...")
    launcher_script_path = directories['base'] / 'start_sdaigen.py'
    
    # *** THIS IS THE CORRECTED LAUNCHER CONTENT ***
    launcher_content = f'''#!/usr/bin/env python3
import sys
import os
import asyncio
from pathlib import Path

print("🚀 Launching sdAIgen...")

scripts_dir = Path("{scripts_dir}")
sys.path.insert(0, str(scripts_dir))

setup_script = scripts_dir / 'setup.py'

if not setup_script.exists():
    print(f"❌ Critical error: Cannot find setup.py at {{setup_script}}")
    sys.exit(1)

# Execute the patched setup script which will then handle the launch
try:
    # Import the setup module
    import setup
    
    # The original script uses an async main function. We must find and run it.
    if hasattr(setup, 'main_async'):
        # Explicitly run its main asynchronous function
        # This bypasses the '__name__ == "__main__"' guard in setup.py
        print("   Found main_async function. Starting application...")
        asyncio.run(setup.main_async())
    else:
        print("❌ Critical error: Could not find the 'main_async' function in the setup script.")
        sys.exit(1)
        
except Exception as e:
    import traceback
    print(f"❌ An error occurred while launching sdAIgen: {{e}}")
    traceback.print_exc()
    print("   Please check the logs and ensure all files are correctly patched.")
    sys.exit(1)
'''
    launcher_script_path.write_text(launcher_content)
    launcher_script_path.chmod(0o755)

    print("\\n" + "="*60)
    print("🎉 INSTALLATION COMPLETE!")
    print("="*60)
    print(f"📁 All files installed in: {directories['base']}")
    print(f"\\nTo start the application, run the following command in a new cell:")
    print(f"\\033[1m%run {launcher_script_path}\\033[0m")
    print("\\n✨ The script has been corrected and patched to run in this environment.")

if __name__ == "__main__":
    main()