import sys
import subprocess
import json
from pathlib import Path

import cure_utility as cu

project_path = cu.Path.local()

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
        cu.Print.status("Error", f"checking package location: `[[COLOR_OFF]]{e}[[COLOR_ON]]`")
    return None

def uninstall_package(package_name):
    """
    Uninstall the package if it is already installed.
    """
    try:
        cu.Print.status("Info", f"Uninstalling existing package: `[[COLOR_OFF]]{package_name}[[COLOR_ON]]`")
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package_name])
        cu.Print.status("Success", "Package uninstalled successfully.")
    except subprocess.CalledProcessError as e:
        cu.Print.status("Error", f"uninstalling the package: `[[COLOR_OFF]]{e}[[COLOR_ON]]`")
        sys.exit(1)

def install_package():
    package_name = "cure_utility"
    project_path = str(Path(__file__).parent.resolve())
    installed_path = get_installed_package_location(package_name)

    cu.Print.status("Info", f"Project path: `[[COLOR_OFF]]{project_path}[[COLOR_ON]]`\n")
    if installed_path:
        # Resolve paths to handle case and separator differences
        installed_path_resolved = str(Path(installed_path).resolve())
        project_path_resolved = str(Path(project_path).resolve())

        cu.Print.status("Notice", f"Detected installed package path: `[[COLOR_OFF]]{installed_path_resolved}[[COLOR_ON]]`\n")
    else:
        cu.Print.status("Notice", "No install package detected.\n")
        installed_path_resolved = None
        project_path_resolved = project_path

    # Compare the resolved paths
    if installed_path_resolved == project_path_resolved:
        cu.Print.status("Success", f"`[[COLOR_OFF]]{package_name}[[COLOR_ON]]` is already installed in editable mode at `[[COLOR_OFF]]{project_path}[[COLOR_ON]]`. Skipping installation.")
    else:
        cu.Print.status("Notice", "Detected installed package path not up to date.\n")

        if installed_path_resolved:
            uninstall_package(package_name)

        python_executable = sys.executable
        command = [python_executable, "-m", "pip", "install", "-e", project_path]

        cu.Print.status("Info", f"Running command: `[[COLOR_OFF]]{' '.join(command)}[[COLOR_ON]]`")

        try:
            subprocess.check_call(command)
            cu.Print.status("Success", "Package installed successfully in editable mode.")
        except subprocess.CalledProcessError as e:
            cu.Print.status("Error", f"An error occurred while installing the package: `[[COLOR_OFF]]{e}[[COLOR_ON]]`")
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
        cu.Print.status("Notice", "VS Code settings.json file not found.")
        return

    with open(settings_path, "r") as f:
        try:
            settings = json.load(f)
        except json.JSONDecodeError:
            cu.Print.status("Error", "Invalid JSON format in settings.json.")
            return

    extra_paths = settings.get("python.analysis.extraPaths", [])
    if not isinstance(extra_paths, list):
        extra_paths = []

    project_folder_name = Path(project_path).name  # Get the last directory name (e.g., "my_project")

    # Remove entries ending with the same folder name but not exactly matching `project_path`
    updated_paths = [
        path for path in extra_paths 
        if not (Path(path).name == project_folder_name and path != project_path)
    ]
    
    # Add `project_path` if it’s not in the updated list
    if project_path not in updated_paths:
        updated_paths.append(project_path)
    
    # Update settings only if there were changes
    if extra_paths != updated_paths:
        settings["python.analysis.extraPaths"] = updated_paths
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=4)
        cu.Print.status("Success", f"Updated settings.json to include `[[COLOR_OFF]]{project_path}[[COLOR_ON]]` and removed paths ending in '{project_folder_name}' that did not exactly match.")
    else:
        cu.Print.status("Success", f"`[[COLOR_OFF]]{project_path}[[COLOR_ON]]` is already in python.analysis.extraPaths with no similar folder duplicates.")

if __name__ == "__main__":
    cu.Print.title("Install Cure Interactive Script Begin")
    install_package()
    update_vscode_settings()
    print()
    cu.Print.title("Install Cure Interactive Script End")
    cu.Print.status("Info", "Press Enter to exit...")
    input()
