#!/usr/bin/env python3
"""
Personal auto-clicker for macOS.
- F9: toggle start/stop
- F10: quit
"""

import threading
import time
import tkinter as tk
from tkinter import ttk

import pyautogui
from pynput import keyboard

pyautogui.FAILSAFE = True  # move mouse to top-left corner to abort


class AutoClicker:
    def __init__(self):
        self.running = False
        self.click_thread = None

        self.root = tk.Tk()
        self.root.title("Auto Clicker")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self._build_ui()
        self._start_hotkey_listener()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # Interval setting
        interval_frame = ttk.LabelFrame(self.root, text="クリック間隔")
        interval_frame.pack(fill="x", **pad)

        ttk.Label(interval_frame, text="間隔 (秒):").grid(row=0, column=0, **pad)
        self.interval_var = tk.DoubleVar(value=0.1)
        ttk.Spinbox(
            interval_frame,
            from_=0.01,
            to=60.0,
            increment=0.1,
            textvariable=self.interval_var,
            width=8,
            format="%.2f",
        ).grid(row=0, column=1, **pad)

        # Mouse button selection
        button_frame = ttk.LabelFrame(self.root, text="マウスボタン")
        button_frame.pack(fill="x", **pad)

        self.button_var = tk.StringVar(value="left")
        for col, (label, val) in enumerate(
            [("左クリック", "left"), ("右クリック", "right"), ("中クリック", "middle")]
        ):
            ttk.Radiobutton(
                button_frame, text=label, variable=self.button_var, value=val
            ).grid(row=0, column=col, **pad)

        # Click position selection
        pos_frame = ttk.LabelFrame(self.root, text="クリック位置")
        pos_frame.pack(fill="x", **pad)

        self.pos_var = tk.StringVar(value="current")
        ttk.Radiobutton(
            pos_frame, text="現在のカーソル位置", variable=self.pos_var, value="current"
        ).grid(row=0, column=0, **pad)
        ttk.Radiobutton(
            pos_frame, text="固定位置:", variable=self.pos_var, value="fixed"
        ).grid(row=1, column=0, **pad)

        coord_frame = ttk.Frame(pos_frame)
        coord_frame.grid(row=1, column=1, **pad)
        ttk.Label(coord_frame, text="X:").pack(side="left")
        self.x_var = tk.IntVar(value=0)
        ttk.Spinbox(coord_frame, from_=0, to=9999, textvariable=self.x_var, width=6).pack(side="left", padx=2)
        ttk.Label(coord_frame, text="Y:").pack(side="left", padx=(8, 0))
        self.y_var = tk.IntVar(value=0)
        ttk.Spinbox(coord_frame, from_=0, to=9999, textvariable=self.y_var, width=6).pack(side="left", padx=2)

        ttk.Button(pos_frame, text="現在位置を取得", command=self._capture_pos).grid(
            row=2, column=0, columnspan=2, **pad
        )

        # Status & controls
        ctrl_frame = ttk.Frame(self.root)
        ctrl_frame.pack(fill="x", **pad)

        self.status_var = tk.StringVar(value="停止中")
        ttk.Label(ctrl_frame, textvariable=self.status_var, font=("", 12, "bold")).pack(side="left", padx=10)

        self.toggle_btn = ttk.Button(ctrl_frame, text="開始 (F9)", command=self.toggle)
        self.toggle_btn.pack(side="right", padx=5)

        # Hotkey info
        ttk.Label(
            self.root,
            text="F9: 開始/停止　F10: 終了　マウスを左上隅に移動: 緊急停止",
            foreground="gray",
        ).pack(pady=(0, 8))

    def _capture_pos(self):
        self.root.withdraw()
        time.sleep(2)
        x, y = pyautogui.position()
        self.x_var.set(x)
        self.y_var.set(y)
        self.pos_var.set("fixed")
        self.root.deiconify()

    def _click_loop(self):
        while self.running:
            try:
                interval = self.interval_var.get()
                button = self.button_var.get()
                if self.pos_var.get() == "fixed":
                    pyautogui.click(self.x_var.get(), self.y_var.get(), button=button)
                else:
                    pyautogui.click(button=button)
                time.sleep(interval)
            except pyautogui.FailSafeException:
                self.running = False
                self.root.after(0, self._update_ui_stopped)
                break

    def toggle(self):
        if self.running:
            self._stop()
        else:
            self._start()

    def _start(self):
        self.running = True
        self.click_thread = threading.Thread(target=self._click_loop, daemon=True)
        self.click_thread.start()
        self.status_var.set("実行中 ●")
        self.toggle_btn.config(text="停止 (F9)")

    def _stop(self):
        self.running = False
        self.status_var.set("停止中")
        self.toggle_btn.config(text="開始 (F9)")

    def _update_ui_stopped(self):
        self.status_var.set("停止中 (フェイルセーフ)")
        self.toggle_btn.config(text="開始 (F9)")

    def _start_hotkey_listener(self):
        def on_press(key):
            if key == keyboard.Key.f9:
                self.root.after(0, self.toggle)
            elif key == keyboard.Key.f10:
                self.root.after(0, self.root.quit)

        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()

    def run(self):
        self.root.mainloop()
        self.running = False


if __name__ == "__main__":
    AutoClicker().run()
