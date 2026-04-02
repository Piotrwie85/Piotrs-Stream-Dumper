"""
Piotr's Stream Dumper
─────────────────────
Dumps a live stream URL directly to an MKV file using ffmpeg.
Requires:  pip install customtkinter
           ffmpeg must be on PATH (https://ffmpeg.org/download.html)
"""

import customtkinter as ctk
from tkinter import messagebox
import subprocess
import threading
import os
import signal
import sys

# ── Appearance ─────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Palette ────────────────────────────────────────────────────────────────────
BG          = "#0d0f18"
SURFACE     = "#161925"
SURFACE2    = "#1e2233"
BORDER      = "#2a2f45"
ACCENT      = "#4f8ef7"
ACCENT_HOV  = "#3a78e8"
DANGER      = "#d95f5f"
SUCCESS     = "#3dba68"
WARNING     = "#e8a628"
TEXT        = "#dde1f0"
TEXT_DIM    = "#6b7394"
FONT_TITLE  = ("Segoe UI Semibold", 14)
FONT_LABEL  = ("Segoe UI", 9)
FONT_ENTRY  = ("Consolas", 11)
FONT_BTN    = ("Segoe UI Semibold", 10)
FONT_STATUS = ("Segoe UI", 9)


class StreamDumper(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.ffmpeg_process = None

        # ── Window setup ───────────────────────────────────────────────────
        self.title("Piotr's Stream Dumper")
        self.configure(fg_color=BG)
        self.resizable(False, False)
        self._set_dark_titlebar()
        self._build_ui()
        self.update_idletasks()

    # ── Dark title bar (Windows 10/11 only) ────────────────────────────────────
    def _set_dark_titlebar(self):
        try:
            from ctypes import windll, byref, sizeof, c_int
            hwnd = windll.user32.GetParent(self.winfo_id())
            windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, byref(c_int(1)), sizeof(c_int))
        except Exception:
            pass

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):

        # ── Header bar ─────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=54)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="  ●  Piotr's Stream Dumper",
            font=FONT_TITLE, text_color=TEXT, anchor="w"
        ).pack(side="left", padx=18)

        ctk.CTkLabel(
            header, text="MKV · ffmpeg  ",
            font=("Segoe UI", 9), text_color=TEXT_DIM, anchor="e"
        ).pack(side="right", padx=18)

        ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")

        # ── Body ───────────────────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        body.pack(fill="both", padx=24, pady=20)

        # Stream URL
        self._section_label(body, "Stream URL")
        url_row = ctk.CTkFrame(body, fg_color="transparent")
        url_row.pack(fill="x", pady=(4, 14))

        self.stream_entry = ctk.CTkEntry(
            url_row, width=390, height=38,
            font=FONT_ENTRY, fg_color=SURFACE,
            border_color=BORDER, border_width=1,
            text_color=TEXT,
            placeholder_text="rtmp://  or  http://...",
            placeholder_text_color=TEXT_DIM,
        )
        self.stream_entry.pack(side="left")
        self.stream_entry.bind("<Button-3>", lambda e: self._context_menu(e, self.stream_entry))

        ctk.CTkButton(
            url_row, text="Paste", width=72, height=38,
            font=FONT_LABEL,
            fg_color=SURFACE2, hover_color=BORDER,
            text_color=TEXT_DIM,
            border_width=1, border_color=BORDER,
            corner_radius=6,
            command=self._paste_to_stream,
        ).pack(side="left", padx=(8, 0))

        # Output filename
        self._section_label(body, "Output Filename")
        out_row = ctk.CTkFrame(body, fg_color="transparent")
        out_row.pack(fill="x", pady=(4, 6))

        self.output_entry = ctk.CTkEntry(
            out_row, width=390, height=38,
            font=FONT_ENTRY, fg_color=SURFACE,
            border_color=BORDER, border_width=1,
            text_color=TEXT,
            placeholder_text="recording_001",
            placeholder_text_color=TEXT_DIM,
        )
        self.output_entry.pack(side="left")
        self.output_entry.bind("<Button-3>", lambda e: self._context_menu(e, self.output_entry))

        ctk.CTkLabel(
            out_row, text=".mkv",
            font=("Consolas", 11), text_color=TEXT_DIM
        ).pack(side="left", padx=(8, 0))

        # Save path hint
        ctk.CTkLabel(
            body,
            text=f"Saves to: {os.getcwd()}",
            font=("Segoe UI", 8),
            text_color=TEXT_DIM, anchor="w"
        ).pack(fill="x", pady=(2, 16))

        # Divider
        ctk.CTkFrame(body, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", pady=(0, 16))

        # Buttons
        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x")

        self.start_btn = ctk.CTkButton(
            btn_row, text="▶  Start Dump",
            width=148, height=40,
            font=FONT_BTN,
            fg_color=ACCENT, hover_color=ACCENT_HOV,
            text_color="#ffffff", corner_radius=8,
            command=self.start_dump,
        )
        self.start_btn.pack(side="left", padx=(0, 10))

        self.stop_btn = ctk.CTkButton(
            btn_row, text="■  Stop",
            width=100, height=40,
            font=FONT_BTN,
            fg_color=SURFACE2, hover_color=BORDER,
            text_color=TEXT_DIM,
            border_width=1, border_color=BORDER,
            corner_radius=8,
            command=self.stop_dump,
        )
        self.stop_btn.pack(side="left")

        # ── Status bar ─────────────────────────────────────────────────────
        ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")

        status_bar = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=36)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)

        # Status dot (plain tk canvas — reliable, no deferred draw needed)
        import tkinter as tk
        self._dot_canvas = tk.Canvas(
            status_bar, width=10, height=10,
            bg=SURFACE, highlightthickness=0
        )
        self._dot_canvas.pack(side="left", padx=(14, 6), pady=12)
        self._dot = self._dot_canvas.create_oval(1, 1, 9, 9, fill=TEXT_DIM, outline="")

        self.status_label = ctk.CTkLabel(
            status_bar, text="Ready.",
            font=FONT_STATUS, text_color=TEXT_DIM, anchor="w"
        )
        self.status_label.pack(side="left")

    # ── Widget helpers ─────────────────────────────────────────────────────────
    def _section_label(self, parent, text):
        spaced = "  ".join(text.upper())
        ctk.CTkLabel(
            parent, text=spaced,
            font=("Segoe UI", 7, "bold"),
            text_color=TEXT_DIM, anchor="w"
        ).pack(anchor="w")

    def _set_status(self, text, colour=TEXT_DIM):
        self.status_label.configure(text=text, text_color=colour)
        self._dot_canvas.itemconfig(self._dot, fill=colour)

    def _context_menu(self, event, widget):
        """Right-click context menu (Cut / Copy / Paste / Select All)."""
        import tkinter as tk
        menu = tk.Menu(
            self, tearoff=0,
            bg=SURFACE2, fg=TEXT,
            activebackground=ACCENT, activeforeground="#ffffff",
            relief="flat", bd=0, font=FONT_LABEL
        )
        menu.add_command(label="Cut",        command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy",       command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste",      command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: widget.select_range(0, "end"))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _paste_to_stream(self):
        try:
            text = self.clipboard_get()
            self.stream_entry.delete(0, "end")
            self.stream_entry.insert(0, text.strip())
        except Exception:
            messagebox.showwarning("Clipboard", "Nothing found in clipboard.")

    # ── Core logic ─────────────────────────────────────────────────────────────
    def start_dump(self):
        url      = self.stream_entry.get().strip()
        filename = self.output_entry.get().strip()

        if not url:
            messagebox.showwarning("Missing Input", "Please enter a stream URL.")
            return
        if not filename:
            messagebox.showwarning("Missing Input", "Please enter an output file name.")
            return

        output_path = os.path.join(os.getcwd(), filename + ".mkv")

        cmd = [
            "ffmpeg", "-y",
            "-i", url,
            "-c", "copy",
            "-f", "matroska",
            output_path,
        ]

        self._set_status("Dumping stream…", SUCCESS)
        self.start_btn.configure(state="disabled", fg_color=SURFACE2, text_color=TEXT_DIM)

        thread = threading.Thread(target=self._run_ffmpeg, args=(cmd,), daemon=True)
        thread.start()

    def _run_ffmpeg(self, cmd):
        try:
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )

            for line in self.ffmpeg_process.stdout:
                if "error" in line.lower():
                    self.after(0, lambda: self._set_status(
                        "FFmpeg error — check URL or codec.", DANGER))

            self.ffmpeg_process.wait()
            rc = self.ffmpeg_process.returncode

            if rc == 0:
                self.after(0, lambda: self._set_status("Dump completed successfully.", SUCCESS))
            else:
                self.after(0, lambda: self._set_status("Dump stopped or failed.", DANGER))

        except FileNotFoundError:
            self.after(0, lambda: self._set_status(
                "ffmpeg not found — install it and add to PATH.", DANGER))
        except Exception as exc:
            msg = str(exc)
            self.after(0, lambda: self._set_status(f"Error: {msg}", DANGER))
        finally:
            self.after(0, self._reset_start_btn)

    def _reset_start_btn(self):
        self.start_btn.configure(state="normal", fg_color=ACCENT, text_color="#ffffff")

    def stop_dump(self):
        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:
            try:
                if sys.platform == "win32":
                    self.ffmpeg_process.terminate()
                else:
                    self.ffmpeg_process.send_signal(signal.SIGINT)
                self._set_status("Stopping stream…", WARNING)
            except Exception as exc:
                messagebox.showerror("Error", f"Could not stop process:\n{exc}")
        else:
            self._set_status("No active dump.", TEXT_DIM)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = StreamDumper()
    app.mainloop()
