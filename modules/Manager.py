""" Manager Module | by ANXETY """

from CivitaiAPI import CivitAiAPI    # CivitAI API
import json_utils as js              # JSON

from urllib.parse import urlparse, parse_qs
from pathlib import Path
import subprocess
import requests
import zipfile
import shlex
import sys
import os
import re


CD = os.chdir

# Constants
HOME = Path.home()
SCR_PATH = HOME / 'ANXETY'
SETTINGS_PATH = SCR_PATH / 'settings.json'

CAI_TOKEN = js.read(SETTINGS_PATH, 'WIDGETS.civitai_token') or '65b66176dcf284b266579de57fbdc024'
HF_TOKEN = js.read(SETTINGS_PATH, 'WIDGETS.huggingface_token') or ''


## ====================== Download =======================

# Logging function
def log_message(message, log=False):
    if log:
        print(f"{message}")

# Error handling decorator
def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_message(f"> \033[31m[Error]:\033[0m {e}", kwargs.get('log', False))
            return None
    return wrapper

# Download function
@handle_errors
def m_download(line, log=False, unzip=False):
    """Download files from a comma-separated list of URLs or file paths."""
    links = [link.strip() for link in line.split(',') if link.strip()]

    if not links:
        log_message('> Missing URL, downloading nothing', log)
        return

    for link in links:
        url = link[0]
        if url.endswith('.txt') and Path(url).expanduser().is_file():
            with open(Path(url).expanduser(), 'r') as file:
                for line in file:
                    process_download(line, log, unzip)
        else:
            process_download(link, log, unzip)

@handle_errors
def process_download(line, log, unzip):
    """Process an individual download line."""
    parts = line.split()
    url = parts[0].replace('\\', '')
    url = clean_url(url)

    if not url:
        return

    path, filename = handle_path_and_filename(parts, url)
    current_dir = Path.cwd()

    try:
        if path:
            path.mkdir(parents=True, exist_ok=True)
            CD(path)

        download_file(url, filename, log)
        if unzip and filename and filename.endswith('.zip'):
            unzip_file(filename, log)
    finally:
        CD(current_dir)

def handle_path_and_filename(parts, url):
    """Extract path and filename from parts."""
    if len(parts) >= 3:
        path = Path(parts[1]).expanduser()
        filename = parts[2]
    elif len(parts) >= 2:
        path = Path(parts[1]).expanduser() if '/' in parts[1] or '~/' in parts[1] else None
        filename = None if path else parts[1]
    else:
        path, filename = None, None

    if 'drive.google.com' not in url:
        if filename and not Path(filename).suffix:
            url = parts[0]
            url_extension = Path(urlparse(url).path).suffix
            if url_extension:
                filename += url_extension
            else:
                filename = None

    return path, filename

@handle_errors
def download_file(url, filename, log):
    """Download a file from various sources."""
    is_special_domain = any(domain in url for domain in ['civitai.com', 'huggingface.co', 'github.com'])

    if is_special_domain:
        download_with_aria2(url, filename, log)
    elif 'drive.google.com' in url:
        download_google_drive(url, filename, log)
    else:
        """Download using curl."""
        command = f"curl -#JL '{url}'"
        if filename:
            command += f" -o '{filename}'"
        execute_shell_command(command, log)

def download_with_aria2(url, filename, log):
    """Download using aria2c."""
    aria2_args = ('aria2c --header="User-Agent: Mozilla/5.0" --allow-overwrite=true --console-log-level=error --stderr=true -c -x16 -s16 -k1M -j5')

    if HF_TOKEN and 'huggingface.co' in url:
        aria2_args += f' --header="Authorization: Bearer {HF_TOKEN}"'

    command = f"{aria2_args} '{url}'"

    if not filename:
        filename = get_file_name(url)
    if filename:
        command += f" -o '{filename}'"

    monitor_aria2_download(command, log)

def download_google_drive(url, filename, log):
    """Download from Google Drive using gdown."""
    cmd = 'gdown --fuzzy ' + url
    if filename:
        cmd += ' -O ' + filename
    if 'drive.google.com/drive/folders' in url:
        cmd += ' --folder'

    execute_shell_command(cmd, log)

def get_file_name(url):
    """Get the file name based on the URL."""
    if any(domain in url for domain in ['civitai.com', 'drive.google.com']):
        return None
    else:
        return Path(urlparse(url).path).name

@handle_errors
def unzip_file(zip_filepath, log):
    """Extract the ZIP file."""
    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
        zip_ref.extractall(Path(zip_filepath).parent)
    log_message(f">> Successfully unpacked: {zip_filepath}", log)

