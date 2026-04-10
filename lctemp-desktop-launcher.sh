#!/bin/bash
# LCTemp Desktop Launcher

# Script'in bulunduğu dizini kesin olarak tespit et
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Wayland ortamlarında Tkinter penceresinin görünmeme sorununu engellemek için X11'i zorla
export GDK_BACKEND=x11

# Uygulamayı çalıştır
python3 lctemp_monitor.py
