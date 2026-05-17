#!/bin/bash
set -e

# ============================================================
# LCTemp AppImage Build Script
# Bu script LCTemp'i AppImage formatında paketler
# pip gerektirmez - sistem paketlerinden kopyalama yapar
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build-appimage"
APPDIR="$BUILD_DIR/LCTemp.AppDir"
ARCH="$(uname -m)"
VERSION="1.0.0"

echo "============================================"
echo "  LCTemp AppImage Builder v${VERSION}"
echo "  Mimari: ${ARCH}"
echo "============================================"
echo ""

# Gerekli araçları kontrol et
check_dependencies() {
    local missing=()
    
    if ! command -v python3 &>/dev/null; then
        missing+=("python3")
    fi
    
    if ! command -v wget &>/dev/null && ! command -v curl &>/dev/null; then
        missing+=("wget veya curl")
    fi
    
    # Tkinter kontrolü
    if ! python3 -c "import tkinter" &>/dev/null 2>&1; then
        missing+=("python3-tk (tkinter)")
    fi
    
    # Pillow kontrolü
    if ! python3 -c "from PIL import Image" &>/dev/null 2>&1; then
        missing+=("python-pillow (Pillow)")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo "HATA: Eksik bağımlılıklar: ${missing[*]}"
        echo ""
        echo "Arch Linux için:"
        echo "  sudo pacman -S python tk python-pillow"
        echo ""
        echo "Ubuntu/Debian için:"
        echo "  sudo apt install python3 python3-tk python3-pil"
        exit 1
    fi
    
    echo "✓ Tüm bağımlılıklar mevcut"
}

# Temizle
cleanup() {
    echo ""
    echo "[1/6] Önceki build temizleniyor..."
    rm -rf "$BUILD_DIR"
    mkdir -p "$APPDIR"
}

# AppDir yapısını oluştur
create_appdir_structure() {
    echo "[2/6] AppDir yapısı oluşturuluyor..."
    
    mkdir -p "$APPDIR/usr/bin"
    mkdir -p "$APPDIR/usr/lib"
    mkdir -p "$APPDIR/usr/app"
    mkdir -p "$APPDIR/usr/share/applications"
    mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
    mkdir -p "$APPDIR/usr/share/metainfo"
}

# Uygulama dosyalarını kopyala
copy_app_files() {
    echo "[3/6] Uygulama dosyaları kopyalanıyor..."
    
    # Ana uygulama
    cp "$SCRIPT_DIR/lctemp_monitor.py" "$APPDIR/usr/app/"
    
    # İkon
    if [ -f "$SCRIPT_DIR/lctemp.png" ]; then
        cp "$SCRIPT_DIR/lctemp.png" "$APPDIR/lctemp.png"
        cp "$SCRIPT_DIR/lctemp.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/lctemp.png"
        cp "$SCRIPT_DIR/lctemp.png" "$APPDIR/.DirIcon"
        echo "  ✓ İkon kopyalandı"
    else
        echo "  ⚠ lctemp.png bulunamadı, varsayılan ikon oluşturuluyor..."
        python3 -c "
from PIL import Image, ImageDraw
img = Image.new('RGBA', (256, 256), (30, 30, 30, 255))
draw = ImageDraw.Draw(img)
draw.rounded_rectangle([100, 40, 156, 200], radius=10, fill=(0, 200, 0), outline='white', width=3)
draw.ellipse([88, 180, 168, 230], fill=(220, 20, 60), outline='white', width=3)
img.save('$APPDIR/lctemp.png')
img.save('$APPDIR/usr/share/icons/hicolor/256x256/apps/lctemp.png')
img.save('$APPDIR/.DirIcon')
" 2>/dev/null || echo "  ⚠ İkon oluşturulamadı, devam ediliyor..."
    fi
    
    # Desktop dosyası (AppImage için)
    cat > "$APPDIR/lctemp.desktop" << 'DESKTOP'
[Desktop Entry]
Name=LCTemp
Name[tr]=LCTemp
GenericName=CPU Temperature Monitor
GenericName[tr]=CPU Sıcaklık Monitörü
Comment=Monitor CPU temperature on Linux
Comment[tr]=Linux'ta CPU sıcaklığını izleyin
Exec=AppRun
Icon=lctemp
Terminal=false
Type=Application
Categories=System;Monitor;Utility;
Keywords=temperature;cpu;monitor;sensor;hardware;
Keywords[tr]=sıcaklık;işlemci;monitör;sensör;donanım;
StartupNotify=true
X-AppImage-Version=1.0.0
DESKTOP
    cp "$APPDIR/lctemp.desktop" "$APPDIR/usr/share/applications/lctemp.desktop"
    
    # AppRun
    cat > "$APPDIR/AppRun" << 'APPRUN'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export PYTHONPATH="${HERE}/usr/lib/python3/site-packages:${HERE}/usr/lib/python3:${PYTHONPATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export TCL_LIBRARY="${HERE}/usr/lib/tcl8.6"
export TK_LIBRARY="${HERE}/usr/lib/tk8.6"

exec "${HERE}/usr/bin/python3" "${HERE}/usr/app/lctemp_monitor.py" "$@"
APPRUN
    chmod +x "$APPDIR/AppRun"
    
    # AppStream metainfo
    cat > "$APPDIR/usr/share/metainfo/com.github.efebalikci5.lctemp.appdata.xml" << 'METAINFO'
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>com.github.efebalikci5.lctemp</id>
  <name>LCTemp</name>
  <summary>CPU Temperature Monitor for Linux</summary>
  <metadata_license>FSFAP</metadata_license>
  <project_license>GPL-2.0</project_license>
  <description>
    <p>LCTemp is a GUI-based CPU temperature monitoring application for Intel and AMD processors on Linux systems.</p>
  </description>
  <url type="homepage">https://github.com/Efebalikci5/LCTemp</url>
  <url type="bugtracker">https://github.com/Efebalikci5/LCTemp/issues</url>
  <launchable type="desktop-id">lctemp.desktop</launchable>
  <releases>
    <release version="1.0.0" date="2026-05-12"/>
  </releases>
</component>
METAINFO
    echo "  ✓ Desktop ve metainfo dosyaları oluşturuldu"
}

