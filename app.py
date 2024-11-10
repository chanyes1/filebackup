from flask import Flask, render_template, request
import os
import shutil
from datetime import datetime

app = Flask(__name__)

BACKUP_FOLDER = "backups"
os.makedirs(BACKUP_FOLDER, exist_ok=True)

backup_history = []

def get_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)  # Convert bytes to megabytes

@app.route('/')
def index():
    return render_template('index.html', history=backup_history)

@app.route('/backup', methods=['POST'])
def backup():
    path = request.form['path']
    backup_type = request.form['backup_type']
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    if backup_type == 'file':
        if not os.path.isfile(path):
            message = "Error: The file does not exist!"
            return render_template('index.html', message=message, history=backup_history)

        file_name = os.path.basename(path)
        backup_file_name = f"{timestamp}_{file_name}"
        backup_path = os.path.join(BACKUP_FOLDER, backup_file_name)

        try:
            shutil.copy(path, backup_path)
            file_size_mb = get_file_size(path)
            message = f"Success: File backed up as '{backup_file_name}' ({file_size_mb:.2f} MB) in the 'backups' folder."
            backup_history.append({'name': backup_file_name, 'size': f"{file_size_mb:.2f} MB", 'size_mb': file_size_mb})
        except Exception as e:
            message = f"Error: Could not back up the file. {str(e)}"

    elif backup_type == 'folder':
        if not os.path.isdir(path):
            message = "Error: The folder does not exist!"
            return render_template('index.html', message=message, history=backup_history)

        folder_name = os.path.basename(path.rstrip("/\\"))
        backup_folder_name = f"{timestamp}_{folder_name}"
        backup_folder_path = os.path.join(BACKUP_FOLDER, backup_folder_name)

        try:
            shutil.copytree(path, backup_folder_path)
            folder_size_mb = sum(get_file_size(os.path.join(dirpath, f)) for dirpath, _, files in os.walk(path) for f in files)
            message = f"Success: Folder backed up as '{backup_folder_name}' ({folder_size_mb:.2f} MB) in the 'backups' folder."
            backup_history.append({'name': backup_folder_name, 'size': f"{folder_size_mb:.2f} MB", 'size_mb': folder_size_mb})
        except Exception as e:
            message = f"Error: Could not back up the folder. {str(e)}"

    return render_template('index.html', message=message, history=backup_history)

if __name__ == '__main__':
    app.run(debug=True)
