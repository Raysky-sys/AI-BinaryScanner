import os
import queue
import threading
from datetime import datetime

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Imports the scanner from your existing file.
# If you rename Binary_scanner.py, update this import.
from Binary_scanner import scan_file


class BinaryScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Binary Scanner")
        self.geometry("1080x740")
        self.minsize(780, 540)

        self.targets = []
        self._target_keys = set()
        self._events = queue.Queue()
        self._scanning = False
        self._worker = None

        self.status_var = tk.StringVar(value="Ready")
        self.count_var = tk.StringVar(value="0 files selected")

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._process_events)

    def _build_ui(self):
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")

        outer = ttk.Frame(self, padding=10)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=2)
        outer.rowconfigure(3, weight=3)

        # ------------------------------------------------------------------
        # Target controls
        # ------------------------------------------------------------------
        tools = ttk.Frame(outer)
        tools.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.add_files_button = ttk.Button(
            tools, text="Add Files", command=self._add_files
        )
        self.add_folder_button = ttk.Button(
            tools, text="Add Folder", command=self._add_folder
        )
        self.remove_button = ttk.Button(
            tools, text="Remove Selected", command=self._remove_selected
        )
        self.clear_targets_button = ttk.Button(
            tools, text="Clear Files", command=self._clear_targets
        )

        self.recursive_var = tk.BooleanVar(value=True)
        self.recursive_check = ttk.Checkbutton(
            tools,
            text="Include subfolders",
            variable=self.recursive_var,
        )

        self.add_files_button.pack(side="left")
        self.add_folder_button.pack(side="left", padx=(6, 0))
        self.remove_button.pack(side="left", padx=(6, 0))
        self.clear_targets_button.pack(side="left", padx=(6, 0))
        self.recursive_check.pack(side="left", padx=(14, 0))

        ttk.Label(tools, textvariable=self.count_var).pack(side="right")

        self.target_buttons = [
            self.add_files_button,
            self.add_folder_button,
            self.remove_button,
            self.clear_targets_button,
        ]

        # ------------------------------------------------------------------
        # Selected files
        # ------------------------------------------------------------------
        files_frame = ttk.LabelFrame(
            outer, text="Files and folders to scan", padding=6
        )
        files_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(0, weight=1)

        list_frame = ttk.Frame(files_frame)
        list_frame.grid(row=0, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.target_list = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            exportselection=False,
            font=("Segoe UI", 9),
        )
        self.target_list.grid(row=0, column=0, sticky="nsew")

        vertical_scroll = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.target_list.yview,
        )
        vertical_scroll.grid(row=0, column=1, sticky="ns")

        horizontal_scroll = ttk.Scrollbar(
            list_frame,
            orient="horizontal",
            command=self.target_list.xview,
        )
        horizontal_scroll.grid(row=1, column=0, sticky="ew")

        self.target_list.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set,
        )

        # ------------------------------------------------------------------
        # Scan controls
        # ------------------------------------------------------------------
        actions = ttk.Frame(outer)
        actions.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        self.scan_button = ttk.Button(
            actions,
            text="Start Scan",
            command=self._start_scan,
        )
        self.export_log_button = ttk.Button(
            actions,
            text="Save Log",
            command=self._export_log,
        )
        self.clear_log_button = ttk.Button(
            actions,
            text="Clear Log",
            command=self._clear_log,
        )

        self.progress = ttk.Progressbar(
            actions,
            mode="determinate",
            length=260,
        )

        self.scan_button.pack(side="left")
        self.export_log_button.pack(side="left", padx=(6, 0))
        self.clear_log_button.pack(side="left", padx=(6, 0))
        self.progress.pack(side="right", padx=(12, 0))

        # ------------------------------------------------------------------
        # Log
        # ------------------------------------------------------------------
        log_frame = ttk.LabelFrame(outer, text="Scan log", padding=6)
        log_frame.grid(row=3, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(
            log_frame,
            wrap="word",
            state="disabled",
            font=("Consolas", 9),
            background="#f7f7f7",
            foreground="#202020",
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")

        log_scroll = ttk.Scrollbar(
            log_frame,
            orient="vertical",
            command=self.log_text.yview,
        )
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.log_text.tag_configure(
            "match", foreground="#b00020"
        )
        self.log_text.tag_configure(
            "error", foreground="#9a6700"
        )

        status = ttk.Label(
            outer,
            textvariable=self.status_var,
            anchor="w",
        )
        status.grid(row=4, column=0, sticky="ew", pady=(8, 0))

    # ----------------------------------------------------------------------
    # File and folder selection
    # ----------------------------------------------------------------------
    def _register_paths(self, paths):
        added = 0

        for raw_path in paths:
            try:
                path = os.path.abspath(os.path.expanduser(raw_path))

                if not os.path.isfile(path):
                    continue

                # Prevent the same file from being added twice.
                key = os.path.normcase(path)
                if key in self._target_keys:
                    continue

                self._target_keys.add(key)
                self.targets.append(path)
                self.target_list.insert(tk.END, path)
                added += 1
            except (OSError, ValueError):
                continue

        self._update_count()
        return added

    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select one or more files",
            filetypes=[
                ("All files", "*.*"),
            ],
        )

        if not paths:
            return

        added = self._register_paths(paths)
        self._append_log(f"Added {added} file(s).")
        self.status_var.set(f"{added} new file(s) added.")

    def _add_folder(self):
        folder = filedialog.askdirectory(
            title="Select a folder to scan"
        )

        if not folder:
            return

        recursive = self.recursive_var.get()
        paths = []

        def on_walk_error(error):
            self._append_log(f"[!] Folder access error: {error}")

        for current_dir, directories, filenames in os.walk(
            folder,
            followlinks=False,
            onerror=on_walk_error,
        ):
            directories.sort()
            filenames.sort()

            if not recursive:
                directories[:] = []

            for filename in filenames:
                paths.append(os.path.join(current_dir, filename))

        added = self._register_paths(paths)

        self._append_log(
            f"Added folder: {folder} "
            f"({added} new file(s) from {len(paths)} file(s) found)."
        )
        self.status_var.set(
            f"Folder processed; {len(self.targets)} file(s) selected."
        )

    def _remove_selected(self):
        if self._scanning:
            return

        selected = sorted(
            self.target_list.curselection(),
            reverse=True,
        )

        for index in selected:
            path = self.targets[index]
            self._target_keys.discard(os.path.normcase(path))
            del self.targets[index]
            self.target_list.delete(index)

        self._update_count()
        self.status_var.set("Selected files removed.")

    def _clear_targets(self):
        if self._scanning:
            return

        self.targets.clear()
        self._target_keys.clear()
        self.target_list.delete(0, tk.END)
        self._update_count()
        self.status_var.set("File list cleared.")

    def _update_count(self):
        self.count_var.set(f"{len(self.targets):,} file(s) selected")

    # ----------------------------------------------------------------------
    # Scanning
    # ----------------------------------------------------------------------
    def _start_scan(self):
        if self._scanning:
            return

        if not self.targets:
            messagebox.showwarning(
                "No Files",
                "Add at least one file or folder before starting a scan.",
            )
            return

        self._clear_log()
        self._events = queue.Queue()

        files = list(self.targets)

        self._append_log("Binary Scanner")
        self._append_log(
            f"Started: {datetime.now():%Y-%m-%d %H:%M:%S}"
        )
        self._append_log(f"Files selected: {len(files)}")
        self._append_log("-" * 60)

        self._scanning = True
        self._set_scanning(True)
        self.progress.configure(maximum=len(files), value=0)
        self.status_var.set(f"Scanning 0 of {len(files)}...")

        self._worker = threading.Thread(
            target=self._scan_worker,
            args=(files,),
            daemon=True,
        )
        self._worker.start()

    def _scan_worker(self, files):
        total = len(files)
        flagged = []
        errors = 0

        for number, path in enumerate(files, start=1):
            self._events.put(
                ("log", f"\n[{number}/{total}] Scanning: {path}")
            )

            try:
                results = scan_file(path)
            except Exception as error:
                results = f"Error reading file: {error}"

            if isinstance(results, list):
                if results:
                    flagged.append(path)

                    self._events.put(
                        ("log", f"    [!] MATCH FOUND: {path}")
                    )
                    self._events.put(
                        (
                            "log",
                            f"    Detected markers: {', '.join(results)}",
                        )
                    )

                    # Special logic from the original scanner.
                    if len(results) == 1 and "cai" in results:
                        self._events.put(
                            (
                                "log",
                                "    NOTE: 'cai' is an Adobe marker and may be "
                                "present when an image was edited in Photoshop.",
                            )
                        )
                else:
                    self._events.put(
                        ("log", "    [OK] No configured markers found.")
                    )
            else:
                errors += 1
                self._events.put(
                    ("log", f"    [-] Skipping {path}: {results}")
                )

            self._events.put(("progress", number))

        self._events.put(("log", "\n--- Scan Complete ---"))
        self._events.put(
            (
                "log",
                f"Files flagged by marker matching: {len(flagged)}",
            )
        )
        self._events.put(
            (
                "log",
                f"Files skipped because of read errors: {errors}",
            )
        )

        if flagged:
            self._events.put(("log", "Flagged files:"))
            for path in flagged:
                self._events.put(("log", f'"{path}"'))

        self._events.put(
            (
                "log",
                "\n"
                + "=" * 60
                + "\n"
                + "NOTE: A marker match is not proof that a file was "
                + "AI-generated.\n"
                + "Markers such as 'adobe', 'cai', 'manifest', and 'c2pa' "
                + "may also occur in\n"
                + "legitimate images that were edited or contain content "
                + "credentials.\n"
                + "Use multiple markers and vendor-specific metadata "
                + "when evaluating results.\n"
                + "=" * 60,
            )
        )
        self._events.put(
            (
                "log",
                f"Finished: {datetime.now():%Y-%m-%d %H:%M:%S}",
            )
        )
        self._events.put(("done", (len(flagged), errors)))

    def _set_scanning(self, scanning):
        state = "disabled" if scanning else "normal"

        for button in self.target_buttons:
            button.configure(state=state)

        self.recursive_check.configure(state=state)
        self.scan_button.configure(state=state)
        self.clear_log_button.configure(state=state)

    # ----------------------------------------------------------------------
    # GUI event processing
    # ----------------------------------------------------------------------
    def _process_events(self):
        try:
            while True:
                event_type, payload = self._events.get_nowait()

                if event_type == "log":
                    self._append_log(payload)

                elif event_type == "progress":
                    self.progress["value"] = payload

                elif event_type == "done":
                    flagged_count, error_count = payload

                    self._scanning = False
                    self._set_scanning(False)
                    self.progress["value"] = self.progress["maximum"]

                    self.status_var.set(
                        f"Complete: {flagged_count} file(s) flagged, "
                        f"{error_count} error(s)."
                    )

        except queue.Empty:
            pass

        self.after(100, self._process_events)

    # ----------------------------------------------------------------------
    # Log handling
    # ----------------------------------------------------------------------
    def _append_log(self, text):
        text = str(text)

        if not text.strip():
            return

        text = text.rstrip("\n")

        self.log_text.configure(state="normal")
        start_index = self.log_text.index("end-1c")
        self.log_text.insert("end-1c", text + "\n")
        end_index = self.log_text.index("end-1c")

        if "[!] MATCH FOUND" in text:
            self.log_text.tag_add("match", start_index, end_index)
        elif text.lstrip().startswith("[-]") or "Error" in text:
            self.log_text.tag_add("error", start_index, end_index)

        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")

    def _export_log(self):
        content = self.log_text.get("1.0", "end-1c")

        if not content.strip():
            messagebox.showinfo(
                "Save Log",
                "There is no log content to save.",
            )
            return

        default_name = (
            f"binary_scan_"
            f"{datetime.now():%Y%m%d_%H%M%S}.txt"
        )

        filename = filedialog.asksaveasfilename(
            title="Save scan log",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )

        if not filename:
            return

        try:
            with open(
                filename,
                "w",
                encoding="utf-8",
                newline="",
            ) as output_file:
                output_file.write(content)

            messagebox.showinfo(
                "Log Saved",
                f"The scan log was saved to:\n\n{filename}",
            )
            self.status_var.set(f"Log saved to {filename}")

        except OSError as error:
            messagebox.showerror(
                "Save Error",
                f"Could not save the log:\n\n{error}",
            )

    def _on_close(self):
        if self._scanning:
            should_close = messagebox.askyesno(
                "Scan in progress",
                "A scan is still running. Close the application anyway?",
            )

            if not should_close:
                return

        self.destroy()


if __name__ == "__main__":
    app = BinaryScannerApp()
    app.mainloop()
