import sys
import subprocess
import os
import json
from pathlib import Path

import cure_terminal as ct

# ANSI color codes
COLOR_RESET = '\033[0m'
COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'
COLOR_YELLOW = '\033[93m'
COLOR_BLUE = '\033[94m'

def get_installed_package_location(package_name):
    """
    Check if the package is installed in editable mode by querying pip show output.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Editable project location:"):
                    return line.split(": ", 1)[1]
    except subprocess.CalledProcessError as e:
        ct.Print.status("Error", f"checking package location: `[[COLOR_OFF]]{e}[[COLOR_ON]]`")
    return None

def uninstall_package(package_name):
    """
    Uninstall the package if it is already installed.
    """
    try:
        ct.Print.status("Info", f"Uninstalling existing package: `[[COLOR_OFF]]{package_name}[[COLOR_ON]]`")
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package_name])
        ct.Print.status("Success", "Package uninstalled successfully.")
    except subprocess.CalledProcessError as e:
        ct.Print.status("Error", f"uninstalling the package: `[[COLOR_OFF]]{e}[[COLOR_ON]]`")
        sys.exit(1)

def install_package():
    package_name = "cure_terminal"
    project_path = str(Path(__file__).parent.resolve())
    installed_path = get_installed_package_location(package_name)

    ct.Print.status("Info", f"Project path: `[[COLOR_OFF]]{project_path}[[COLOR_ON]]`\n")
    if installed_path:
        ct.Print.status("Notice", f"Detected installed package path: `[[COLOR_OFF]]{installed_path}[[COLOR_ON]]`\n")

    if installed_path == project_path:
        ct.Print.status("Success", f"`[[COLOR_OFF]]{package_name}[[COLOR_ON]]` is already installed in editable mode at `[[COLOR_OFF]]{project_path}[[COLOR_ON]]`. Skipping installation.")
    else:
        if installed_path:
            uninstall_package(package_name)

        python_executable = sys.executable
        command = [python_executable, "-m", "pip", "install", "-e", project_path]

        ct.Print.status("Info", f"Running command: `[[COLOR_OFF]]{' '.join(command)}[[COLOR_ON]]`")

        try:
            subprocess.check_call(command)
            ct.Print.status("Success", "Package installed successfully in editable mode.")
        except subprocess.CalledProcessError as e:
            ct.Print.status("Error", f"An error occurred while installing the package: `[[COLOR_OFF]]{e}[[COLOR_ON]]`")
            sys.exit(1)

def find_vscode_settings_path():
    paths_to_check = [
        Path.home() / "AppData/Roaming/Code/User/settings.json",
        Path.home() / "Library/Application Support/Code/User/settings.json",
        Path.home() / ".config/Code/User/settings.json",
        Path(".vscode/settings.json"),
    ]

    for path in paths_to_check:
        if path.exists():
            return path
    return None

def update_vscode_settings():
    settings_path = find_vscode_settings_path()
    if not settings_path:
        ct.Print.status("Notice", "VS Code settings.json file not found.")
        return

    with open(settings_path, "r") as f:
        try:
            settings = json.load(f)
        except json.JSONDecodeError:
            ct.Print.status("Error", "Invalid JSON format in settings.json.")
            return

    extra_paths = settings.get("python.analysis.extraPaths", [])
    if not isinstance(extra_paths, list):
        extra_paths = []

    project_path = str(Path(__file__).parent.resolve())
    if project_path not in extra_paths:
        extra_paths.append(project_path)
        settings["python.analysis.extraPaths"] = extra_paths

        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=4)
        ct.Print.status("Success", f"Updated settings.json to include `[[COLOR_OFF]]{project_path}[[COLOR_ON]]` in python.analysis.extraPaths.")
    else:
        ct.Print.status("Success", f"`[[COLOR_OFF]]{project_path}[[COLOR_ON]]` is already in python.analysis.extraPaths.")

if __name__ == "__main__":
    ct.Print.title("Install Cure Interactive Script Begin")
    install_package()
    update_vscode_settings()
    print()
    ct.Print.title("Install Cure Interactive Script End")
    ct.Print.status("Info", "Press Enter to exit...")
    input()