@handle_errors
def monitor_aria2_download(command, log):
    """Monitor aria2c download progress."""
    try:
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        error_codes, error_messages = [], []
        result = ''
        br = False

        while True:
            lines = process.stderr.readline()
            if lines == '' and process.poll() is not None:
                break

            if lines:
                result += lines
                for output_line in lines.splitlines():
                    handle_error_output(lines, error_codes, error_messages)

                    if re.match(r'\[#\w{6}\s.*\]', output_line):
                        formatted_line = format_output_line(output_line)
                        if log:
                            print(f"\r{' ' * 180}\r{formatted_line}", end='')
                            sys.stdout.flush()
                        br = True
                        break

        if log:
            for error in error_codes + error_messages:
                print(f"{error}")

            if br:
                print()

            stripe = result.find('======+====+===========')
            if stripe != -1:
                for line in result[stripe:].splitlines():
                    if '|' in line and 'OK' in line:
                        formatted_line = re.sub(r'(\|\s*)(OK)(\s*\|)', r'\1\033[32m\2\033[0m\3', line)
                        print(f"{formatted_line}")

        process.wait()
    except KeyboardInterrupt:
        log_message('\n> Download interrupted', log)

def format_output_line(line):
    """Format a line of output with ANSI color codes."""
    line = re.sub(r'\[', '\033[35m【\033[0m', line)
    line = re.sub(r'\]', '\033[35m】\033[0m', line)
    line = re.sub(r'(#)(\w+)', r'\1\033[32m\2\033[0m', line)
    line = re.sub(r'(\(\d+%\))', r'\033[36m\1\033[0m', line)
    line = re.sub(r'(CN:)(\d+)', r'\1\033[34m\2\033[0m', line)
    line = re.sub(r'(DL:)(\d+\w+)', r'\1\033[32m\2\033[0m', line)
    line = re.sub(r'(ETA:)(\d+\w+)', r'\1\033[33m\2\033[0m', line)
    return line

def handle_error_output(line, error_codes, error_messages):
    """Check and collect error messages from the output."""
    if 'errorCode' in line or 'Exception' in line:
        error_codes.append(line)
    if '|' in line and 'ERR' in line:
        formatted_line = re.sub(r'(\|\s*)(ERR)(\s*\|)', r'\1\033[31m\2\033[0m\3', line)
        error_messages.append(formatted_line)

@handle_errors
def execute_shell_command(command, log):
    """Execute a shell command and handle logging."""
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if log:
        for line in process.stderr:
            print(line, end='')
    process.wait()

@handle_errors
def clean_url(url):
    """Clean and format URLs to ensure correct access."""
    if 'civitai.com/models/' in url:
        api = CivitAiAPI(CAI_TOKEN)
        if not (data := api.validate_download(url)):
            return

        url = data.download_url

    elif 'huggingface.co' in url:
        if '/blob/' in url:
            url = url.replace('/blob/', '/resolve/')
        if '?' in url:
            url = url.split('?')[0]

    elif 'github.com' in url:
        if '/blob/' in url:
            url = url.replace('/blob/', '/raw/')

    return url

## ======================== Clone ========================

def m_clone(input_source, log=False):
    """Main function to clone repositories"""
    commands = process_input_source(input_source, log)

    if not commands:
        log_message('>> No valid repositories to clone', log)
        return

    for command in commands:
        execute_command(command, log=log)

def process_input_source(input_source, log=False):
    input_path = Path(input_source).expanduser()
    commands = []

    def build_command(line):
        line = line.strip()
        if not line:
            return None

        # Extract base command and URL
        parts = shlex.split(line)
        if len(parts) >= 2 and parts[0] == 'git' and parts[1] == 'clone':
            base_command = parts
            url = next((p for p in parts[2:] if re.match(r'https?://', p)), None)
        else:
            url = line
            base_command = ['git', 'clone', url]

        if not url:
            log_message(f">> Skipping invalid command: {line}", log)
            return None

        # Add shallow clone parameters
        if '--depth' not in base_command:
            base_command += ['--depth', '1']

        return ' '.join(base_command)

    # Process different input types
    if input_source.endswith('.txt') and input_path.is_file():
        with open(input_path, 'r') as f:
            for line in f:
                if cmd := build_command(line):
                    commands.append(cmd)
    else:
        sources = [input_source] if isinstance(input_source, str) else input_source
        for source in sources:
            if cmd := build_command(source):
                commands.append(cmd)

    return commands


@handle_errors
def execute_command(command, log=False):
    repo_url = re.search(r'https?://\S+', command).group()
    process = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    repo_name = None
    while True:
        output = process.stdout.readline()
        if not output and process.poll() is not None:
            break

        output = output.strip()
        if not output:
            continue

        # Parse cloning progress
        if 'Cloning into' in output:
            repo_path = re.search(r"'(.+?)'", output).group(1)
            repo_name = '/'.join(repo_path.split('/')[-3:])
            log_message(f">> Cloning: {repo_name} -> {repo_url}", log)

        # Handle error messages
        if 'fatal' in output.lower():
            log_message(f">> \033[31m[Error]:\033[0m {output}", log)