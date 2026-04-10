# LCTemp - Kurulum Rehberi

## Gereksinimler

### Temel Bağımlılıklar

| Bağımlılık | Sürüm | Açıklama |
|------------|-------|----------|
| Python | 3.8+ | Uygulamanın çalışması için gerekli |
| tkinter | - | GUI kütüphanesi (Python ile birlikte gelir) |
| pystray | 0.19+ | Sistem tepsisi desteği |
| Pillow | 9.0+ | Görüntü işleme kütüphanesi |

### Sistem Gereksinimleri

- **Linux Kernel**: hwmon desteği (sıcaklık sensörleri için)
- **Masaüstü Ortamı**: Cinnamon, KDE, GNOME, XFCE, MATE veya diğerleri
- **Sensör Desteği**: lm-sensors paketi kurulu olmalı

## Kurulum Yöntemleri

### 1. Debian/Ubuntu Paketi ile Kurulum (Önerilen)

```bash
# Paketi indirin
wget https://github.com/Efebalikci5/LCTemp/releases/latest/download/lctemp.deb

# Paketi kurun
sudo dpkg -i lctemp.deb

# Eksik bağımlılıkları düzeltin (gerekirse)
sudo apt-get install -f
```

### 2. Kaynak Koddan Kurulum

```bash
# Repository'yi klonlayın
git clone https://github.com/Efebalikci5/LCTemp.git
cd LCTemp

# Bağımlılıkları kurun
pip3 install -r lctemp_requirements.txt

# Uygulamayı çalıştırın
python3 lctemp_monitor.py
```

### 3. Manuel Bağımlılık Kurulumu

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

## Olası Sorunlar ve Çözümleri

### 1. Tkinter Hatası

**Hata Mesajı:**
```
HATA: Tkinter kütüphanesi bulunamadı!
```

**Çözüm:**
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

### 2. Sensör Bulunamadı Hatası

**Hata Mesajı:**
```
Sensör bulunamadı!
```

**Çözüm:**
```bash
# lm-sensors paketini kurun
sudo apt install lm-sensors  # Ubuntu/Debian
sudo dnf install lm_sensors  # Fedora
sudo pacman -S lm_sensors    # Arch Linux

# Sensörleri algılayın
sudo sensors-detect

# Değişikliklerin uygulanması için yeniden başlatın
sudo reboot
```

### 3. pystray Kurulum Hatası

**Hata Mesajı:**
```
ModuleNotFoundError: No module named 'pystray'
```

**Çözüm:**
```bash
# pip ile kurun
pip3 install pystray

# Eğer pip yoksa önce pip'i kurun
sudo apt install python3-pip  # Ubuntu/Debian
sudo dnf install python3-pip  # Fedora
```

### 4. Pillow Kurulum Hatası

**Hata Mesajı:**
```
ModuleNotFoundError: No module named 'PIL'
```

**Çözüm:**
```bash
# Pillow kurun
pip3 install Pillow

# Eğer hata devam ederse
pip3 install --upgrade Pillow
```

### 5. Sistem Tepsisi Çalışmıyor

**Sorun:** Sistem tepsisi ikonu görünmüyor

**Çözüm:**
- Sistem tepsisi yalnızca **Cinnamon** ve **KDE** masaüstlerinde çalışır
- GNOME, XFCE ve MATE'de sistem tepsisi desteği sınırlıdır
- Beta aşamasında olduğu için bazı hatalar oluşabilir

### 6. İzin Hatası

**Hata Mesajı:**
```
PermissionError: [Errno 13] Permission denied
```

**Çözüm:**
```bash
# Sensör dosyalarına erişim izni verin
sudo chmod 644 /sys/class/hwmon/hwmon*/temp*_input

# Veya uygulamayı sudo ile çalıştırın (önerilmez)
sudo python3 lctemp_monitor.py
```

### 7. Python Sürüm Uyumsuzluğu

**Hata Mesajı:**
```
SyntaxError: invalid syntax
```

**Çözüm:**
```bash
# Python sürümünüzü kontrol edin
python3 --version

# Eğer 3.8'den düşükse Python'u güncelleyin
sudo apt install python3.10  # Ubuntu/Debian
```

### 8. dpkg Hatası (Debian Paketi)

**Hata Mesajı:**
```
dpkg: error processing archive lctemp.deb
```

**Çözüm:**
```bash
# Eksik bağımlılıkları düzeltin
sudo apt-get install -f

# Paketi yeniden kurun
sudo dpkg -i lctemp.deb
```

## Masaüstü Entegrasyonu

### Uygulamayı Çalıştırılabilir Yapma

```bash
# Uygulamaya çalıştırma izni verin
sudo chmod +x /usr/bin/lctemp

# Veya kaynak koddan kurulumda
chmod +x lctemp_monitor.py
```

### Masaüstü Kısayolu Oluşturma

```bash
# .desktop dosyasını kopyalayın
sudo cp LCTemp.desktop /usr/share/applications/

# Veya kullanıcı bazlı kurulum için
mkdir -p ~/.local/share/applications
cp LCTemp.desktop ~/.local/share/applications/
```

### Uygulamayı Başlatma

```bash
# Terminalden çalıştırın
lctemp

# Veya
python3 /usr/bin/lctemp

# Veya masaüstü ortamından uygulama menüsünden başlatın
```

## Doğrulama

Kurulumdan sonra uygulamanın düzgün çalıştığını doğrulamak için:

```bash
# Uygulamayı çalıştırın
lctemp

# Veya
python3 /usr/bin/lctemp
```

Başarılı kurulumda:
- GUI penceresi açılacak
- Sıcaklık değerleri görüntülenecek
- Sistem tepsisi ikonu görünecek (Cinnamon/KDE)

## Kaldırma

### Debian Paketi ile Kaldırma
```bash
sudo dpkg -r lctemp
```

### Kaynak Koddan Kaldırma
```bash
# Klonlanan dizini silin
rm -rf LCTemp
```

## Destek

Sorun yaşarsanız:
- GitHub Issues: https://github.com/Efebalikci5/LCTemp/issues
- E-posta: efebalikci9@gmail.com
