# Installation Guide for Cure Utility

## Overview
This repository includes a package named `cure_utility` and a script, `install_package.py`, to facilitate its installation. The package is installed in editable mode for easy development and testing.

---

## Prerequisites
Before proceeding, ensure you have the following:
- **Python**: Version 3.6 or later
- **pip**: Installed and up-to-date
- **VS Code (optional)**: If you're using Visual Studio Code, the script can automatically update the Python analysis paths.

---

## Installation Steps

1. **Clone or Download the Repository**:
   Ensure you have the repository files locally.

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Run the Installation Script**:
   Execute the `install_package.py` script to install the `cure_utility` package in editable mode.

   ```bash
   python install_package.py
   ```

   The script performs the following:
   - Checks if the package is already installed.
   - Uninstalls the package if an outdated version is detected.
   - Installs the package in editable mode.

3. **Update VS Code Settings (Optional)**:
   If you use Visual Studio Code, the script automatically updates your `settings.json` file to include the project directory in `python.analysis.extraPaths`. This ensures that VS Code can properly analyze the package and provide autocompletions.

4. **Verify Installation**:
   After running the script, verify the package installation:

   ```bash
   python -m pip show cure_utility
   ```

   You should see details of the installed package.

---

## Additional Notes
- If the installation fails, the script provides error messages and logs to assist with troubleshooting.
- To uninstall the package manually, run:

   ```bash
   python -m pip uninstall cure_utility
   ```

---

## Contact
For questions or issues, please refer to the repository's issue tracker or contact the maintainers.
