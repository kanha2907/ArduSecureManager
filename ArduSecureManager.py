#!/usr/bin/env python3
"""
ArduPilot Secure Firmware Manager
A GUI tool for managing secure firmware: key generation, build, sign, flash.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import glob
import json
import base64
import time
import serial.tools.list_ports

# ─── Theme ───────────────────────────────────────────────────────────────────
BG       = "#0d0f14"
BG2      = "#151820"
BG3      = "#1c2030"
ACCENT   = "#00d4ff"
ACCENT2  = "#ff6b35"
GREEN    = "#00ff88"
RED      = "#ff3355"
YELLOW   = "#ffd700"
TEXT     = "#e8eaf0"
MUTED    = "#556070"
BORDER   = "#252a3a"
FONT_MONO= ("JetBrains Mono", 10) if os.path.exists("/usr/share/fonts/truetype/jetbrains") else ("Courier New", 10)
FONT_UI  = ("Segoe UI", 10)
FONT_H1  = ("Segoe UI", 14, "bold")
FONT_H2  = ("Segoe UI", 11, "bold")

# Map display name -> waf board name
ARDUPILOT_BOARDS_MAP = {
    "AcctonGodwit GA1": "AcctonGodwit",
    "ARKV6X DS-10 Pixhawk6": "ARK_ARKV6X",
    "CUAV V5 Plus": "CUAVv5",
    "CUAV V5 Nano": "CUAVv5Nano",
    "CUAV Nora": "CUAVNora",
    "CUAV Pixhawk v6X": "CUAVv6X",
    "CUAV Pixhawk v6X V2": "CUAVv6XV2",
    "CUAV X7/X7Pro/X7+": "CUAV-X7",
    "CUAV-7-Nano": "CUAV-7-Nano",
    "Drotek Pixhawk3": "Pixhawk3Pro",
    "F4BY": "F4BY",
    "CubePilot Cube Black": "CubeBlack",
    "CubePilot Cube Orange": "CubeOrange",
    "CubePilot Cube Purple": "CubePurple",
    "CubePilot Cube Yellow": "CubeYellow",
    "CubePilot Cube Green": "CubeGreen",
    "Holybro Durandal H7": "Durandal",
    "Holybro Pix32 v5": "Pix32v5",
    "Holybro Pixhawk 4": "Pixhawk4",
    "Holybro Pixhawk6X": "Pixhawk6X",
    "Holybro Pixhawk6C": "Pixhawk6C",
    "Holybro Pix32v6": "Pix32v6",
    "mRo Pixhawk": "mRoX21",
    "mRo Pixracer": "Pixracer",
    "mRo X2.1": "mRoX21",
    "mRo X2.1-777": "mRoX21-777",
    "OpenPilot Revolution": "Revolution",
    "SULIGH7": "SULIGH7",
    "TauLabs Sparky2": "Sparky2",
    "ZeroOneX6": "ZeroOneX6",
    "ZeroOneX6-Air": "ZeroOneX6-Air",
    "3DR Control Zero H7 OEM": "ControlZeroH7OEM",
    "ACNS-CM4Pilot": "ACNS-CM4Pilot",
    "AEDROX H7": "AEDROX-H743",
    "AnyleafH7": "AnyleafH7",
    "ARK FPV": "ARK_FPV",
    "ARK_PI6X": "ARK_PI6X",
    "AtomRC F405-NAVI": "AtomRCF405NAVI",
    "BetaFPV F405": "BetaFPVF405",
    "BrahmaF4": "BrahmaF4",
    "brainFPV RADIX2 HD": "RADIX2HD",
    "CBUnmanned H743": "CBUnmanned-H743-Stamp",
    "CrazyF405": "CrazyF405",
    "CUAV-X25-EVO": "CUAV-X25-EVO",
    "DroneerF405": "DroneerF405",
    "F4BY_H743": "F4BY_H743",
    "Flywoo F405 Pro": "FlywooF405Pro",
    "Flywoo F745": "FlywooF745",
    "Flywoo H743": "FlywooH743",
    "Foxeer F405v2": "FoxeerF405v2",
    "Foxeer H743": "FoxeerH743",
    "GEPRC Taker F745": "GEPRC_F745",
    "GEPRC Taker H743": "GEPRC_H743",
    "HeeWing F405": "HeeWingF405",
    "Holybro Kakute F4": "KakuteF4",
    "Holybro Kakute F4 Mini": "KakuteF4Mini",
    "Holybro Kakute F7": "KakuteF7",
    "Holybro Kakute F4 Wing": "KakuteF4Wing",
    "Holybro Kakute H7 V1": "KakuteH7",
    "Holybro Kakute H7 V2": "KakuteH7v2",
    "Holybro Kakute H7 Wing": "KakuteH7Wing",
    "Holybro Pixhawk 4 Mini": "Pixhawk4Mini",
    "Holybro Pixhawk5X": "Pixhawk5X",
    "iFlight Beast F7": "iflight_beast_f7",
    "iFlight BeastH7 AIO": "iflight_blitz_h7",
    "iFlight Blitz F745": "iflight_blitz_f7",
    "iFlight Blitz H743 Pro": "iflight_blitz_h743",
    "iFlight Thunder H7": "iflight_thunder_h7",
    "JHEMCU F405Pro": "JHEMCUF405Pro",
    "JHEMCU H743HD": "JHEMCUH743HD",
    "Mamba F405 MK2": "MambaF405MK2",
    "Mamba H743 v4": "MambaH743v4",
    "Mateksys F405 TE": "MatekF405TE",
    "Mateksys H743-Wing": "MatekH743",
    "Mateksys H743-MINI": "MatekH743-mini",
    "Mateksys H743-SLIM": "MatekH743-slim",
    "MicoAir405v2": "MicoAir405v2",
    "MicoAir743": "MicoAir743",
    "ModalAI Flight core": "modalai_fc-v1",
    "mRo ControlZero F7": "mRoControlZeroF7",
    "mRo ControlZero H7": "mRoControlZeroH7",
    "mRo Pixracer Pro H7": "mRoPixracerPro",
    "Omnibus F4 Pro": "OmnibusF4Pro",
    "OmnibusNanoV6": "OmnibusNanoV6",
    "Omnibus F7V2": "omnibusf7v2",
    "Parrot Bebop": "bebop",
    "QioTek Zealot F427": "QioTekZealotF427",
    "QioTek Zealot H743": "QioTekZealotH743",
    "RadioLink MiniPix": "MiniPix",
    "RadioLinkF405": "RadioLinkF405",
    "RadioLinkPIX6": "RadioLinkPIX6",
    "SIYI N7": "SIYI_N7",
    "Sky-Drones AIRLink": "AIRLink",
    "SkystarsH7HD": "SkystarsH7HD",
    "SPRacing H7 Extreme": "SPRacingH7Extreme",
    "SPRacing H7 RF": "SPRacingH7RF",
    "SpeedyBee F405 AIO": "speedybeef405",
    "SpeedyBee F405 Mini": "speedybeef405mini",
    "SpeedyBeeF405WING": "speedybeef405wing",
    "TBS Lucid H7": "TBSLucidH7",
    "TBS Lucid H7 Wing": "TBSLucidH7Wing",
    "ThePeach FCC-K1": "ThePeach-K1",
    "ThePeach FCC-R1": "ThePeach-R1",
    "VR Brain 5": "VRBrain5",
    "YJUAV A6SE": "YJUAV_A6SE",
    "YJUAV A6SE H743": "YJUAV_A6SE_H743",
    "fmuv2": "fmuv2",
    "fmuv3": "fmuv3",
    "fmuv4": "fmuv4",
    "fmuv5": "fmuv5",
}
ARDUPILOT_BOARDS = sorted(ARDUPILOT_BOARDS_MAP.keys())

VEHICLE_TYPES = ["copter", "plane", "rover", "sub", "antennatracker", "blimp"]


class TerminalWidget(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG2, **kwargs)
        self.text = scrolledtext.ScrolledText(
            self, bg="#080a0f", fg=TEXT, font=FONT_MONO,
            insertbackground=ACCENT, borderwidth=0, highlightthickness=0,
            wrap=tk.WORD, state=tk.DISABLED
        )
        self.text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.text.tag_configure("success", foreground=GREEN)
        self.text.tag_configure("error",   foreground=RED)
        self.text.tag_configure("warn",    foreground=YELLOW)
        self.text.tag_configure("info",    foreground=ACCENT)
        self.text.tag_configure("cmd",     foreground=ACCENT2)
        self.text.tag_configure("muted",   foreground=MUTED)

    def write(self, text, tag=None):
        self.text.configure(state=tk.NORMAL)
        if tag:
            self.text.insert(tk.END, text, tag)
        else:
            self.text.insert(tk.END, text)
        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)

    def clear(self):
        self.text.configure(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.configure(state=tk.DISABLED)


class StatusBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG3, height=28)
        self.pack_propagate(False)
        self.dot = tk.Label(self, text="●", bg=BG3, fg=MUTED, font=("Segoe UI", 12))
        self.dot.pack(side=tk.LEFT, padx=(12, 4))
        self.label = tk.Label(self, text="Ready", bg=BG3, fg=MUTED, font=("Segoe UI", 9))
        self.label.pack(side=tk.LEFT)
        self.right = tk.Label(self, text="ArduPilot Secure Manager v1.0", bg=BG3, fg=MUTED, font=("Segoe UI", 9))
        self.right.pack(side=tk.RIGHT, padx=12)

    def set(self, text, state="idle"):
        colors = {"idle": MUTED, "running": YELLOW, "ok": GREEN, "error": RED}
        color = colors.get(state, MUTED)
        self.dot.configure(fg=color)
        self.label.configure(text=text, fg=color)


def styled_button(parent, text, command, style="primary", width=None):
    colors = {
        "primary": (ACCENT,   BG,   ACCENT),
        "danger":  (RED,      BG,   RED),
        "success": (GREEN,    BG,   GREEN),
        "warning": (YELLOW,   BG,   YELLOW),
        "ghost":   (BG3,      TEXT, BORDER),
    }
    bg, fg, border = colors.get(style, colors["primary"])
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg if style != "primary" else BG,
        font=("Segoe UI", 9, "bold"),
        relief=tk.FLAT, borderwidth=0, cursor="hand2",
        padx=14, pady=6, activebackground=border, activeforeground=fg
    )
    if style == "primary":
        btn.configure(fg=BG)
    if width:
        btn.configure(width=width)
    return btn


def section_label(parent, text):
    f = tk.Frame(parent, bg=BG)
    tk.Label(f, text=text, bg=BG, fg=ACCENT, font=FONT_H2).pack(side=tk.LEFT)
    tk.Frame(f, bg=BORDER, height=1).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(12,0), pady=8)
    return f


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ArduPilot Secure Firmware Manager")
        self.configure(bg=BG)
        self.geometry("1100x750")
        self.minsize(900, 600)

        self.ardupilot_path = tk.StringVar(value=self._find_ardupilot())
        self.private_key    = tk.StringVar()
        self.public_key     = tk.StringVar()
        self.key_name       = tk.StringVar(value="mykey")
        self.board          = tk.StringVar(value="CUAVv5")
        self.vehicle        = tk.StringVar(value="copter")
        self.firmware_path  = tk.StringVar()
        self.serial_port    = tk.StringVar()
        self.running        = False

        self._build_ui()
        self._refresh_ports()
        self._auto_detect_keys()

    def _find_ardupilot(self):
        candidates = [
            os.path.expanduser("~/Desktop/secure/ardupilot"),
            os.path.expanduser("~/ardupilot"),
            os.path.expanduser("~/src/ardupilot"),
        ]
        for p in candidates:
            if os.path.isdir(p):
                return p
        return os.path.expanduser("~/ardupilot")

    def _auto_detect_keys(self):
        ap = self.ardupilot_path.get()
        for f in glob.glob(os.path.join(ap, "*_private_key.dat")):
            self.private_key.set(f)
            pub = f.replace("_private_key.dat", "_public_key.dat")
            if os.path.exists(pub):
                self.public_key.set(pub)
            break
        # Also check Desktop/secure
        for f in glob.glob(os.path.expanduser("~/Desktop/secure/*_private_key.dat")):
            if not self.private_key.get():
                self.private_key.set(f)

    def _build_ui(self):
        # ── Header ──
        header = tk.Frame(self, bg=BG3, height=56)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="🔐", bg=BG3, font=("Segoe UI", 22)).pack(side=tk.LEFT, padx=(16,8), pady=8)
        tk.Label(header, text="ARDUPILOT SECURE FIRMWARE MANAGER",
                 bg=BG3, fg=ACCENT, font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT, pady=8)
        tk.Label(header, text="SECURE BUILD PIPELINE",
                 bg=BG3, fg=MUTED, font=("Segoe UI", 8)).pack(side=tk.RIGHT, padx=16)

        # ── Main area ──
        main = tk.Frame(self, bg=BG)
        main.pack(fill=tk.BOTH, expand=True)

        # Left panel - controls
        left = tk.Frame(main, bg=BG, width=420)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(16,8), pady=12)
        left.pack_propagate(False)

        # Right panel - terminal
        right = tk.Frame(main, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8,16), pady=12)

        self._build_controls(left)
        self._build_terminal(right)

        # ── Status bar ──
        self.status = StatusBar(self)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def _build_controls(self, parent):
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=BG)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._build_sections(frame)

    def _build_sections(self, parent):
        pad = {"padx": 0, "fill": tk.X}

        # ─ ArduPilot Path ─
        section_label(parent, "ARDUPILOT PATH").pack(fill=tk.X, pady=(0,4))
        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, pady=2)
        entry = tk.Entry(row, textvariable=self.ardupilot_path, bg=BG2, fg=TEXT,
                         font=FONT_MONO, relief=tk.FLAT, insertbackground=ACCENT,
                         highlightthickness=1, highlightcolor=ACCENT, highlightbackground=BORDER)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        styled_button(row, "Browse", lambda: self._browse_dir(self.ardupilot_path), "ghost").pack(side=tk.LEFT, padx=(4,0))

        # ─ Key Management ─
        section_label(parent, "KEY MANAGEMENT").pack(fill=tk.X, pady=(12,4))

        tk.Label(parent, text="Key name", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor=tk.W)
        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, pady=2)
        tk.Entry(row, textvariable=self.key_name, bg=BG2, fg=TEXT, font=FONT_MONO,
                 relief=tk.FLAT, insertbackground=ACCENT,
                 highlightthickness=1, highlightcolor=ACCENT, highlightbackground=BORDER,
                 width=16).pack(side=tk.LEFT, ipady=5)
        styled_button(row, "⚡ Generate Keys", self._generate_keys, "primary").pack(side=tk.LEFT, padx=(8,0))

        tk.Label(parent, text="Private key (.dat)", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(8,0))
        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, pady=2)
        tk.Entry(row, textvariable=self.private_key, bg=BG2, fg=ACCENT2, font=FONT_MONO,
                 relief=tk.FLAT, insertbackground=ACCENT,
                 highlightthickness=1, highlightcolor=ACCENT, highlightbackground=BORDER).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        styled_button(row, "Browse", lambda: self._browse_file(self.private_key, "*.dat"), "ghost").pack(side=tk.LEFT, padx=(4,0))

        tk.Label(parent, text="Public key (.dat)", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(4,0))
        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, pady=2)
        tk.Entry(row, textvariable=self.public_key, bg=BG2, fg=GREEN, font=FONT_MONO,
                 relief=tk.FLAT, insertbackground=ACCENT,
                 highlightthickness=1, highlightcolor=ACCENT, highlightbackground=BORDER).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        styled_button(row, "Browse", lambda: self._browse_file(self.public_key, "*.dat"), "ghost").pack(side=tk.LEFT, padx=(4,0))

        # ─ Board & Vehicle ─
        section_label(parent, "TARGET CONFIGURATION").pack(fill=tk.X, pady=(12,4))

        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, pady=2)
        col1 = tk.Frame(row, bg=BG)
        col1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,4))
        col2 = tk.Frame(row, bg=BG)
        col2.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(col1, text="Board", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor=tk.W)
        board_cb = ttk.Combobox(col1, textvariable=self.board, values=sorted(ARDUPILOT_BOARDS),
                                font=FONT_MONO, state="normal")
        board_cb.pack(fill=tk.X, ipady=3)

        tk.Label(col2, text="Vehicle", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor=tk.W)
        vehicle_cb = ttk.Combobox(col2, textvariable=self.vehicle, values=VEHICLE_TYPES,
                                  font=FONT_MONO, state="readonly")
        vehicle_cb.pack(fill=tk.X, ipady=3)

        # Style comboboxes
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground=BG2, background=BG3,
                        foreground=TEXT, selectbackground=ACCENT,
                        selectforeground=BG, bordercolor=BORDER)

        # ─ Build ─
        section_label(parent, "BUILD").pack(fill=tk.X, pady=(12,4))

        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, pady=2)
        styled_button(row, "🔨 Build Bootloader", self._build_bootloader, "warning").pack(side=tk.LEFT, padx=(0,4))
        styled_button(row, "🔨 Build Firmware", self._build_firmware, "primary").pack(side=tk.LEFT)

        row2 = tk.Frame(parent, bg=BG)
        row2.pack(fill=tk.X, pady=(4,0))
        styled_button(row2, "🔨 Build Both", self._build_both, "success").pack(fill=tk.X)

        # ─ Sign ─
        section_label(parent, "SIGN FIRMWARE").pack(fill=tk.X, pady=(12,4))

        tk.Label(parent, text="Firmware (.apj)", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor=tk.W)
        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, pady=2)
        tk.Entry(row, textvariable=self.firmware_path, bg=BG2, fg=TEXT, font=FONT_MONO,
                 relief=tk.FLAT, insertbackground=ACCENT,
                 highlightthickness=1, highlightcolor=ACCENT, highlightbackground=BORDER).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        styled_button(row, "Browse", lambda: self._browse_file(self.firmware_path, "*.apj"), "ghost").pack(side=tk.LEFT, padx=(4,0))
        styled_button(parent, "✍️  Sign Firmware", self._sign_firmware, "primary").pack(fill=tk.X, pady=(4,0))

        # ─ Flash ─
        section_label(parent, "FLASH").pack(fill=tk.X, pady=(12,4))

        # Auto-detect status display
        detect_frame = tk.Frame(parent, bg=BG2, padx=8, pady=6)
        detect_frame.pack(fill=tk.X, pady=2)
        tk.Label(detect_frame, text="🔌 Port", bg=BG2, fg=MUTED, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.port_label = tk.Label(detect_frame, textvariable=self.serial_port, bg=BG2, fg=ACCENT, font=FONT_MONO)
        self.port_label.pack(side=tk.LEFT, padx=(8,0))

        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Override port (optional)", bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(anchor=tk.W)
        row2 = tk.Frame(parent, bg=BG)
        row2.pack(fill=tk.X)
        self.port_cb = ttk.Combobox(row2, textvariable=self.serial_port, font=FONT_MONO)
        self.port_cb.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        styled_button(row2, "↺ Scan", self._refresh_ports, "ghost").pack(side=tk.LEFT, padx=(4,0))

        row3 = tk.Frame(parent, bg=BG)
        row3.pack(fill=tk.X, pady=(6,0))
        styled_button(row3, "⚡ Flash Firmware (Auth)", self._flash_firmware, "success").pack(fill=tk.X)

        # ─ Quick Actions ─
        section_label(parent, "QUICK ACTIONS").pack(fill=tk.X, pady=(12,4))
        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, pady=2)
        styled_button(row, "🚀 Full Pipeline", self._full_pipeline, "success").pack(side=tk.LEFT, padx=(0,4))
        styled_button(row, "🛑 Stop", self._stop, "danger").pack(side=tk.LEFT)

        tk.Frame(parent, bg=BG, height=20).pack()

    def _build_terminal(self, parent):
        header = tk.Frame(parent, bg=BG3, height=32)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="● TERMINAL OUTPUT", bg=BG3, fg=GREEN, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=12, pady=6)
        styled_button(header, "Clear", lambda: self.terminal.clear(), "ghost").pack(side=tk.RIGHT, padx=8, pady=4)

        self.terminal = TerminalWidget(parent)
        self.terminal.pack(fill=tk.BOTH, expand=True, pady=(1,0))

        # Progress bar
        self.progress = ttk.Progressbar(parent, mode='indeterminate', style="green.Horizontal.TProgressbar")
        self.progress.pack(fill=tk.X, pady=(4,0))

        style = ttk.Style()
        style.configure("green.Horizontal.TProgressbar", background=GREEN, troughcolor=BG3)

    def _browse_dir(self, var):
        d = filedialog.askdirectory(initialdir=var.get())
        if d:
            var.set(d)

    def _browse_file(self, var, pattern):
        f = filedialog.askopenfilename(filetypes=[("Key files", pattern), ("All", "*")])
        if f:
            var.set(f)

    def _refresh_ports(self):
        import serial.tools.list_ports as lp
        ports_info = list(lp.comports())
        by_id = glob.glob("/dev/serial/by-id/*")
        all_ports = [p.device for p in ports_info] + by_id
        self.port_cb['values'] = all_ports

        # Auto-detect board from USB descriptor
        for p in ports_info:
            desc = f"{p.description} {p.manufacturer or ''} {p.product or ''}".lower()
            matched = None
            # Match by common keywords
            board_keywords = {
                "cuav": ["CUAV V5 Plus", "CUAV V5 Nano"],
                "pixhawk4": ["Holybro Pixhawk 4"],
                "pixhawk6": ["Holybro Pixhawk6X"],
                "pixhawk6c": ["Holybro Pixhawk6C"],
                "durandal": ["Holybro Durandal H7"],
                "kakuteh7": ["Holybro Kakute H7 V1"],
                "kakutef7": ["Holybro Kakute F7"],
                "kakutef4": ["Holybro Kakute F4"],
                "cube": ["CubePilot Cube Orange"],
                "matek": ["Mateksys H743-Wing"],
                "speedybee": ["SpeedyBee F405 AIO"],
                "omnibus": ["Omnibus F4 Pro"],
                "pixracer": ["mRo Pixracer"],
            }
            for keyword, board_names in board_keywords.items():
                if keyword in desc:
                    matched = board_names[0]
                    break

            # Also try matching against our board map keys
            if not matched:
                for display_name in ARDUPILOT_BOARDS:
                    waf = ARDUPILOT_BOARDS_MAP.get(display_name, "")
                    if waf.lower() in desc or display_name.lower() in desc:
                        matched = display_name
                        break

            if matched:
                self.board.set(matched)
                self.serial_port.set(p.device)
                self._log(f"\n🔍 Auto-detected: {matched} on {p.device}\n", "success")
                return

        # Fallback: just set first port
        if all_ports and not self.serial_port.get():
            self.serial_port.set(all_ports[0])

        # Start background auto-detect polling
        self.after(3000, self._refresh_ports)

    def _log(self, text, tag=None):
        self.terminal.write(text, tag)

    def _run_cmd(self, cmd, cwd=None, success_msg=None, on_done=None):
        """Run a shell command in a thread, stream output to terminal"""
        if self.running:
            self._log("⚠ Another process is running. Please wait.\n", "warn")
            return

        self.running = True
        self.progress.start(10)
        self.status.set("Running...", "running")
        self._log(f"\n$ {' '.join(cmd)}\n", "cmd")

        def run():
            try:
                proc = subprocess.Popen(
                    cmd, cwd=cwd or self.ardupilot_path.get(),
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1
                )
                for line in proc.stdout:
                    tag = None
                    if "error" in line.lower():   tag = "error"
                    elif "warning" in line.lower(): tag = "warn"
                    elif "ok" in line.lower() or "success" in line.lower() or "done" in line.lower(): tag = "success"
                    self.after(0, self._log, line, tag)

                proc.wait()
                if proc.returncode == 0:
                    msg = success_msg or "✅ Done!\n"
                    self.after(0, self._log, f"\n{msg}\n", "success")
                    self.after(0, self.status.set, "Success", "ok")
                else:
                    self.after(0, self._log, f"\n❌ Failed (exit {proc.returncode})\n", "error")
                    self.after(0, self.status.set, "Failed", "error")
            except Exception as e:
                self.after(0, self._log, f"\n❌ Error: {e}\n", "error")
                self.after(0, self.status.set, "Error", "error")
            finally:
                self.running = False
                self.after(0, self.progress.stop)
                if on_done:
                    self.after(0, on_done)

        threading.Thread(target=run, daemon=True).start()

    def _validate(self, *checks):
        """Validate required fields. checks: list of (var, name)"""
        for var, name in checks:
            if not var.get():
                messagebox.showerror("Missing", f"Please set: {name}")
                return False
        return True

    # ─── Actions ─────────────────────────────────────────────────────────────

    def _generate_keys(self):
        if not self._validate((self.ardupilot_path, "ArduPilot path")):
            return
        name = self.key_name.get().strip()
        if not name:
            messagebox.showerror("Missing", "Enter a key name first")
            return

        ap = self.ardupilot_path.get()
        self._log(f"\n🔑 Generating key pair: {name}\n", "info")

        def run():
            try:
                result = subprocess.run(
                    ["python3", "Tools/scripts/signing/generate_keys.py", name],
                    cwd=ap, capture_output=True, text=True
                )
                self.after(0, self._log, result.stdout, "success")
                self.after(0, self._log, result.stderr, "warn" if result.returncode != 0 else None)

                priv = os.path.join(ap, f"{name}_private_key.dat")
                pub  = os.path.join(ap, f"{name}_public_key.dat")
                if os.path.exists(priv):
                    self.after(0, self.private_key.set, priv)
                    self.after(0, self.public_key.set, pub)
                    self.after(0, self._log, f"\n✅ Keys saved:\n  Private: {priv}\n  Public:  {pub}\n", "success")
                    self.after(0, self.status.set, f"Keys generated: {name}", "ok")
                    # Backup reminder
                    self.after(0, messagebox.showinfo, "Key Generated",
                               f"Keys saved!\n\n⚠️ BACK UP your private key:\n{priv}\n\nWithout it you cannot update firmware!")
            except Exception as e:
                self.after(0, self._log, f"Error: {e}\n", "error")

        threading.Thread(target=run, daemon=True).start()

    def _build_bootloader(self, on_done=None):
        if not self._validate(
            (self.ardupilot_path, "ArduPilot path"),
            (self.public_key, "Public key"),
            (self.board, "Board")
        ):
            return
        self._log(f"\n🔨 Building secure bootloader for {self.board.get()}\n", "info")
        board_waf = ARDUPILOT_BOARDS_MAP.get(self.board.get(), self.board.get())
        self._run_cmd([
            "python3", "Tools/scripts/build_bootloaders.py",
            board_waf,
            f"--signing-key={self.public_key.get()}"
        ], success_msg="✅ Bootloader built!", on_done=on_done)

    def _build_firmware(self, on_done=None):
        if not self._validate(
            (self.ardupilot_path, "ArduPilot path"),
            (self.board, "Board"),
            (self.vehicle, "Vehicle type")
        ):
            return
        ap = self.ardupilot_path.get()
        board = self.board.get()
        board_waf = ARDUPILOT_BOARDS_MAP.get(board, board)
        vehicle = self.vehicle.get()
        self._log(f"\n🔨 Building {vehicle} firmware for {board} ({board_waf})\n", "info")

        def run_build():
            # Configure
            self._run_cmd(
                ["./waf", "configure", "--board", board_waf, "--signed-fw"],
                on_done=lambda: self._run_cmd(
                    ["./waf", vehicle],
                    success_msg=f"✅ {vehicle} firmware built!",
                    on_done=lambda: self._auto_set_firmware(on_done)
                )
            )
        run_build()

    def _auto_set_firmware(self, on_done=None):
        ap = self.ardupilot_path.get()
        board = self.board.get()
        vehicle = self.vehicle.get()
        apj = os.path.join(ap, "build", ARDUPILOT_BOARDS_MAP.get(board, board), "bin", f"ardu{vehicle}.apj")
        if os.path.exists(apj):
            self.firmware_path.set(apj)
            self._log(f"📦 Firmware: {apj}\n", "info")
        if on_done:
            on_done()

    def _build_both(self):
        self._build_bootloader(on_done=self._build_firmware)

    def _sign_firmware(self, on_done=None):
        if not self._validate(
            (self.firmware_path, "Firmware .apj path"),
            (self.private_key, "Private key")
        ):
            return
        self._log(f"\n✍️  Signing firmware\n", "info")
        self._run_cmd([
            "python3", "Tools/scripts/signing/make_secure_fw.py",
            self.firmware_path.get(),
            self.private_key.get()
        ], success_msg="✅ Firmware signed!", on_done=on_done)

    def _flash_firmware(self):
        if not self._validate(
            (self.firmware_path, "Firmware .apj path"),
            (self.private_key, "Private key"),
            (self.serial_port, "Serial port")
        ):
            return
        self._log(f"\n⚡ Flashing to {self.serial_port.get()}\n", "info")
        self._log("ℹ Unplug and replug USB if board doesn't respond\n", "warn")
        self._run_cmd([
            "python3", "Tools/scripts/uploader.py",
            self.firmware_path.get(),
            "--auth-key", self.private_key.get(),
            "--port", self.serial_port.get(),
            "--baud-bootloader", "115200"
        ], success_msg="✅ Firmware flashed!")

    def _full_pipeline(self):
        """Run: build bootloader → build firmware → sign → flash"""
        if not self._validate(
            (self.ardupilot_path, "ArduPilot path"),
            (self.board, "Board"),
            (self.vehicle, "Vehicle type"),
            (self.private_key, "Private key"),
            (self.public_key, "Public key"),
            (self.serial_port, "Serial port")
        ):
            return

        self._log("\n🚀 FULL PIPELINE START\n", "info")
        self._log(f"  Board:   {self.board.get()}\n", "muted")
        self._log(f"  Vehicle: {self.vehicle.get()}\n", "muted")
        self._log(f"  Key:     {self.private_key.get()}\n", "muted")

        def step3_flash():
            self._flash_firmware()

        def step2_sign():
            self._sign_firmware(on_done=step3_flash)

        def step1_build():
            self._build_firmware(on_done=step2_sign)

        self._build_bootloader(on_done=step1_build)

    def _stop(self):
        self.running = False
        self.progress.stop()
        self.status.set("Stopped", "idle")
        self._log("\n🛑 Stopped by user\n", "warn")


def main():
    # Check dependencies
    missing = []
    try:
        import serial
    except ImportError:
        missing.append("pyserial")

    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip3 install {' '.join(missing)} --break-system-packages")

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
