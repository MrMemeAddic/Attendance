"""
main.py — Face Recognition App entry point
Tkinter 3-tab GUI: Register | Recognize | Manage
"""
import calendar as _calendar
from datetime import datetime as _dt
# ── Fix Tcl/Tk paths BEFORE importing tkinter (Python 3.14 on Windows) ──
import os as _os, sys
_TCL_SEARCH = [
    # AppData (standard Python.org installer)
    _os.path.join(_os.environ.get("LOCALAPPDATA", ""),
                  "Programs", "Python", "Python314", "tcl", "tcl8.6"),
    # Fallback: base_prefix / tcl / tcl8.6
    _os.path.join(getattr(sys, "base_prefix", ""), "tcl", "tcl8.6"),
]
for _tcl in _TCL_SEARCH:
    if _os.path.isfile(_os.path.join(_tcl, "init.tcl")):
        _os.environ.setdefault("TCL_LIBRARY", _tcl)
        _os.environ.setdefault("TK_LIBRARY",
                               _tcl.replace("tcl8.6", "tk8.6"))
        break
del _os, _TCL_SEARCH
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from core.database import FaceDatabase
from core.embedder import FaceEmbedder
from core.matcher  import FaceMatcher
from ui.register_panel  import RegisterPanel
from ui.recognize_panel import RecognizePanel
from ui.manage_panel    import ManagePanel

APP_TITLE = "Jagte Raho"
DARK  = "#1a1a2e"
MID   = "#16213e"
ACC   = "#0f3460"
GREEN = "#00e676"
WHITE = "#e0e0e0"