# Python ortamını paketle
bundle_python() {
    echo "[4/6] Python ortamı paketleniyor..."
    
    PYTHON_BIN="$(which python3)"
    PYTHON_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    PYTHON_PREFIX="$(python3 -c 'import sys; print(sys.prefix)')"
    
    echo "  Python: $PYTHON_BIN (sürüm $PYTHON_VERSION)"
    
    # Python binary kopyala
    cp "$PYTHON_BIN" "$APPDIR/usr/bin/python3"
    chmod +x "$APPDIR/usr/bin/python3"
    
    # Python standart kütüphanesini bul
    PYTHON_LIB=""
    for candidate in \
        "$PYTHON_PREFIX/lib/python${PYTHON_VERSION}" \
        "/usr/lib/python${PYTHON_VERSION}" \
        "/usr/lib64/python${PYTHON_VERSION}"; do
        if [ -d "$candidate" ]; then
            PYTHON_LIB="$candidate"
            break
        fi
    done
    
    if [ -z "$PYTHON_LIB" ]; then
        echo "HATA: Python standart kütüphanesi bulunamadı!"
        exit 1
    fi
    
    echo "  Stdlib: $PYTHON_LIB"
    
    # Standart kütüphaneyi kopyala (gereksizleri hariç tut)
    mkdir -p "$APPDIR/usr/lib/python${PYTHON_VERSION}"
    
    if command -v rsync &>/dev/null; then
        rsync -a --quiet \
            --exclude='test/' \
            --exclude='tests/' \
            --exclude='__pycache__/' \
            --exclude='*.pyc' \
            --exclude='ensurepip/' \
            --exclude='idlelib/' \
            --exclude='turtle*' \
            --exclude='turtledemo/' \
            --exclude='pydoc*' \
            --exclude='doctest*' \
            --exclude='unittest/' \
            --exclude='lib2to3/' \
            --exclude='venv/' \
            "$PYTHON_LIB/" "$APPDIR/usr/lib/python${PYTHON_VERSION}/"
    else
        cp -r "$PYTHON_LIB"/* "$APPDIR/usr/lib/python${PYTHON_VERSION}/"
    fi
    echo "  ✓ Python stdlib kopyalandı"
    
    # _tkinter.so'yu bul ve kopyala
    TKINTER_SO="$(python3 -c 'import _tkinter; print(_tkinter.__file__)' 2>/dev/null || true)"
    if [ -n "$TKINTER_SO" ] && [ -f "$TKINTER_SO" ]; then
        DYNLOAD_DIR="$APPDIR/usr/lib/python${PYTHON_VERSION}/lib-dynload"
        mkdir -p "$DYNLOAD_DIR"
        cp "$TKINTER_SO" "$DYNLOAD_DIR/" 2>/dev/null || true
        echo "  ✓ _tkinter.so kopyalandı"
    fi
    
    # TCL/TK kütüphanelerini kopyala
    TCL_FOUND=false
    for tcl_dir in /usr/share/tcltk/tcl8.6 /usr/lib/tcl8.6 /usr/share/tcl8.6 /usr/lib/tcl8 /usr/share/tcl; do
        if [ -d "$tcl_dir" ]; then
            cp -r "$tcl_dir" "$APPDIR/usr/lib/tcl8.6" 2>/dev/null || true
            TCL_FOUND=true
            break
        fi
    done
    # Arch Linux: TCL/TK /usr/lib/tcl8.6 altında olmayabilir
    if [ "$TCL_FOUND" = false ]; then
        # tcl paketi yolunu bul
        TCL_AUTO="$(python3 -c 'import tkinter; root=tkinter.Tk(); print(root.tk.eval("info library")); root.destroy()' 2>/dev/null || true)"
        if [ -n "$TCL_AUTO" ] && [ -d "$TCL_AUTO" ]; then
            cp -r "$TCL_AUTO" "$APPDIR/usr/lib/tcl8.6" 2>/dev/null || true
            echo "  ✓ TCL kopyalandı: $TCL_AUTO"
        fi
    else
        echo "  ✓ TCL kopyalandı"
    fi
    
    TK_FOUND=false
    for tk_dir in /usr/share/tcltk/tk8.6 /usr/lib/tk8.6 /usr/share/tk8.6 /usr/lib/tk8 /usr/share/tk; do
        if [ -d "$tk_dir" ]; then
            cp -r "$tk_dir" "$APPDIR/usr/lib/tk8.6" 2>/dev/null || true
            TK_FOUND=true
            break
        fi
    done
    if [ "$TK_FOUND" = false ]; then
        TK_AUTO="$(python3 -c 'import tkinter; root=tkinter.Tk(); print(root.tk.eval("info library").replace("tcl","tk")); root.destroy()' 2>/dev/null || true)"
        if [ -n "$TK_AUTO" ] && [ -d "$TK_AUTO" ]; then
            cp -r "$TK_AUTO" "$APPDIR/usr/lib/tk8.6" 2>/dev/null || true
            echo "  ✓ TK kopyalandı: $TK_AUTO"
        fi
    else
        echo "  ✓ TK kopyalandı"
    fi
    
    # Sistem site-packages'tan bağımlılıkları kopyala (pip gerektirmez!)
    echo "  Sistem site-packages'tan bağımlılıklar kopyalanıyor..."
    SITE_PACKAGES_DIR="$APPDIR/usr/lib/python${PYTHON_VERSION}/site-packages"
    mkdir -p "$SITE_PACKAGES_DIR"
    
    # Pillow'u bul ve kopyala
    PIL_PATH="$(python3 -c 'import PIL; import os; print(os.path.dirname(PIL.__file__))' 2>/dev/null || true)"
    if [ -n "$PIL_PATH" ] && [ -d "$PIL_PATH" ]; then
        cp -r "$PIL_PATH" "$SITE_PACKAGES_DIR/" 2>/dev/null || true
        echo "  ✓ Pillow kopyalandı: $PIL_PATH"
    fi
    
    # pystray'ı bul ve kopyala (opsiyonel)
    PYSTRAY_PATH="$(python3 -c 'import pystray; import os; print(os.path.dirname(pystray.__file__))' 2>/dev/null || true)"
    if [ -n "$PYSTRAY_PATH" ] && [ -d "$PYSTRAY_PATH" ]; then
        cp -r "$PYSTRAY_PATH" "$SITE_PACKAGES_DIR/" 2>/dev/null || true
        echo "  ✓ pystray kopyalandı"
        
        # pystray bağımlılıkları: six, xlib vb.
        for dep_mod in six xlib; do
            DEP_PATH="$(python3 -c "import ${dep_mod}; import os; print(os.path.dirname(${dep_mod}.__file__) if hasattr(${dep_mod}, '__file__') and os.path.isdir(os.path.dirname(${dep_mod}.__file__)) else ${dep_mod}.__file__)" 2>/dev/null || true)"
            if [ -n "$DEP_PATH" ]; then
                if [ -d "$DEP_PATH" ]; then
                    cp -r "$DEP_PATH" "$SITE_PACKAGES_DIR/" 2>/dev/null || true
                elif [ -f "$DEP_PATH" ]; then
                    cp "$DEP_PATH" "$SITE_PACKAGES_DIR/" 2>/dev/null || true
                fi
            fi
        done
    else
        echo "  ⚠ pystray bulunamadı (sistem tepsisi desteği olmadan devam edilecek)"
    fi
    
    # Paylaşılan kütüphaneleri kopyala
    echo "  Paylaşılan kütüphaneler kopyalanıyor..."
    
    # libpython
    LIBPYTHON_DIR="$(python3 -c 'import sysconfig; print(sysconfig.get_config_var("LIBDIR"))' 2>/dev/null || echo '/usr/lib')"
    for libpy in "$LIBPYTHON_DIR"/libpython${PYTHON_VERSION}*.so*; do
        if [ -f "$libpy" ]; then
            cp "$libpy" "$APPDIR/usr/lib/" 2>/dev/null || true
        fi
    done
    
    # TCL/TK shared libs
    for lib in tcl tk; do
        LIB_PATH="$(ldconfig -p 2>/dev/null | grep "lib${lib}8" | head -1 | awk '{print $NF}')"
        if [ -n "$LIB_PATH" ] && [ -f "$LIB_PATH" ]; then
            cp "$LIB_PATH" "$APPDIR/usr/lib/" 2>/dev/null || true
        fi
    done
    
    # Pillow'un .so bağımlılıkları
    if [ -d "$SITE_PACKAGES_DIR/PIL" ]; then
        for so_file in "$SITE_PACKAGES_DIR/PIL"/*.so; do
            if [ -f "$so_file" ]; then
                ldd "$so_file" 2>/dev/null | grep "=>" | awk '{print $3}' | while read -r dep; do
                    if [ -f "$dep" ] && [[ "$dep" != /lib* ]] && [[ "$dep" != /usr/lib/libc* ]] && [[ "$dep" != /usr/lib/libm* ]] && [[ "$dep" != /usr/lib/libpthread* ]] && [[ "$dep" != /usr/lib/libdl* ]]; then
                        cp "$dep" "$APPDIR/usr/lib/" 2>/dev/null || true
                    fi
                done
            fi
        done
    fi
    
    echo "  ✓ Paylaşılan kütüphaneler kopyalandı"
    
    # Symlink oluştur
    cd "$APPDIR/usr/lib" && ln -sf "python${PYTHON_VERSION}" "python3" 2>/dev/null || true
}

# appimagetool'u indir ve AppImage oluştur
build_appimage() {
    echo "[5/6] appimagetool indiriliyor..."
    
    APPIMAGETOOL="$BUILD_DIR/appimagetool"
    
    if [ ! -f "$APPIMAGETOOL" ]; then
        TOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-${ARCH}.AppImage"
        
        if command -v wget &>/dev/null; then
            wget -q --show-progress "$TOOL_URL" -O "$APPIMAGETOOL"
        else
            curl -L --progress-bar "$TOOL_URL" -o "$APPIMAGETOOL"
        fi
        
        chmod +x "$APPIMAGETOOL"
        echo "  ✓ appimagetool indirildi"
    fi
    
    echo "[6/6] AppImage oluşturuluyor..."
    
    OUTPUT_FILE="$SCRIPT_DIR/LCTemp-${VERSION}-${ARCH}.AppImage"
    
    # FUSE kontrolü ve build
    if "$APPIMAGETOOL" --version &>/dev/null 2>&1; then
        "$APPIMAGETOOL" "$APPDIR" "$OUTPUT_FILE"
    else
        echo "  FUSE bulunamadı, extract modunda çalışılıyor..."
        APPIMAGE_EXTRACT_AND_RUN=1 "$APPIMAGETOOL" "$APPDIR" "$OUTPUT_FILE" 2>/dev/null || \
        "$APPIMAGETOOL" --appimage-extract-and-run "$APPDIR" "$OUTPUT_FILE"
    fi
    
    chmod +x "$OUTPUT_FILE"
    
    echo ""
    echo "============================================"
    echo "  ✅ AppImage başarıyla oluşturuldu!"
    echo "  📦 Dosya: $OUTPUT_FILE"
    echo "  📏 Boyut: $(du -h "$OUTPUT_FILE" | cut -f1)"
    echo "============================================"
    echo ""
    echo "Çalıştırmak için:"
    echo "  chmod +x $(basename "$OUTPUT_FILE")"
    echo "  ./$(basename "$OUTPUT_FILE")"
}

# Ana akış
main() {
    check_dependencies
    cleanup
    create_appdir_structure
    copy_app_files
    bundle_python
    build_appimage
    
    # Build dizinini temizle
    rm -rf "$BUILD_DIR"
    echo "Build dizini temizlendi."
}

main "$@"
