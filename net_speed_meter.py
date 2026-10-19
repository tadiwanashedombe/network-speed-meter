#!/usr/bin/env python3
import signal, socket, threading, time, os
import psutil
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GLib, AppIndicator3

UPDATE_INTERVAL = 1

BOLD = str.maketrans(
    "0123456789KMGBs.",
    "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵𝗞𝗠𝗚𝗕𝘀."
)

def fmt(bps):
    if bps < 1024:    r = f"{bps:.0f}B/s"
    elif bps<1024**2: r = f"{bps/1024:.0f}K/s"
    elif bps<1024**3: r = f"{bps/1024**2:.1f}M/s"
    else:             r = f"{bps/1024**3:.1f}G/s"
    return r.translate(BOLD)

def fmt_bytes(b):
    if b < 1024:    return f"{b}B"
    if b < 1024**2: return f"{b/1024:.1f}KB"
    if b < 1024**3: return f"{b/1024**2:.2f}MB"
    return                  f"{b/1024**3:.2f}GB"

def get_iface():
    for iface, stat in psutil.net_if_stats().items():
        if iface == "lo" or not stat.isup:
            continue
        for addr in psutil.net_if_addrs().get(iface, []):
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                return iface
    return ""

state = {"dl":0.0, "ul":0.0, "iface":"", "sdl":0, "sul":0}

def sampler():
    prev = psutil.net_io_counters()
    pt   = time.monotonic()
    while True:
        time.sleep(UPDATE_INTERVAL)
        now  = psutil.net_io_counters()
        nt   = time.monotonic()
        dl_b = max(now.bytes_recv - prev.bytes_recv, 0)
        ul_b = max(now.bytes_sent - prev.bytes_sent, 0)
        ela  = nt - pt
        iface = get_iface()
        state["dl"]    = dl_b / ela
        state["ul"]    = ul_b / ela
        state["iface"] = iface
        if iface:
            state["sdl"] += dl_b
            state["sul"] += ul_b
        prev, pt = now, nt

def build_menu(ind):
    menu = Gtk.Menu()
    iface_item = Gtk.MenuItem(label=f"Interface: {state['iface'] or 'none'}")
    iface_item.set_sensitive(False)
    menu.append(iface_item)
    sess_item = Gtk.MenuItem(label=f"Session: ▼{fmt_bytes(state['sdl'])}  ▲{fmt_bytes(state['sul'])}")
    sess_item.set_sensitive(False)
    menu.append(sess_item)
    menu.append(Gtk.SeparatorMenuItem())
    quit_item = Gtk.MenuItem(label="Quit Net Speed Meter")
    quit_item.connect("activate", lambda _: Gtk.main_quit())
    menu.append(quit_item)
    menu.show_all()
    return menu

def update_label(ind):
    label = f"▼ {fmt(state['dl'])}  ▲ {fmt(state['ul'])}"
    ind.set_label(label, "▼ 000K/s  ▲ 000K/s")
    ind.set_menu(build_menu(ind))
    return True

def main():
    threading.Thread(target=sampler, daemon=True).start()
    ind = AppIndicator3.Indicator.new(
        "net-speed-meter",
        "network-transmit-receive",
        AppIndicator3.IndicatorCategory.SYSTEM_SERVICES,
    )
    ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
    ind.set_label("▼ ---  ▲ ---", "▼ 000K/s  ▲ 000K/s")
    ind.set_menu(build_menu(ind))
    GLib.timeout_add_seconds(UPDATE_INTERVAL, update_label, ind)
    signal.signal(signal.SIGINT,  lambda *_: Gtk.main_quit())
    signal.signal(signal.SIGTERM, lambda *_: Gtk.main_quit())
    Gtk.main()

main()
