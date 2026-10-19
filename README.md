# Net Speed Meter
 
A lightweight network speed indicator for the Linux top bar. It shows your live download and upload speed right in the panel, with session totals one click away.
 
```
▼ 𝟭𝟮𝟯𝗞/𝘀  ▲ 𝟰𝟱𝗞/𝘀
```
 
## Features
 
- Live download (▼) and upload (▲) speed, updated every second
- Auto-scaling units: B/s, K/s, M/s, G/s
- Bold Unicode digits so the text stays readable in the panel
- Dropdown menu showing the active interface and session totals
- Single file, no config
## Requirements
 
- Python 3
- GTK 3 with AppIndicator support
- `psutil`
Install the dependencies on Debian/Ubuntu-based systems:
 
```bash
sudo apt install python3-psutil python3-gi gir1.2-appindicator3-0.1
```
 
> **GNOME users:** install the *AppIndicator and KStatusNotifierItem Support* extension, otherwise the indicator won't appear in the top bar. Ubuntu ships with it enabled. Linux Mint and KDE work out of the box.
 
## Usage
 
```bash
git clone https://github.com/tadiwanashedombe/network-speed-meter.git
cd network-speed-meter
python3 net_speed_meter.py
```
 
Click the indicator to see the active interface and how much you've downloaded and uploaded since the script started. Choose **Quit Net Speed Meter** to exit.
 
 
 ## Run automatically on start

This assumes the script is at `~/network-speed-meter/net_speed_meter.py`. If it’s saved under a different name, change the `Exec= line` to match. You can check with ls `~/net_speed_meter.py`.

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/net-speed-meter.desktop << EOF
[Desktop Entry]
Type=Application
Name=Net Speed Meter
Exec=python3 $HOME/network-speed-meter/net_speed_meter.py
X-GNOME-Autostart-enabled=true
EOF
```
Replace `$HOME/network-speed-meter/net_speed_meter.py` with the real path to the script.

## Configuration
 
Change the refresh rate by editing this line at the top of the script:
 
```python
UPDATE_INTERVAL = 1  # seconds
```
 
## How it works
 
A background thread reads total bytes sent and received from `psutil.net_io_counters()` every interval, subtracts the previous reading, and divides by the elapsed time to get bytes per second. The result is displayed through `AppIndicator3`. The active interface is the first one that is up and has a non-loopback IPv4 address.
