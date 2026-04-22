# Butterwalk Linux (Improved Movement)

A movement utility for Darkages players on Linux.
This tool monitors physical keyboard input and injects movement commands directly into the game window for a "buttery" smooth experience.

## Prerequisites
- **Python 3.8+**
- **xdotool:** Used for injecting keystrokes.
  - Ubuntu/Debian: `sudo apt install xdotool`
  - Fedora: `sudo dnf install xdotool`
  - Arch: `sudo pacman -S xdotool`

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/phever/butterwalk.git
cd butterwalk
```

### 2. Set Up Permissions
The script needs to read keyboard events globally. It is recommended to add your user to the `input` group so you don't have to run the script as root.
```bash
chmod +x setup_permissions.sh
sudo ./setup_permissions.sh
```
**Note:** You MUST log out and log back in (or restart) after running this for changes to take effect.

### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

## How to Run

Always ensure your virtual environment is active before running:
```bash
source venv/bin/activate
python improved_walk.py
```

## Controls
| Key | Action |
| :--- | :--- |
| `Arrows` | Movement |
| `ZXCV` | Movement (if enabled) |
| `+` / `-` | Increase / Decrease Speed Level |
| `m` | Toggle ZXCV Movement |
| `q` | Exit |

## Troubleshooting
- **"Permission denied for /dev/input/":** Ensure you ran the `setup_permissions.sh` script AND restarted your session.
- **"Client: Not Found":** Ensure the Darkages window is open and has "Darkages" in the title. (Can update with additional keywords if needed in `improved_walk.py`)
- **No Movement In-Game:** Ensure `xdotool` is installed on your system.
