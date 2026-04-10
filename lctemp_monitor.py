#!/usr/bin/env python3
"""
LCTemp - Linux Control Temp
Intel ve AMD işlemciler için görsel arayüzlü sıcaklık izleme uygulaması
"""

import os
import sys
import glob
import time
import json

# Tkinter bağımlılığını güvenli yakalama
try:
    import tkinter as tk
    from tkinter import font as tkfont
    from tkinter import messagebox
except ImportError:
    print("\n" + "="*60)
    print("HATA: Tkinter kütüphanesi bulunamadı!")
    print("="*60)
    print("\nBu uygulama Tkinter gerektirir ancak sisteminizde yüklü değil.")
    print("\nUbuntu/Kubuntu için şu komutu çalıştırın:")
    print("  sudo apt update && sudo apt install python3-tk")
    print("\nDiğer dağıtımlar için:")
    print("  - Fedora: sudo dnf install python3-tkinter")
    print("  - Arch Linux: sudo pacman -S tk")
    print("  - openSUSE: sudo zypper install python3-tk")
    print("\nKurulumdan sonra uygulamayı tekrar çalıştırın.")
    print("="*60 + "\n")
    sys.exit(1)

# Sistem tepsisi için pystray
try:
    from pystray import MenuItem as Item
    import pystray
    from PIL import Image, ImageDraw, ImageFont
    PYSTRAY_AVAILABLE = True
except (ImportError, ValueError) as e:
    PYSTRAY_AVAILABLE = False


def detect_desktop_environment():
    """Masaüstü ortamını algılar (Cinnamon, KDE, vb.)"""
    xdg_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()
    
    # Cinnamon kontrolü
    if 'cinnamon' in xdg_desktop or 'cinnamon' in desktop_session:
        return 'cinnamon'
    
    # KDE/Plasma kontrolü
    if 'kde' in xdg_desktop or 'plasma' in xdg_desktop or 'kde' in desktop_session:
        return 'kde'
    
    # GNOME kontrolü
    if 'gnome' in xdg_desktop or 'gnome' in desktop_session:
        return 'gnome'
    
    # XFCE kontrolü
    if 'xfce' in xdg_desktop or 'xfce' in desktop_session:
        return 'xfce'
    
    # MATE kontrolü
    if 'mate' in xdg_desktop or 'mate' in desktop_session:
        return 'mate'
    
    return 'unknown'