class SplashScreen(tk.Toplevel):
    """Loading screen shown while FaceNet model is downloading/loading."""

    def __init__(self, master):
        super().__init__(master)
        self.overrideredirect(True)
        self.configure(bg=DARK)
        w, h = 420, 200
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        tk.Label(self, text="Jagte Raho", font=("Segoe UI", 36, "bold"),
                 bg=DARK, fg=GREEN).pack(pady=(30, 4))
        tk.Label(self, text="Loading FaceNet model…",
                 font=("Segoe UI", 11), bg=DARK, fg="#aaa").pack()

        self.bar = ttk.Progressbar(self, mode="indeterminate", length=340)
        self.bar.pack(pady=16)
        self.bar.start(12)

    def close(self):
        self.bar.stop()
        self.destroy()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg=DARK)
        self.minsize(720, 640)
        self._center()
        self.state("zoomed")          # start maximized (fills whole screen)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── Header ────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=ACC, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⬡  Jagte Raho",
                 font=("Segoe UI", 20, "bold"), bg=ACC, fg=GREEN).pack(side="left", padx=20)
        self.known_lbl = tk.Label(hdr, text="", font=("Segoe UI", 10),
                                  bg=ACC, fg="#aaa")
        self.known_lbl.pack(side="right", padx=20)

        # ── Clock & Calendar ──────────────────────────────────────────
        self._cal_popup = None          # reference to open calendar window
        self._cal_year  = None
        self._cal_month = None

        clock_frame = tk.Frame(hdr, bg=ACC)
        clock_frame.pack(side="right", padx=14)

        # Time label (HH:MM:SS)
        self._clock_lbl = tk.Label(
            clock_frame,
            font=("Segoe UI", 17, "bold"),
            bg=ACC, fg=GREEN, cursor="hand2"
        )
        self._clock_lbl.pack()

        # Date label (Wed, 24 Jun 2026)
        self._date_lbl = tk.Label(
            clock_frame,
            font=("Segoe UI", 9),
            bg=ACC, fg="#b0c4de", cursor="hand2"
        )
        self._date_lbl.pack()

        # Clicking either label toggles the calendar popup
        for w in (self._clock_lbl, self._date_lbl, clock_frame):
            w.bind("<Button-1>", self._toggle_calendar)

        self._tick()   # start the live clock

        # ── Shared resources (lazy-loaded in background) ───────────────
        self.db = FaceDatabase()
        self.embedder: FaceEmbedder | None = None
        self.matcher  = FaceMatcher()

        # Show splash while loading model
        splash = SplashScreen(self)
        self.withdraw()

        def _load():
            try:
                self.embedder = FaceEmbedder()          # Downloads model if needed
                self.matcher.reload(self.db)
            except Exception as e:
                self.after(0, lambda: (
                    splash.close(),
                    messagebox.showerror("Model Error", str(e)),
                    self.destroy()
                ))
                return
            self.after(0, lambda: self._on_loaded(splash))

        threading.Thread(target=_load, daemon=True).start()

    def _on_loaded(self, splash: SplashScreen):
        splash.close()
        self._build_tabs()
        self.deiconify()
        self._update_known_count()

    # ── Tabs ──────────────────────────────────────────────────────────

    def _build_tabs(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=MID, foreground=WHITE,
                        font=("Segoe UI", 11, "bold"), padding=(20, 8))
        style.map("TNotebook.Tab",
                  background=[("selected", ACC)],
                  foreground=[("selected", GREEN)])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        def _on_gallery_change():
            self.matcher.reload(self.db)
            self._update_known_count()

        self._reg_panel = RegisterPanel(
            nb, db=self.db, embedder=self.embedder,
            on_registered=_on_gallery_change, bg=DARK
        )
        self._rec_panel = RecognizePanel(
            nb, db=self.db, embedder=self.embedder, matcher=self.matcher, bg=DARK
        )
        self._mgr_panel = ManagePanel(
            nb, db=self.db, matcher=self.matcher,
            on_change=_on_gallery_change, bg=DARK
        )

        nb.add(self._reg_panel, text="  ➕  Register  ")
        nb.add(self._rec_panel, text="  👁  Recognize  ")
        nb.add(self._mgr_panel, text="  🗂  Manage  ")

        # Auto-refresh manage panel when tab selected
        nb.bind("<<NotebookTabChanged>>", lambda e: (
            self._mgr_panel.refresh()
            if nb.index(nb.select()) == 2 else None
        ))

    # ── Clock helpers ─────────────────────────────────────────────────

    def _tick(self):
        """Update the clock every second."""
        now = _dt.now()
        self._clock_lbl.config(text=now.strftime("%I:%M:%S %p"))
        self._date_lbl.config(text=now.strftime("%a, %d %b %Y"))
        self.after(1000, self._tick)

    def _toggle_calendar(self, event=None):
        """Show or hide the mini calendar popup."""
        if self._cal_popup and self._cal_popup.winfo_exists():
            self._cal_popup.destroy()
            self._cal_popup = None
            return
        now = _dt.now()
        self._cal_year  = now.year
        self._cal_month = now.month
        self._show_calendar()

    def _show_calendar(self):
        """Create (or re-draw) the floating calendar Toplevel."""
        today = _dt.now()

        if self._cal_popup and self._cal_popup.winfo_exists():
            self._cal_popup.destroy()

        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.configure(bg="#0f3460")
        popup.attributes("-topmost", True)
        self._cal_popup = popup

        # Position below the clock
        self.update_idletasks()
        cx = self._clock_lbl.winfo_rootx()
        cy = self._clock_lbl.winfo_rooty() + self._clock_lbl.winfo_height() + 4
        popup.geometry(f"240x230+{cx}+{cy}")

        # Close when clicking anywhere outside
        popup.bind("<FocusOut>", lambda e: popup.destroy() if popup.winfo_exists() else None)
        popup.focus_set()

        CAL_BG   = "#0f3460"
        HDR_FG   = GREEN
        DAY_FG   = "#e0e0e0"
        TODAY_BG = GREEN
        TODAY_FG = "#1a1a2e"
        WKD_FG   = "#ff6b6b"
        BTN_FG   = "#b0c4de"

        # ── Month/Year navigation row ──
        nav = tk.Frame(popup, bg=CAL_BG)
        nav.pack(fill="x", padx=6, pady=(6, 2))

        def _prev():
            self._cal_month -= 1
            if self._cal_month < 1:
                self._cal_month = 12
                self._cal_year -= 1
            self._show_calendar()

        def _next():
            self._cal_month += 1
            if self._cal_month > 12:
                self._cal_month = 1
                self._cal_year += 1
            self._show_calendar()

        tk.Button(nav, text="◀", command=_prev,
                  bg=CAL_BG, fg=BTN_FG, relief="flat",
                  font=("Segoe UI", 11, "bold"), bd=0,
                  activebackground="#16213e", activeforeground=GREEN,
                  cursor="hand2").pack(side="left")

        month_name = _calendar.month_abbr[self._cal_month]
        tk.Label(nav, text=f"{month_name}  {self._cal_year}",
                 bg=CAL_BG, fg=HDR_FG,
                 font=("Segoe UI", 12, "bold")).pack(side="left", expand=True)

        tk.Button(nav, text="▶", command=_next,
                  bg=CAL_BG, fg=BTN_FG, relief="flat",
                  font=("Segoe UI", 11, "bold"), bd=0,
                  activebackground="#16213e", activeforeground=GREEN,
                  cursor="hand2").pack(side="right")

        # ── Weekday headers ──
        grid = tk.Frame(popup, bg=CAL_BG)
        grid.pack(padx=6, pady=2)

        for col, day_hdr in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            fg = WKD_FG if col >= 5 else "#7ec8e3"
            tk.Label(grid, text=day_hdr, width=3,
                     bg=CAL_BG, fg=fg,
                     font=("Segoe UI", 8, "bold")).grid(row=0, column=col, pady=(0, 2))

        # ── Day cells ──
        weeks = _calendar.monthcalendar(self._cal_year, self._cal_month)
        for row_i, week in enumerate(weeks):
            for col_i, day in enumerate(week):
                if day == 0:
                    tk.Label(grid, text="", width=3, bg=CAL_BG).grid(
                        row=row_i + 1, column=col_i)
                    continue

                is_today = (
                    day == today.day
                    and self._cal_month == today.month
                    and self._cal_year  == today.year
                )
                cell_bg = TODAY_BG if is_today else CAL_BG
                cell_fg = TODAY_FG if is_today else (
                    WKD_FG if col_i >= 5 else DAY_FG)
                cell_font = ("Segoe UI", 9, "bold") if is_today else ("Segoe UI", 9)

                tk.Label(grid, text=str(day), width=3,
                         bg=cell_bg, fg=cell_fg,
                         font=cell_font,
                         relief="flat").grid(row=row_i + 1, column=col_i, pady=1)

        # ── Thin separator + "Today" jump ──
        sep = tk.Frame(popup, bg="#16213e", height=1)
        sep.pack(fill="x", padx=6, pady=(4, 0))

        def _jump_today():
            now2 = _dt.now()
            self._cal_year  = now2.year
            self._cal_month = now2.month
            self._show_calendar()

        tk.Button(popup, text="Today", command=_jump_today,
                  bg=CAL_BG, fg=GREEN, relief="flat",
                  font=("Segoe UI", 9, "bold"), bd=0,
                  activebackground="#16213e", activeforeground=GREEN,
                  cursor="hand2").pack(pady=4)

    # ── Helpers ───────────────────────────────────────────────────────

    def _update_known_count(self):
        n = len(self.db.get_all_persons())
        self.known_lbl.config(text=f"👤 {n} registered person{'s' if n != 1 else ''}")

    def _center(self):
        self.update_idletasks()
        w, h = 760, 680
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _on_close(self):
        if hasattr(self, "_rec_panel"):
            self._rec_panel.stop()
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
