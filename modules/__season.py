# ~ __season.py | by ANXETY ~ (GitHub Commit & File List Update)

from IPython.display import display, HTML
import datetime

TRANSLATIONS = {
    'en': {
        'done_message': "Done! Now you can run the cells below. ☄️",
        'runtime_env': "Runtime environment:",
        'file_location': "File location:",
        'current_fork': "Current fork:",
        'current_branch': "Current branch:",
        'latest_commit': "Latest Commit:",
        'commit_author': "by",
        'downloaded_files_summary': "Downloaded Files"
    },
    'ru': {
        'done_message': "Готово! Теперь вы можете выполнить ячейки ниже. ☄️",
        'runtime_env': "Среда выполнения:",
        'file_location': "Расположение файлов:",
        'current_fork': "Текущий форк:",
        'current_branch': "Текущая ветка:",
        'latest_commit': "Последний коммит:",
        'commit_author': "от",
        'downloaded_files_summary': "Загруженные файлы"
    }
}

def display_info(env, scr_folder, branch, lang='en', fork=None, commit_info=None, downloaded_files=None):
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])

    # --- Commit Info HTML ---
    commit_html = ""
    if commit_info and not commit_info.get('error'):
        # Format date nicely
        date_obj = datetime.datetime.fromisoformat(commit_info['date'].replace('Z', '+00:00'))
        formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S UTC')
        
        commit_html = f"""
        <div class="commit-info">
            <span>{translations['latest_commit']}</span>
            <span class="commit-sha">[{commit_info['sha']}]</span>
            <span class="commit-message">"{commit_info['message']}"</span>
            <span>{translations['commit_author']}</span>
            <span class="commit-author">{commit_info['author']}</span>
            <span>on {formatted_date}</span>
        </div>
        """
    elif commit_info and commit_info.get('error'):
        commit_html = f"""
        <div class="commit-info">
            <span class="commit-error">Could not fetch latest commit info: {commit_info['error']}</span>
        </div>
        """

    # --- Downloaded Files HTML ---
    files_html = ""
    if downloaded_files:
        file_list_items = "".join([f"<li>{file}</li>" for file in downloaded_files])
        files_html = f"""
        <details class="downloaded-files-details">
            <summary>{translations['downloaded_files_summary']} ({len(downloaded_files)})</summary>
            <ul class="downloaded-files-list">{file_list_items}</ul>
        </details>
        """

    # --- Main Banner HTML ---
    CONTENT = f"""
    <div class="season-container">
      <div class="text-container">
        <span>A</span><span>N</span><span>X</span><span>E</span><span>T</span><span>Y</span>
        <span>&nbsp;</span>
        <span>V</span><span>2</span>
      </div>
      <div class="message-container">
        <span>{translations['done_message']}</span>
        <span>{translations['runtime_env']} <span class="env">{env}</span></span>
        <span>{translations['file_location']} <span class="files-location">{scr_folder}</span></span>
        {f"<span>{translations['current_fork']} <span class='fork'>{fork}</span></span>" if fork else ""}
        <span>{translations['current_branch']} <span class="branch">{branch}</span></span>
        {commit_html}
        {files_html}
      </div>
    </div>
    """
    
    # --- CSS ---
    STYLE = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Righteous&display=swap');
    .season-container {
      position: relative; margin: 0 10px !important; padding: 20px !important;
      border-radius: 15px; margin: 10px 0; overflow: hidden;
      background: linear-gradient(180deg, #66666633, transparent);
      border-top: 2px solid #666666;
    }
    .text-container {
      display: flex; flex-wrap: wrap; justify-content: center; align-items: center;
      gap: 0.5em; font-family: 'Righteous', cursive; margin-bottom: 1em;
    }
    .text-container span {
      font-size: 2.5rem; color: #fff7cc;
    }
    .message-container {
      font-family: 'Righteous', cursive; text-align: center; display: flex;
      flex-direction: column; gap: 0.5em; font-size: 1.2rem; color: #fff7cc;
    }
    .env { color: #FFA500 !important; }
    .files-location { color: #FF99C2 !important; }
    .branch { color: #16A543 !important; }
    .fork { color: #C786D3 !important; }
    
    .commit-info {
        background-color: rgba(0,0,0,0.2); border-radius: 8px; padding: 8px;
        margin-top: 10px; font-size: 0.9rem; color: #ccc;
    }
    .commit-info span { font-size: 0.9rem !important; color: #ccc !important; }
    .commit-sha { color: #FFA500 !important; font-family: monospace; }
    .commit-message { color: #fff !important; font-style: italic; }
    .commit-author { color: #93b466 !important; }
    .commit-error { color: #ff8f66 !important; }

    .downloaded-files-details { margin-top: 10px; }
    .downloaded-files-details summary {
        cursor: pointer; background-color: rgba(0,0,0,0.2);
        padding: 5px; border-radius: 5px;
    }
    .downloaded-files-list {
        text-align: left; font-size: 0.8rem; font-family: monospace;
        background-color: rgba(0,0,0,0.4); border-radius: 5px;
        padding: 10px 10px 10px 30px; margin-top: 5px;
        max-height: 150px; overflow-y: auto;
    }
    </style>
    """
    display(HTML(CONTENT + STYLE))
