import tkinter as tk
from tkinter import ttk, messagebox
import os
import requests
import hashlib
from zipfile import ZipFile
import io
import shutil
import tempfile

GITHUB_REPO_ZIP = "https://github.com/ZockerKatze/pfand/archive/refs/heads/main.zip"

IGNORED_FILES = {"key.py"}

class GitHubUpdater(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("PfandUpdater")
        self.geometry("700x550")
        self.resizable(False, False)
        self.configure(bg="#f0f2f5")

        self.local_dir = os.getcwd()
        self.file_differences = []
        self.structure = {}
        self.current_view = "root"

        self._build_ui()
        self.check_for_updates()

    def _build_ui(self):
        header = tk.Label(self, text="PfandUpdater", font=("Helvetica", 18, "bold"), bg="#f0f2f5")
        header.pack(pady=(20, 5))

        self.status_label = tk.Label(self, text="Suche nach Updates...", font=("Helvetica", 12), bg="#f0f2f5")
        self.status_label.pack(pady=(0, 10))

        self.frame = ttk.Frame(self)
        self.frame.pack(expand=True, fill="both", padx=20, pady=10)

        self.canvas = tk.Canvas(self.frame, bg="white")
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.back_button = ttk.Button(self, text="Zurück", command=self.show_root_view)
        self.back_button.pack(pady=(0, 5))
        self.back_button.pack_forget()

        self.update_button = ttk.Button(self, text="Dateien aktualisieren (Updaten)", command=self.perform_update, state='disabled')
        self.update_button.pack(pady=10)

    def show_root_view(self):
        self.current_view = "root"
        self.back_button.pack_forget()
        self.display_structure(self.structure)

    def display_structure(self, struct, parent_path=""):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for name, content in struct.items():
            full_path = os.path.join(parent_path, name)
            if isinstance(content, dict):
                btn = ttk.Button(self.scrollable_frame, text=f"📁 {name}", command=lambda p=full_path: self.open_folder(p))
            else:
                btn = ttk.Button(self.scrollable_frame, text=f"📄 {name}")
            btn.pack(fill="x", padx=10, pady=5)

    def open_folder(self, folder_path):
        self.current_view = folder_path
        self.back_button.pack()
        parts = folder_path.split(os.sep)
        subtree = self.structure
        for part in parts:
            subtree = subtree.get(part, {})
        self.display_structure(subtree, folder_path)

    def check_for_updates(self):
        try:
            response = requests.get(GITHUB_REPO_ZIP)
            with ZipFile(io.BytesIO(response.content)) as zip_file:
                temp_dir = tempfile.mkdtemp()
                zip_file.extractall(temp_dir)
                extracted_path = os.path.join(temp_dir, os.listdir(temp_dir)[0])
                self.file_differences = self.compare_directories(extracted_path, self.local_dir)

                if self.file_differences:
                    self.status_label.config(text="⚠️ Updates verfügbar", fg="red")
                    self.structure = self.build_structure(self.file_differences)
                    self.display_structure(self.structure)
                    self.update_button.config(state='normal')
                else:
                    self.status_label.config(text="✅ Alle Dateien sind aktuell", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Fehler: {e}", fg="red")

    def compare_directories(self, src_dir, dest_dir):
        differences = []
        for root, _, files in os.walk(src_dir):
            for file in files:
                if file in IGNORED_FILES:
                    continue
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, src_dir)
                dest_path = os.path.join(dest_dir, rel_path)

                if not os.path.exists(dest_path) or not self.files_match(src_path, dest_path):
                    differences.append(rel_path)
        return differences

    def build_structure(self, file_paths):
        tree = {}
        for path in file_paths:
            parts = path.split(os.sep)
            d = tree
            for part in parts[:-1]:
                d = d.setdefault(part, {})
            d[parts[-1]] = path
        return tree

    def files_match(self, file1, file2):
        return self.hash_file(file1) == self.hash_file(file2)

    def hash_file(self, filepath):
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def perform_update(self):
        try:
            response = requests.get(GITHUB_REPO_ZIP)
            with ZipFile(io.BytesIO(response.content)) as zip_file:
                temp_dir = tempfile.mkdtemp()
                zip_file.extractall(temp_dir)
                extracted_path = os.path.join(temp_dir, os.listdir(temp_dir)[0])

                for rel_path in self.file_differences:
                    src_path = os.path.join(extracted_path, rel_path)
                    dest_path = os.path.join(self.local_dir, rel_path)

                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)

                messagebox.showinfo("Aktualisierung abgeschlossen", "Dateien wurden erfolgreich aktualisiert.")
                self.destroy()
        except Exception as e:
            messagebox.showerror("Aktualisierung fehlgeschlagen", str(e))

def open_updater():
    root = tk.Tk()
    root.withdraw()
    updater = GitHubUpdater(root)
    updater.mainloop()

