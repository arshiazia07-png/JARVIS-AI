
import math
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path


# Find the existing JARVIS file in this folder
PROJECT_DIR = Path(__file__).resolve().parent
JARVIS_FILE = PROJECT_DIR / "jarvis.py"

BG = "#070B14"
PANEL = "#0D1524"
BORDER = "#1A2B43"
CYAN = "#50E6FF"
TEXT = "#E5F0FF"
MUTED = "#8295AD"


class JarvisDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S. | Personal AI")
        self.root.geometry("1000x650")
        self.root.minsize(820, 540)
        self.root.configure(bg=BG)

        self.events = queue.Queue()
        self.process = None
        self.frame_number = 0

        self._build_ui()

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(100, self._poll_output)
        self.root.after(80, self._animate_orb)

        self.start_jarvis()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 12))

        tk.Label(
            header,
            text="J.A.R.V.I.S.",
            font=("Segoe UI", 25, "bold"),
            bg=BG,
            fg=CYAN
        ).pack(side="left")

        tk.Label(
            header,
            text="PERSONAL AI  /  LOCAL OLLAMA BRAIN",
            font=("Consolas", 10),
            bg=BG,
            fg=MUTED
        ).pack(side="left", padx=18, pady=(9, 0))

        self.status_label = tk.Label(
            header,
            text="● STARTING",
            font=("Consolas", 11, "bold"),
            bg=BG,
            fg=CYAN
        )
        self.status_label.pack(side="right", pady=10)

        # Main two-panel layout
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=8)
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1, minsize=330)
        body.grid_columnconfigure(1, weight=1, minsize=350)

        left = tk.Frame(
            body, bg=PANEL,
            highlightbackground=BORDER, highlightthickness=1
        )
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        right = tk.Frame(
            body, bg=PANEL,
            highlightbackground=BORDER, highlightthickness=1
        )
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Left: animated visualizer
        tk.Label(
            left,
            text="SYSTEM VISUALIZER",
            font=("Consolas", 10, "bold"),
            bg=PANEL,
            fg=MUTED
        ).pack(anchor="w", padx=18, pady=(18, 0))

        self.canvas = tk.Canvas(
            left,
            bg=PANEL,
            highlightthickness=0,
            height=330
        )
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)

        tk.Label(
            left,
            text="VOICE INTERFACE  •  JARVIS CORE",
            font=("Consolas", 9),
            bg=PANEL,
            fg=CYAN
        ).pack(pady=(0, 18))

        # Right: live activity log
        tk.Label(
            right,
            text="ACTIVITY LOG",
            font=("Consolas", 10, "bold"),
            bg=PANEL,
            fg=MUTED
        ).pack(anchor="w", padx=18, pady=(18, 12))

        self.log = tk.Text(
            right,
            bg="#080E19",
            fg=TEXT,
            insertbackground=CYAN,
            font=("Consolas", 10),
            relief="flat",
            wrap="word",
            padx=14,
            pady=12,
            state="disabled"
        )
        self.log.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.log.tag_configure("JARVIS", foreground=CYAN)
        self.log.tag_configure("YOU", foreground="#B9A6FF")
        self.log.tag_configure("SYSTEM", foreground=MUTED)

        # Controls
        controls = tk.Frame(self.root, bg=BG)
        controls.pack(fill="x", padx=24, pady=(4, 20))

        tk.Button(
            controls,
            text="START JARVIS",
            command=self.start_jarvis,
            bg="#123A45",
            fg=CYAN,
            activebackground="#1B5261",
            activeforeground="white",
            relief="flat",
            font=("Consolas", 10, "bold"),
            padx=16,
            pady=10,
            cursor="hand2"
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            controls,
            text="STOP JARVIS",
            command=self.stop_jarvis,
            bg="#3C202B",
            fg="#FF8C9B",
            activebackground="#60303D",
            activeforeground="white",
            relief="flat",
            font=("Consolas", 10, "bold"),
            padx=16,
            pady=10,
            cursor="hand2"
        ).pack(side="left", padx=8)

        tk.Button(
            controls,
            text="CLEAR LOG",
            command=self.clear_log,
            bg="#182235",
            fg=TEXT,
            activebackground="#263750",
            activeforeground="white",
            relief="flat",
            font=("Consolas", 10),
            padx=16,
            pady=10,
            cursor="hand2"
        ).pack(side="right")

    def set_status(self, status):
        colors = {
            "STARTING": CYAN,
            "LISTENING": "#54F0BD",
            "STANDBY": "#54F0BD",
            "SPEAKING": "#B9A6FF",
            "COMMAND RECEIVED": CYAN,
            "STOPPING": "#FFBF69",
            "OFFLINE": "#FF8090",
            "ERROR": "#FF8090",
        }
        self.status_label.config(
            text=f"● {status}",
            fg=colors.get(status, CYAN)
        )

    def add_log(self, category, message):
        if not message:
            return

        self.log.configure(state="normal")
        self.log.insert("end", f"{category}: ", category)
        self.log.insert("end", message + "\n\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def start_jarvis(self):
        if self.process is not None and self.process.poll() is None:
            self.add_log("SYSTEM", "JARVIS is already running.")
            return

        if not JARVIS_FILE.exists():
            self.set_status("ERROR")
            self.add_log(
                "SYSTEM",
                f"Could not find {JARVIS_FILE.name}. "
                "Keep jarvis_gui.py beside jarvis.py."
            )
            return

        try:
            self.set_status("STARTING")
            self.add_log("SYSTEM", "Launching your existing JARVIS...")

            self.process = subprocess.Popen(
                [sys.executable, "-u", str(JARVIS_FILE)],
                cwd=str(PROJECT_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1
            )

            threading.Thread(
                target=self._read_output,
                args=(self.process,),
                daemon=True
            ).start()

        except Exception as error:
            self.set_status("ERROR")
            self.add_log("SYSTEM", str(error))

    def _read_output(self, process):
        try:
            if process.stdout:
                for line in process.stdout:
                    self.events.put(
                        ("line", process, line.rstrip("\r\n"))
                    )
        except Exception as error:
            self.events.put(("line", process, str(error)))
        finally:
            code = process.wait()
            self.events.put(("exit", process, code))

    def _handle_line(self, line):
        line = line.strip()

        if not line:
            return

        if line.startswith("JARVIS:"):
            self.set_status("SPEAKING")
            self.add_log("JARVIS", line.split(":", 1)[1].strip())

        elif line.startswith("YOU:"):
            self.set_status("COMMAND RECEIVED")
            self.add_log("YOU", line.split(":", 1)[1].strip())

        elif "Listening..." in line:
            self.set_status("LISTENING")

        elif "Waiting for wake word..." in line:
            self.set_status("STANDBY")

        else:
            self.add_log("SYSTEM", line)

    def _poll_output(self):
        try:
            while True:
                event = self.events.get_nowait()
                kind, process, value = event

                # Ignore late output from a previous process.
                if process is not self.process:
                    continue

                if kind == "line":
                    self._handle_line(value)

                elif kind == "exit":
                    self.process = None
                    self.set_status("OFFLINE")
                    self.add_log(
                        "SYSTEM",
                        f"JARVIS stopped (exit code {value})."
                    )

        except queue.Empty:
            pass

        self.root.after(100, self._poll_output)

    def _animate_orb(self):
        self.frame_number += 1
        self.canvas.delete("orb")

        width = max(self.canvas.winfo_width(), 320)
        height = max(self.canvas.winfo_height(), 280)
        cx = width / 2
        cy = height / 2

        status = self.status_label.cget("text")
        if "SPEAKING" in status:
            color = "#B9A6FF"
        elif "LISTENING" in status or "STANDBY" in status:
            color = "#54F0BD"
        elif "OFFLINE" in status:
            color = "#FF8090"
        else:
            color = CYAN

        pulse = math.sin(self.frame_number * 0.12)

        for index in range(4):
            radius = 48 + index * 20 + pulse * (index + 1) * 2
            self.canvas.create_oval(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                outline=color,
                width=2 if index == 0 else 1,
                tags="orb"
            )

        self.canvas.create_oval(
            cx - 43, cy - 43, cx + 43, cy + 43,
            fill="#101F35",
            outline=color,
            width=2,
            tags="orb"
        )

        self.canvas.create_text(
            cx, cy - 7,
            text="J",
            font=("Segoe UI", 38, "bold"),
            fill="white",
            tags="orb"
        )

        self.canvas.create_text(
            cx, cy + 43,
            text="OLLAMA  •  AI CORE",
            font=("Consolas", 9),
            fill=color,
            tags="orb"
        )

        self.root.after(80, self._animate_orb)

    def stop_jarvis(self):
        if self.process is not None and self.process.poll() is None:
            self.set_status("STOPPING")
            self.add_log("SYSTEM", "Stopping JARVIS...")
            self.process.terminate()
        else:
            self.set_status("OFFLINE")

    def close(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
        self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    app = JarvisDashboard(window)
    window.mainloop()
