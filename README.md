# LCTemp - Linux Control Temp

LCTemp is a GUI-based CPU temperature monitoring application for Intel and AMD processors on Linux-based systems.

## Features

- **CPU Temperature Monitoring**: Reading temperatures from Intel (coretemp) and AMD (k10temp, zen) sensors
- **Core Monitoring**: Displaying temperatures of all CPU cores
- **CPU Usage Rate**: Real-time processor usage percentage
- **Max/Min Monitoring**: Recording highest and lowest CPU usage values
- **System Type Support**:
  - Desktop
  - Laptop - Battery power and charging status
- **Fan Speed**: Displaying current fan RPM values (requires hardware support)
- **Theme Support**: Dark and Light themes
- **Language Support**: Turkish and English
- **System Tray** (Beta): Temperature indicator on Cinnamon and KDE desktops
- **Settings Persistence**: User settings are automatically saved

## Supported Sensors

- `coretemp` - Intel processors
- `k10temp` - AMD processors (older)
- `zen` - AMD Ryzen series
- `cpu` - General CPU sensors
- `k8temp` - AMD older generation
- `cputemp` - Alternative sensor

## Requirements

- Python 3.8+
- Linux kernel (hwmon support)
- tkinter (usually comes with Python)
- pystray (for system tray)
- Pillow (for image processing)

## Temperature Thresholds

| Status | Temperature |
|--------|-------------|
| Normal | < 50°C |
| High | 50-70°C |
| Very High | 70-85°C |
| Critical | > 85°C |

## License

This project is licensed under the GNU General Public License v2.0 (GPL-2.0) - see the [LICENSE](LICENSE) file for details.
