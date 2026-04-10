# LCTemp - Installation Guide

## Requirements

### Basic Dependencies

| Dependency | Version | Description |
|------------|---------|-------------|
| Python | 3.8+ | Required for the application to run |
| tkinter | - | GUI library (comes with Python) |
| pystray | 0.19+ | System tray support |
| Pillow | 9.0+ | Image processing library |

### System Requirements

- **Linux Kernel**: hwmon support (for temperature sensors)
- **Desktop Environment**: Cinnamon, KDE, GNOME, XFCE, MATE, or others
- **Sensor Support**: lm-sensors package must be installed

## Installation Methods

### 1. Debian/Ubuntu Package Installation (Recommended)

```bash
# Download the package
wget https://github.com/Efebalikci5/LCTemp/releases/latest/download/lctemp.deb

# Install the package
sudo dpkg -i lctemp.deb

# Fix missing dependencies (if needed)
sudo apt-get install -f
```

### 2. Installation from Source Code

```bash
# Clone the repository
git clone https://github.com/Efebalikci5/LCTemp.git
cd LCTemp

# Install dependencies
pip3 install -r lctemp_requirements.txt

# Run the application
python3 lctemp_monitor.py
```

### 3. Manual Dependency Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-tk python3-pip
pip3 install pystray Pillow

# Fedora
sudo dnf install python3-tkinter python3-pip
pip3 install pystray Pillow

# Arch Linux
sudo pacman -S tk python-pip
pip3 install pystray Pillow

# openSUSE
sudo zypper install python3-tk python3-pip
pip3 install pystray Pillow
```

## Desktop Integration

### Making the Application Executable

```bash
# Give execution permission to the application
sudo chmod +x /usr/bin/lctemp

# Or for source code installation
chmod +x lctemp_monitor.py
```

### Creating Desktop Shortcut

```bash
# Copy the .desktop file
sudo cp LCTemp.desktop /usr/share/applications/

# Or for user-level installation
mkdir -p ~/.local/share/applications
cp LCTemp.desktop ~/.local/share/applications/
```

### Starting the Application

```bash
# Run from terminal
lctemp

# Or
python3 /usr/bin/lctemp

# Or start from the application menu in your desktop environment
```

## Troubleshooting

### 1. Tkinter Error

**Error Message:**
```
ERROR: Tkinter library not found!
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk

# openSUSE
sudo zypper install python3-tk
```

### 2. Sensor Not Found Error

**Error Message:**
```
Sensor not found!
```

**Solution:**
```bash
# Install lm-sensors package
sudo apt install lm-sensors  # Ubuntu/Debian
sudo dnf install lm_sensors  # Fedora
sudo pacman -S lm_sensors    # Arch Linux

# Detect sensors
sudo sensors-detect

# Reboot to apply changes
sudo reboot
```

### 3. pystray Installation Error

**Error Message:**
```
ModuleNotFoundError: No module named 'pystray'
```

**Solution:**
```bash
# Install with pip
pip3 install pystray

# If pip is not installed, install pip first
sudo apt install python3-pip  # Ubuntu/Debian
sudo dnf install python3-pip  # Fedora
```

### 4. Pillow Installation Error

**Error Message:**
```
ModuleNotFoundError: No module named 'PIL'
```

**Solution:**
```bash
# Install Pillow
pip3 install Pillow

# If error persists
pip3 install --upgrade Pillow
```

### 5. System Tray Not Working

**Problem:** System tray icon is not visible

**Solution:**
- System tray only works on **Cinnamon** and **KDE** desktops
- System tray support is limited on GNOME, XFCE, and MATE
- Some errors may occur as it is in beta stage

### 6. Permission Error

**Error Message:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Give access permission to sensor files
sudo chmod 644 /sys/class/hwmon/hwmon*/temp*_input

# Or run the application with sudo (not recommended)
sudo python3 lctemp_monitor.py
```

### 7. Python Version Incompatibility

**Error Message:**
```
SyntaxError: invalid syntax
```

**Solution:**
```bash
# Check your Python version
python3 --version

# If lower than 3.8, update Python
sudo apt install python3.10  # Ubuntu/Debian
```

### 8. dpkg Error (Debian Package)

**Error Message:**
```
dpkg: error processing archive lctemp.deb
```

**Solution:**
```bash
# Fix missing dependencies
sudo apt-get install -f

# Reinstall the package
sudo dpkg -i lctemp.deb
```

## Verification

To verify that the application is working correctly after installation:

```bash
# Run the application
lctemp

# Or
python3 /usr/bin/lctemp
```

Successful installation:
- GUI window will open
- Temperature values will be displayed
- System tray icon will appear (Cinnamon/KDE)

## Uninstallation

### Uninstalling Debian Package
```bash
sudo dpkg -r lctemp
```

### Uninstalling from Source Code
```bash
# Delete the cloned directory
rm -rf LCTemp
```

## Support

If you encounter issues:
- GitHub Issues: https://github.com/Efebalikci5/LCTemp/issues
- Email: efebalikci9@gmail.com