class LCTemp:
    """CPU sıcaklık izleme uygulaması - LCTemp"""
    
    # Desteklenen sensör isimleri
    SUPPORTED_SENSORS = ['coretemp', 'k10temp', 'cpu', 'k8temp', 'zen', 'cputemp']
    
    # Sıcaklık eşik değerleri
    TEMP_THRESHOLDS = {
        'cool': 50,
        'warm': 70,
        'hot': 85
    }
    
    # Tema renkleri
    THEMES = {
        'dark': {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'fg_secondary': '#aaaaaa',
            'fg_muted': '#666666',
            'border': '#444444',
            'progress_bg': '#333333',
            'input_bg': '#2d2d2d'
        },
        'light': {
            'bg': '#f5f5f5',
            'fg': '#1e1e1e',
            'fg_secondary': '#555555',
            'fg_muted': '#888888',
            'border': '#cccccc',
            'progress_bg': '#e0e0e0',
            'input_bg': '#ffffff'
        }
    }
    
    LANGUAGES = {
        'tr': {
            'title': '🖥️ Linux Control Temp',
            'temp': '°C',
            'cpu': 'İşlemci',
            'cores': 'Çekirdekler',
            'max': 'Max',
            'min': 'Min',
            'sensor_wait': 'Sensör bekleniyor...',
            'sensor_found': 'Sensör bulundu',
            'sensor_not_found': 'Sensör bulunamadı!',
            'data_unavailable': 'Veri alınamıyor',
            'normal': 'Normal',
            'warm': 'Yüksek',
            'hot': 'Çok Yüksek',
            'critical': 'Kritik!',
            'single_core': 'Tek çekirdek/hybrid',
            'show_tray': 'Sistem tepsisinde göster (Beta - Cinnamon/KDE)',
            'menu_file': 'Dosya',
            'menu_refresh': 'Yenile',
            'menu_exit': 'Çıkış',
            'menu_settings': 'Ayarlar',
            'menu_theme': 'Tema',
            'menu_language': 'Dil',
            'menu_dark': 'Koyu',
            'menu_light': 'Açık',
            'menu_reset_minmax': 'Min/Max Sıfırla',
            'menu_interval': 'Okuma Aralığı',
            'menu_display': 'Görüntüleme Seçenekleri',
            'menu_fan_speed': 'Fan Hızı',
            'menu_battery': 'Pil Gücü (Laptop)',
            'menu_cpu_usage': 'İşlemci Kullanımı',
            'menu_cores': 'Çekirdekler',
            'menu_about': 'Hakkında',
            'about_title': 'LCTemp - Hakkında',
            'about_text': 'LCTemp - Linux Control Temp\n\nVersiyon: 1.0.0\n\nefebalikci9@gmail.com\nhttps://github.com/Efebalikci5/LCTemp\n\nÖzellikler:\n• Linux\'ta işlemci sıcaklığı ölçme\n• İşlemci kullanım oranı görüntüleme\n• İşlemcinin max ve min kullanım oranını görüntüleme\n• KDE ve Cinnamon masaüstüleri için sistem tepsisinden sıcaklık kontrolü (Geliştirme aşamasında)'
        },
        'en': {
            'title': '🖥️ Linux Control Temp',
            'temp': '°C',
            'cpu': 'CPU',
            'cores': 'Cores',
            'max': 'Max',
            'min': 'Min',
            'sensor_wait': 'Waiting for sensor...',
            'sensor_found': 'Sensor found',
            'sensor_not_found': 'Sensor not found!',
            'data_unavailable': 'Data unavailable',
            'normal': 'Normal',
            'warm': 'Warm',
            'hot': 'Very Hot',
            'critical': 'Critical!',
            'single_core': 'Single/hybrid core',
            'show_tray': 'Show in system tray (Beta - Cinnamon/KDE)',
            'menu_file': 'File',
            'menu_refresh': 'Refresh',
            'menu_exit': 'Exit',
            'menu_settings': 'Settings',
            'menu_theme': 'Theme',
            'menu_language': 'Language',
            'menu_dark': 'Dark',
            'menu_light': 'Light',
            'menu_reset_minmax': 'Reset Min/Max',
            'menu_interval': 'Reading Interval',
            'menu_display': 'Display Options',
            'menu_fan_speed': 'Fan Speed',
            'menu_battery': 'Battery Power (Laptop)',
            'menu_cpu_usage': 'CPU Usage',
            'menu_cores': 'Cores',
            'menu_about': 'About',
            'about_title': 'LCTemp - About',
            'about_text': 'LCTemp - Linux Control Temp\n\nVersion: 1.0.0\n\nefebalikci9@gmail.com\nhttps://github.com/Efebalikci5/LCTemp\n\nFeatures:\n• CPU temperature measurement on Linux\n• CPU usage percentage display\n• CPU max and min usage rate display\n• System tray temperature monitoring for KDE and Cinnamon desktops (In Development)'
        }
    }
    def __init__(self, root):
        self.root = root
        self.sensor_path = None
        self.sensor_name = None
        self.running = True
        
        # Tema ve dil ayarları
        self.current_theme = 'dark'
        self.current_language = 'en'
        
        # Tema ve dil için radiobutton değişkenleri (sınıf düzeyinde tek örnek)
        self.theme_var = tk.StringVar(value='dark')
        self.language_var = tk.StringVar(value='en')
        
        # Okuma aralığı (saniye) - varsayılan 2 saniye
        self.read_interval = 2
        self.interval_var = tk.IntVar(value=2)
        
        # Görüntüleme seçenekleri
        self.show_cpu_usage = True
        self.show_cores = True
        self.show_fan_speed = False
        self.show_battery = False
        
        self.display_var_cpu = tk.BooleanVar(value=True)
        self.display_var_cores = tk.BooleanVar(value=True)
        self.display_var_fan = tk.BooleanVar(value=False)
        self.display_var_battery = tk.BooleanVar(value=False)
        
        # Masaüstü ortamı algılama
        self.desktop_environment = detect_desktop_environment()
        self.is_cinnamon = self.desktop_environment == 'cinnamon'
        self.is_kde = self.desktop_environment == 'kde'
        
        # Max/Min sıcaklık değerleri
        self.max_temp = None
        self.min_temp = None
        
        # CPU kullanımı için
        self.last_cpu_times = None
        self.last_cpu_idle = None
        
        # CPU frekansı için
        self.last_cpu_freq = None
        self.cpu_freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
        self.max_cpu_freq = None  # Max CPU frekansı (throttling için)
        
        # Şu anki sıcaklık
        self.current_temp = 0
        self.current_usage = 0
        
        # Sistem tepsisi
        self.system_tray_enabled = False
        self.tray_icon = None
        self.tray_var = tk.BooleanVar(value=False)  # Ortak tray checkbox değişkeni
        
        # GUI bileşenleri
        self.widgets = {}
        
        # Ayarları yükle (kullanıcının kaydettiği ayarları al)
        self.load_settings()
        
        # GUI'yi başlat
        self.setup_gui()
        self.create_menu()
        
        # Sensörü bul
        self.find_sensor()
        
        # Masaüstü ortamı hakkında bilgi yazdır
        if self.is_cinnamon or self.is_kde:
            print(f"Algılanan masaüstü ortamı: {self.desktop_environment.upper()} - Sistem tepsisi destekleniyor")
        else:
            print(f"Algılanan masaüstü ortamı: {self.desktop_environment.upper()} - Sistem tepsisi yalnızca Cinnamon/KDE'de çalışır")
        
        # Sıcaklık okuma döngüsünü başlat
        self.update_temperature()
    
    @property
    def lang(self):
        return self.LANGUAGES[self.current_language]
    
    @property
    def theme(self):
        return self.THEMES[self.current_theme]
    
    def _find_font(self, size=14):
        """Sistem fontunu bulur - Linux dağıtımından bağımsız (fc-match ile)"""
        import subprocess
        
        # fc-match ile sistemden font yolunu al
        try:
            result = subprocess.run(
                ['fc-match', '-f', '%{file}'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                font_path = result.stdout.strip()
                return ImageFont.truetype(font_path, size)
        except Exception:
            pass
        
        # fc-match başarısız olursa elle font dene
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu-sans-ttf/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
        ]
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
        # Fallback to default
        try:
            return ImageFont.load_default()
        except:
            return None

    def create_tray_icon_image(self, temp):
        """Sistem tepsisi için sıcaklık değeri gösteren ikon oluşturur"""
        if temp < self.TEMP_THRESHOLDS['cool']:
            color = (0, 200, 0)  # Yeşil
        elif temp < self.TEMP_THRESHOLDS['warm']:
            color = (255, 165, 0)  # Turuncu
        elif temp < self.TEMP_THRESHOLDS['hot']:
            color = (255, 100, 0)  # Kırmızımsı turuncu
        else:
            color = (220, 20, 60)  # Kırmızı
        
        # İkon boyutu - büyük ve okunabilir
        width, height = 64, 64
        bg_color = self.theme['bg'].lstrip('#')
        bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
        
        image = Image.new('RGB', (width, height), bg_rgb)
        draw = ImageDraw.Draw(image)
        
        # Termometre gövdesi
        draw.rectangle([26, 12, 38, 56], fill=color, outline='white', width=2)
        # Termometre başı
        draw.ellipse([22, 8, 42, 20], fill=color, outline='white', width=2)
        
        # Sıcaklık değerini ikonun alt kısmına ekle
        temp_text = f"{temp:.0f}°"
        
        # Yazı tipi ayarla - sistem fontunu bulmaya çalış
        font = self._find_font(14)
        
        # Metin pozisyonu - ikonun sağında veya altında
        if font:
            # Metin boyutunu al
            bbox = draw.textbbox((0, 0), temp_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Metni ikonun sağına veya üstüne yerleştir
            # Yeni geniş ikon - sıcaklık sağda
            x_pos = 44
            y_pos = 20
            
            # Beyaz arka plan üzerine siyah yazı
            draw.rectangle([x_pos - 2, y_pos - 2, x_pos + text_width + 2, y_pos + text_height + 2], 
                          fill='white', outline='white')
            draw.text((x_pos, y_pos), temp_text, fill='black', font=font)
        
        return image
    
    def setup_system_tray(self):
        """Sistem tepsisini kurar"""
        if not PYSTRAY_AVAILABLE:
            return
        
        try:
            icon_image = self.create_tray_icon_image(0)
            menu = (
                Item('Show', self.show_window),
                Item('Exit', self.quit_app)
            )
            self.tray_icon = pystray.Icon("LCTemp", icon_image, "LCTemp", menu)
        except Exception as e:
            print(f"Sistem tepsisi kurulum hatası: {e}")
    
    def update_system_tray(self):
        if not PYSTRAY_AVAILABLE or not self.tray_icon or not self.system_tray_enabled:
            return
        
        try:
            new_image = self.create_tray_icon_image(self.current_temp)
            self.tray_icon.icon = new_image
            tooltip_text = f"LCTemp\n{self.current_temp:.1f}°C\n{self.lang['cpu']}: {self.current_usage:.1f}%"
            self.tray_icon.title = tooltip_text
        except Exception as e:
            print(f"Sistem tepsisi güncelleme hatası: {e}")
    
    def show_window(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)
    
    def quit_app(self, icon=None, item=None):
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()
    
    def find_sensor(self):
        hwmon_base = "/sys/class/hwmon"
        
        if not os.path.exists(hwmon_base):
            self.update_status(self.lang['sensor_not_found'], "red")
            return False
        
        hwmon_dirs = glob.glob(os.path.join(hwmon_base, "hwmon*"))
        
        for hwmon_dir in sorted(hwmon_dirs):
            name_file = os.path.join(hwmon_dir, "name")
            
            try:
                if os.path.exists(name_file):
                    with open(name_file, 'r') as f:
                        sensor_name = f.read().strip()
                    
                    if sensor_name in self.SUPPORTED_SENSORS:
                        self.sensor_path = hwmon_dir
                        self.sensor_name = sensor_name
                        self.update_status(f"{self.lang['sensor_found']}: {sensor_name} ({os.path.basename(hwmon_dir)})", "green")
                        return True
                        
            except (IOError, PermissionError):
                continue
        
        self.update_status(self.lang['sensor_not_found'], "red")
        return False
    
    def read_cpu_usage(self):
        """CPU kullanımını okur - ilk okumada None döndürür"""
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
            
            fields = line.split()
            if fields[0] == 'cpu':
                times = [int(x) for x in fields[1:]]
                total = sum(times)
                idle = times[3]
                
                if self.last_cpu_times is not None:
                    delta_total = total - self.last_cpu_times
                    delta_idle = idle - self.last_cpu_idle
                    
                    if delta_total > 0:
                        usage = 100.0 * (1.0 - delta_idle / delta_total)
                        self.last_cpu_times = total
                        self.last_cpu_idle = idle
                        return round(max(0.0, min(100.0, usage)), 1)  # Clamp to 0-100
                
                # İlk okuma - değeri kaydet ama None döndür
                self.last_cpu_times = total
                self.last_cpu_idle = idle
                return None
                
        except Exception:
            pass
        
        return None
    
    def read_cpu_freq(self):
        """CPU frekansını MHz cinsinden okur"""
        try:
            # Max frekansı bul (sadece ilk okumada)
            if self.max_cpu_freq is None:
                max_freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"
                try:
                    with open(max_freq_path, 'r') as f:
                        self.max_cpu_freq = int(f.read().strip()) / 1000  # MHz
                except:
                    self.max_cpu_freq = 3000  # Varsayılan değer
            
            with open(self.cpu_freq_path, 'r') as f:
                freq_khz = int(f.read().strip())
                # MHz cinsinden dön
                return freq_khz / 1000
        except Exception:
            return None
    
    def read_temperature(self):
        if not self.sensor_path:
            return None, []
        
        try:
            temp_files = glob.glob(os.path.join(self.sensor_path, "temp*_input"))
            
            if not temp_files:
                return None, []
            
            temperatures = []
            
            for temp_file in sorted(temp_files):
                try:
                    with open(temp_file, 'r') as f:
                        temp_millidegrees = int(f.read().strip())
                        temp_celsius = temp_millidegrees / 1000.0
                        temperatures.append(temp_celsius)
                except (ValueError, IOError, PermissionError):
                    continue
            
            if not temperatures:
                return None, []
            
            package_temp = temperatures[0]
            return package_temp, temperatures
            
        except Exception:
            return None, []
    
    def update_min_max(self, temp):
        if temp is not None:
            if self.max_temp is None or temp > self.max_temp:
                self.max_temp = temp
            if self.min_temp is None or temp < self.min_temp:
                self.min_temp = temp
    
    def get_temp_color(self, temp):
        if temp is None:
            return self.theme['fg_muted']
        
        if temp < self.TEMP_THRESHOLDS['cool']:
            return "#00FF00"
        elif temp < self.TEMP_THRESHOLDS['warm']:
            return "#FFA500"
        elif temp < self.TEMP_THRESHOLDS['hot']:
            return "#FF4500"
        else:
            return "#FF0000"
    
    def get_temp_description(self, temp):
        if temp is None:
            return self.lang['data_unavailable']
        
        if temp < self.TEMP_THRESHOLDS['cool']:
            return self.lang['normal']
        elif temp < self.TEMP_THRESHOLDS['warm']:
            return self.lang['warm']
        elif temp < self.TEMP_THRESHOLDS['hot']:
            return self.lang['hot']
        else:
            return self.lang['critical']
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.lang['menu_file'], menu=file_menu)
        file_menu.add_command(label=self.lang['menu_refresh'], command=self.refresh_sensor)
        file_menu.add_separator()
        file_menu.add_command(label=self.lang['menu_exit'], command=self.on_close)
        
        # Ayarlar menüsü
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.lang['menu_settings'], menu=settings_menu)
        
        # Tema alt menüsü
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label=self.lang['menu_theme'], menu=theme_menu)
        theme_menu.add_radiobutton(label=self.lang['menu_dark'], command=lambda: self.set_theme('dark'), variable=self.theme_var)
        theme_menu.add_radiobutton(label=self.lang['menu_light'], command=lambda: self.set_theme('light'), variable=self.theme_var)
        
        # Dil alt menüsü
        language_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label=self.lang['menu_language'], menu=language_menu)
        language_menu.add_radiobutton(label="Türkçe", command=lambda: self.set_language('tr'), variable=self.language_var)
        language_menu.add_radiobutton(label="English", command=lambda: self.set_language('en'), variable=self.language_var)
        
        settings_menu.add_separator()
        
        # Okuma aralığı alt menüsü
        interval_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label=self.lang['menu_interval'], menu=interval_menu)
        interval_menu.add_radiobutton(label="1 saniye", command=lambda: self.set_interval(1), variable=self.interval_var)
        interval_menu.add_radiobutton(label="2 saniye (Önerilen)", command=lambda: self.set_interval(2), variable=self.interval_var)
        interval_menu.add_radiobutton(label="4 saniye", command=lambda: self.set_interval(4), variable=self.interval_var)
        interval_menu.add_radiobutton(label="6 saniye", command=lambda: self.set_interval(6), variable=self.interval_var)
        interval_menu.add_radiobutton(label="10 saniye", command=lambda: self.set_interval(10), variable=self.interval_var)
        
        # Görüntüleme seçenekleri alt menüsü
        display_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label=self.lang['menu_display'], menu=display_menu)
        display_menu.add_checkbutton(label=self.lang['menu_cpu_usage'], variable=self.display_var_cpu, command=self.toggle_display_item)
        display_menu.add_checkbutton(label=self.lang['menu_cores'], variable=self.display_var_cores, command=self.toggle_display_item)
        display_menu.add_checkbutton(label=self.lang['menu_fan_speed'], variable=self.display_var_fan, command=self.toggle_display_item)
        display_menu.add_checkbutton(label=self.lang['menu_battery'], variable=self.display_var_battery, command=self.toggle_display_item)
        
        settings_menu.add_checkbutton(
            label=self.lang['show_tray'],
            variable=self.tray_var,
            command=self.toggle_system_tray
        )
        settings_menu.add_command(label=self.lang['menu_reset_minmax'], command=self.reset_min_max)
        
        # Hakkında menüsü
        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.lang['menu_about'], menu=about_menu)
        about_menu.add_command(label=self.lang['menu_about'], command=self.show_about)
    
    def set_theme(self, theme):
        self.current_theme = theme
        self.theme_var.set(theme)
        self.save_settings()
        self.refresh_gui()
    
    def set_language(self, lang):
        self.current_language = lang
        self.language_var.set(lang)
        self.save_settings()
        self.refresh_gui()
    
    def set_interval(self, interval):
        self.read_interval = interval
        self.interval_var.set(interval)
        self.save_settings()
    
    def get_config_path(self):
        """Flatpak uyumlu yapılandırma dosyası yolunu alır"""
        # Flatpak ortamında XDG_CONFIG_HOME kullan
        if 'FLATPAK_ID' in os.environ:
            config_dir = os.path.join(os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')), 'lctemp')
        else:
            # Normal Linux ortamı
            config_dir = os.path.expanduser('~/.config/lctemp')
        
        # Dizin mevcut değse oluştur
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'settings.json')
    
    def save_settings(self):
        """Kullanıcı ayarlarını kaydeder"""
        try:
            settings = {
                'theme': self.current_theme,
                'language': self.current_language,
                'read_interval': self.read_interval,
                'show_cpu_usage': self.display_var_cpu.get(),
                'show_cores': self.display_var_cores.get(),
                'show_fan_speed': self.display_var_fan.get(),
                'show_battery': self.display_var_battery.get(),
                'system_tray': self.tray_var.get()
            }
            config_path = self.get_config_path()
            with open(config_path, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata: {e}")
    
    def load_settings(self):
        """Kullanıcı ayarlarını yükler"""
        try:
            config_path = self.get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    settings = json.load(f)
                
                # Ayarları uygula
                if 'theme' in settings:
                    self.current_theme = settings['theme']
                    self.theme_var.set(settings['theme'])
                
                if 'language' in settings:
                    self.current_language = settings['language']
                    self.language_var.set(settings['language'])
                
                if 'read_interval' in settings:
                    self.read_interval = settings['read_interval']
                    self.interval_var.set(settings['read_interval'])
                
                if 'show_cpu_usage' in settings:
                    self.display_var_cpu.set(settings['show_cpu_usage'])
                    self.show_cpu_usage = settings['show_cpu_usage']
                
                if 'show_cores' in settings:
                    self.display_var_cores.set(settings['show_cores'])
                    self.show_cores = settings['show_cores']
                
                if 'show_fan_speed' in settings:
                    self.display_var_fan.set(settings['show_fan_speed'])
                    self.show_fan_speed = settings['show_fan_speed']
                
                if 'show_battery' in settings:
                    self.display_var_battery.set(settings['show_battery'])
                    self.show_battery = settings['show_battery']
                
                if 'system_tray' in settings:
                    self.tray_var.set(settings['system_tray'])
        except Exception as e:
            print(f"Ayarlar yüklenirken hata: {e}")
    
    def toggle_display_item(self):
        self.show_cpu_usage = self.display_var_cpu.get()
        self.show_cores = self.display_var_cores.get()
        self.show_fan_speed = self.display_var_fan.get()
        self.show_battery = self.display_var_battery.get()
        self.save_settings()
        self.refresh_gui()
    
    def read_fan_speed(self):
        """Fan hızını okur - birden fazla yöntem dener"""
        import subprocess
        
        # Yöntem 1: hwmon'dan fan hızını dene
        if self.sensor_path:
            try:
                fan_files = glob.glob(os.path.join(self.sensor_path, "fan*_input"))
                if fan_files:
                    with open(fan_files[0], 'r') as f:
                        return int(f.read().strip())
            except Exception:
                pass
        
        # Yöntem 2: /sys/class/hwmon/ klasöründeki tüm fan dosyalarını kontrol et
        try:
            hwmon_base = "/sys/class/hwmon"
            for hwmon_dir in os.listdir(hwmon_base):
                hwmon_path = os.path.join(hwmon_base, hwmon_dir)
                # fan1_input, fan2_input dosyalarını ara
                for i in range(1, 10):
                    fan_file = os.path.join(hwmon_path, f"fan{i}_input")
                    if os.path.exists(fan_file):
                        with open(fan_file, 'r') as f:
                            fan_speed = int(f.read().strip())
                            if fan_speed > 0:
                                return fan_speed
        except Exception:
            pass
        
        # Yöntem 3: sensors komutunu kullanarak fan hızını al
        try:
            result = subprocess.run(['sensors'], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                output = result.stdout
                # fan regex: fan1: xxx RPM
                import re
                fan_matches = re.findall(r'fan\d+:\s*(\d+)\s*RPM', output, re.IGNORECASE)
                if fan_matches:
                    return int(fan_matches[0])
        except Exception:
            pass
        
        return None
    
    def read_battery_power(self):
        """Pil gücünü okur (watt)"""
        try:
            # /sys/class/power_supply/ dan pil verilerini dene
            battery_dirs = glob.glob("/sys/class/power_supply/BAT*")
            for battery_dir in battery_dirs:
                # Anlık güç (power_now)
                power_file = os.path.join(battery_dir, "power_now")
                if os.path.exists(power_file):
                    with open(power_file, 'r') as f:
                        microwatts = int(f.read().strip())
                        return microwatts / 1000000.0  # microwatts to watts
                # Energy rate (power)
                power_file = os.path.join(battery_dir, "power")
                if os.path.exists(power_file):
                    with open(power_file, 'r') as f:
                        microwatts = int(f.read().strip())
                        return microwatts / 1000000.0
        except Exception:
            pass
        return None
    
    def refresh_gui(self):
        """GUI'yi tema ve dil değişikliğinden sonra yeniler"""
        # Mevcut widget'ları temizle
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # GUI'yi yeniden oluştur - tray_var korunacak
        self.setup_gui()
        self.create_menu()
    
    def show_about(self):
        messagebox.showinfo(self.lang['about_title'], self.lang['about_text'])
    
    def refresh_sensor(self):
        self.find_sensor()
    
    def reset_min_max(self):
        self.max_temp = None
        self.min_temp = None
        # Etiketleri güncelle
        t = self.lang['temp']
        self.widgets['max_label'].config(text=f"{self.lang['max']}: --.-{t}")
        self.widgets['min_label'].config(text=f"{self.lang['min']}: --.-{t}")
    
    def toggle_system_tray(self):
        if not PYSTRAY_AVAILABLE:
            messagebox.showwarning("Sistem Tepsi", "pystray kütüphanesi gerekli.")
            self.tray_var.set(False)
            return
        
        # Check desktop environment BEFORE enabling
        new_state = self.tray_var.get()
        
        if new_state and not (self.is_cinnamon or self.is_kde):
            messagebox.showwarning(
                "Sistem Tepsi",
                "Bu özellik yalnızca Cinnamon ve KDE masaüstü ortamlarında çalışır.\n"
                f"Algılanan masaüstü ortamı: {self.desktop_environment}"
            )
            self.tray_var.set(False)
            self.system_tray_enabled = False
            return
        
        self.system_tray_enabled = new_state
        
        if self.system_tray_enabled:
            if self.tray_icon is None:
                self.setup_system_tray()
            
            if self.tray_icon and (not hasattr(self, 'tray_thread') or not self.tray_thread.is_alive()):
                import threading
                self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
                self.tray_thread.start()
                self.root.withdraw()
        else:
            if self.tray_icon:
                self.tray_icon.stop()
                self.tray_icon = None
                self.tray_thread = None
            self.root.deiconify()
    
    # toggle_system_tray_from_menu kaldırıldı - toggle_system_tray ile birleştirildi
    
    def setup_gui(self):
        t = self.theme
        
        self.root.title("LCTemp - CPU Sıcaklık Monitörü")
        self.root.geometry("420x420")
        self.root.resizable(False, False)
        
        main_frame = tk.Frame(self.root, bg=t['bg'], padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        title_font = tkfont.Font(family="Arial", size=16, weight="bold")
        title_label = tk.Label(main_frame, text=self.lang['title'], font=title_font, bg=t['bg'], fg=t['fg'])
        title_label.pack(pady=(0, 10))
        
        # Sıcaklık göstergesi
        self.widgets['temp_label'] = tk.Label(
            main_frame, text="--.- " + self.lang['temp'],
            font=tkfont.Font(family="Arial", size=52, weight="bold"),
            bg=t['bg'], fg=t['fg_muted']
        )
        self.widgets['temp_label'].pack(pady=5)
        
        # Durum
        self.widgets['status_label'] = tk.Label(
            main_frame, text=self.lang['sensor_wait'],
            font=tkfont.Font(family="Arial", size=11),
            bg=t['bg'], fg=t['fg_muted']
        )
        self.widgets['status_label'].pack(pady=2)
        
        # İlerleme çubuğu
        self.widgets['progress_canvas'] = tk.Canvas(main_frame, width=320, height=16, bg=t['progress_bg'], highlightthickness=0)
        self.widgets['progress_canvas'].pack(pady=8)
        self.widgets['progress_canvas'].create_rectangle(4, 4, 316, 12, outline=t['border'], width=1)
        self.widgets['progress_bar'] = self.widgets['progress_canvas'].create_rectangle(4, 4, 4, 12, fill="#00FF00", width=0)
        
        # CPU kullanım (görüntüleme seçeneği açıksa)
        if self.show_cpu_usage:
            usage_frame = tk.Frame(main_frame, bg=t['bg'])
            usage_frame.pack(pady=5, fill=tk.X)
            
            self.widgets['usage_label'] = tk.Label(
                usage_frame, text=f"{self.lang['cpu']}: --.-%",
                font=tkfont.Font(family="Arial", size=11),
                bg=t['bg'], fg="#00bfff"
            )
            self.widgets['usage_label'].pack()
        
        # Thermal Throttling uyarısı
        throttle_frame = tk.Frame(main_frame, bg=t['bg'])
        throttle_frame.pack(pady=5, fill=tk.X)
        
        self.widgets['throttle_label'] = tk.Label(
            throttle_frame, text="CPU: -- MHz",
            font=tkfont.Font(family="Arial", size=10),
            bg=t['bg'], fg=t['fg']
        )
        self.widgets['throttle_label'].pack()
        
        # Fan hızı (görüntüleme seçeneği açıksa)
        if self.show_fan_speed:
            fan_frame = tk.Frame(main_frame, bg=t['bg'])
            fan_frame.pack(pady=5, fill=tk.X)
            
            self.widgets['fan_label'] = tk.Label(
                fan_frame, text=f"{self.lang['menu_fan_speed']}: -- RPM",
                font=tkfont.Font(family="Arial", size=11),
                bg=t['bg'], fg="#98d8c8"
            )
            self.widgets['fan_label'].pack()
        
        # Pil gücü (görüntüleme seçeneği açıksa)
        if self.show_battery:
            battery_frame = tk.Frame(main_frame, bg=t['bg'])
            battery_frame.pack(pady=5, fill=tk.X)
            
            self.widgets['battery_label'] = tk.Label(
                battery_frame, text=f"{self.lang['menu_battery']}: -- W",
                font=tkfont.Font(family="Arial", size=11),
                bg=t['bg'], fg="#f7dc6f"
            )
            self.widgets['battery_label'].pack()
        
        # Çekirdekler (görüntüleme seçeneği açıksa)
        if self.show_cores:
            cores_frame = tk.Frame(main_frame, bg=t['bg'])
            cores_frame.pack(pady=5, fill=tk.BOTH, expand=True)
            
            self.widgets['cores_label'] = tk.Label(
                cores_frame, text=f"{self.lang['cores']}: -",
                font=tkfont.Font(family="Arial", size=9),
                bg=t['bg'], fg=t['fg_secondary'], wraplength=350
            )
            self.widgets['cores_label'].pack()
        
        # Min/Max
        minmax_frame = tk.Frame(main_frame, bg=t['bg'])
        minmax_frame.pack(pady=5, fill=tk.X)
        
        self.widgets['max_label'] = tk.Label(
            minmax_frame, text=f"{self.lang['max']}: --.-{self.lang['temp']}",
            font=tkfont.Font(family="Arial", size=10, weight="bold"),
            bg=t['bg'], fg="#ff6b6b"
        )
        self.widgets['max_label'].pack(side=tk.LEFT, padx=20)
        
        self.widgets['min_label'] = tk.Label(
            minmax_frame, text=f"{self.lang['min']}: --.-{self.lang['temp']}",
            font=tkfont.Font(family="Arial", size=10, weight="bold"),
            bg=t['bg'], fg="#4ecdc4"
        )
        self.widgets['min_label'].pack(side=tk.RIGHT, padx=20)
        
        # Sensör bilgisi
        self.widgets['sensor_info_label'] = tk.Label(
            main_frame, text="",
            font=tkfont.Font(family="Arial", size=8),
            bg=t['bg'], fg=t['fg_muted']
        )
        self.widgets['sensor_info_label'].pack(side=tk.BOTTOM, pady=(5, 0))
        
        # Sistem tepsisi checkbox
        self.widgets['tray_var'] = self.tray_var
        self.widgets['tray_checkbox'] = tk.Checkbutton(
            main_frame, text=self.lang['show_tray'],
            variable=self.widgets['tray_var'],
            command=self.toggle_system_tray,
            bg=t['bg'], fg=t['fg_secondary'],
            selectcolor=t['input_bg'],
            font=tkfont.Font(family="Arial", size=9),
            activebackground=t['bg'], activeforeground=t['fg_secondary']
        )
        self.widgets['tray_checkbox'].pack(side=tk.BOTTOM, pady=(5, 0))
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def update_min_max_label(self):
        t = self.lang['temp']
        
        if self.max_temp is not None:
            self.widgets['max_label'].config(text=f"{self.lang['max']}: {self.max_temp:.1f}{t}")
        else:
            self.widgets['max_label'].config(text=f"{self.lang['max']}: --.-{t}")
        
        if self.min_temp is not None:
            self.widgets['min_label'].config(text=f"{self.lang['min']}: {self.min_temp:.1f}{t}")
        else:
            self.widgets['min_label'].config(text=f"{self.lang['min']}: --.-{t}")
    
    def update_status(self, message, color="white"):
        if 'status_label' in self.widgets:
            self.widgets['status_label'].config(text=message, fg=color)
    
    def update_temperature(self):
        if not self.running:
            return
        
        # CPU kullanımını oku (gösteriliyorsa)
        if self.show_cpu_usage:
            cpu_usage = self.read_cpu_usage()
            if cpu_usage is not None:
                self.current_usage = cpu_usage
                if 'usage_label' in self.widgets:
                    self.widgets['usage_label'].config(text=f"{self.lang['cpu']}: {cpu_usage:.1f}%")
        
        # CPU frekansını oku
        cpu_freq = self.read_cpu_freq()
        if cpu_freq is not None:
            if 'throttle_label' in self.widgets:
                self.widgets['throttle_label'].config(
                    text=f"CPU: {cpu_freq:.0f} MHz",
                    fg=self.theme['fg']
                )
        
        # Fan hızını oku (gösteriliyorsa)
        if self.show_fan_speed:
            fan_speed = self.read_fan_speed()
            if 'fan_label' in self.widgets:
                if fan_speed is not None:
                    self.widgets['fan_label'].config(text=f"{self.lang['menu_fan_speed']}: {fan_speed} RPM")
                else:
                    self.widgets['fan_label'].config(text=f"{self.lang['menu_fan_speed']}: -- RPM")
        
        # Pil gücünü oku (gösteriliyorsa)
        if self.show_battery:
            battery_power = self.read_battery_power()
            if 'battery_label' in self.widgets:
                if battery_power is not None:
                    self.widgets['battery_label'].config(text=f"{self.lang['menu_battery']}: {battery_power:.1f} W")
                else:
                    self.widgets['battery_label'].config(text=f"{self.lang['menu_battery']}: -- W")
        
        package_temp, all_temps = self.read_temperature()
        
        self.update_min_max(package_temp)
        
        if package_temp is not None:
            self.current_temp = package_temp
            
            self.widgets['temp_label'].config(
                text=f"{package_temp:.1f} {self.lang['temp']}",
                fg=self.get_temp_color(package_temp)
            )
            
            status_text = self.get_temp_description(package_temp)
            self.update_status(status_text, self.get_temp_color(package_temp))
            
            progress_width = min(312, max(4, (min(package_temp, 100) / 100.0) * 312))
            self.widgets['progress_canvas'].coords(
                self.widgets['progress_bar'],
                4, 4, progress_width + 4, 12
            )
            self.widgets['progress_canvas'].itemconfig(
                self.widgets['progress_bar'],
                fill=self.get_temp_color(package_temp)
            )
            
            if self.show_cores and 'cores_label' in self.widgets:
                if len(all_temps) > 1:
                    cores_text = f"{self.lang['cores']}: " + " | ".join([f"{t:.0f}{self.lang['temp']}" for t in all_temps[1:]])
                    self.widgets['cores_label'].config(text=cores_text)
                else:
                    self.widgets['cores_label'].config(text=f"{self.lang['cores']}: {self.lang['single_core']}")
            
            if self.sensor_name:
                self.widgets['sensor_info_label'].config(
                    text=f"Sensör: {self.sensor_name} | Okuma: {len(all_temps)} değer | Aralık: {self.read_interval}s"
                )
            
        else:
            self.widgets['temp_label'].config(text=f"--.- {self.lang['temp']}", fg=self.theme['fg_muted'])
            self.update_status(self.lang['data_unavailable'], "orange")
        
        self.update_min_max_label()
        self.update_system_tray()
        
        self.root.after(self.read_interval * 1000, self.update_temperature)
    
    def on_close(self):
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = LCTemp(root)
    root.mainloop()


if __name__ == "__main__":
    print("=" * 50)
    print("LCTemp - Linux CPU Sıcaklık Monitörü")
    print("=" * 50)
    print("Usage: python3 lctemp_monitor.py")
    print("=" * 50)
    main()
