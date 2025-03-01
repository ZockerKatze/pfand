import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import sys
import os
import threading
import queue
import datetime
from clean import clean
from build import main as build_main

class RedirectText:
    def __init__(self, text_widget, queue):
        self.text_widget = text_widget
        self.queue = queue

    def write(self, string):
        self.queue.put(string)

    def flush(self):
        pass

class ModernButton(ttk.Button):
    """Custom styled button with hover effect"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, e):
        self['style'] = 'Hover.Action.TButton'

    def on_leave(self, e):
        self['style'] = 'Action.TButton'

class BuildUtilGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pfandrechner Build Utility")
        
        # Set minimum window size
        self.root.minsize(900, 700)
        
        # Configure theme and styles
        self.setup_styles()
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create title frame
        self.create_title_frame()
        
        # Create buttons frame
        self.create_buttons_frame()
        
        # Create log frame with toolbar
        self.create_log_frame()
        
        # Status bar
        self.create_status_bar()
        
        # Queue for log messages
        self.log_queue = queue.Queue()
        self.root.after(100, self.check_queue)
        
        # Store original stdout
        self.original_stdout = sys.stdout
        
        # Center window on screen
        self.center_window()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Track current theme
        self.is_dark_mode = False

    def setup_styles(self):
        style = ttk.Style()
        
        # Configure professional color scheme
        self.colors = {
            'light': {
                'bg': '#ffffff',
                'fg': '#2c3e50',
                'button': '#3498db',
                'button_hover': '#2980b9',
                'success': '#2ecc71',
                'error': '#e74c3c',
                'progress': '#3498db',
                'accent': '#34495e',
                'border': '#bdc3c7',
                'log_bg': '#f8f9fa',
                'log_fg': '#2c3e50',
                'tooltip_bg': '#34495e',
                'tooltip_fg': '#ecf0f1'
            },
            'dark': {
                'bg': '#2c3e50',
                'fg': '#ecf0f1',
                'button': '#3498db',
                'button_hover': '#2980b9',
                'success': '#27ae60',
                'error': '#c0392b',
                'progress': '#3498db',
                'accent': '#95a5a6',
                'border': '#34495e',
                'log_bg': '#34495e',
                'log_fg': '#ecf0f1',
                'tooltip_bg': '#ecf0f1',
                'tooltip_fg': '#2c3e50'
            }
        }
        
        # Configure button styles
        style.configure(
            'Action.TButton',
            padding=15,
            font=('Segoe UI', 10),
            background=self.colors['light']['button'],
            foreground=self.colors['light']['fg']
        )
        
        style.configure(
            'Hover.Action.TButton',
            background=self.colors['light']['button_hover'],
            foreground=self.colors['light']['fg']
        )
        
        # Configure frame styles
        style.configure(
            'TFrame',
            background=self.colors['light']['bg']
        )
        
        style.configure(
            'TLabelframe',
            background=self.colors['light']['bg'],
            foreground=self.colors['light']['fg']
        )
        
        style.configure(
            'TLabelframe.Label',
            font=('Segoe UI', 10, 'bold'),
            background=self.colors['light']['bg'],
            foreground=self.colors['light']['fg']
        )
        
        # Configure label styles
        style.configure(
            'Title.TLabel',
            font=('Segoe UI', 24, 'bold'),
            padding=10,
            background=self.colors['light']['bg'],
            foreground=self.colors['light']['accent']
        )
        
        style.configure(
            'Subtitle.TLabel',
            font=('Segoe UI', 11),
            padding=(0, 0, 0, 20),
            background=self.colors['light']['bg'],
            foreground=self.colors['light']['fg']
        )

    def create_title_frame(self):
        title_frame = ttk.Frame(self.main_frame)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        title = ttk.Label(
            title_frame,
            text="Pfandrechner Builder",
            style='Title.TLabel'
        )
        title.grid(row=0, column=0, sticky="w")
        
        subtitle = ttk.Label(
            title_frame,
            text="Build and manage your Pfandrechner application",
            style='Subtitle.TLabel'
        )
        subtitle.grid(row=1, column=0, sticky="w")

    def create_buttons_frame(self):
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Main action buttons with improved tooltips
        self.clean_button = ModernButton(
            self.buttons_frame,
            text="🧹 Clean Repository",
            command=self.run_clean,
            style="Action.TButton"
        )
        self.clean_button.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(
            self.clean_button,
            "Clean build artifacts and temporary files\n(Ctrl+C)"
        )
        
        self.build_button = ModernButton(
            self.buttons_frame,
            text="🔨 Build Executable",
            command=self.run_build,
            style="Action.TButton"
        )
        self.build_button.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(
            self.build_button,
            "Build the executable\n(Ctrl+B)"
        )
        
        # Right-aligned utility buttons
        utils_frame = ttk.Frame(self.buttons_frame)
        utils_frame.pack(side=tk.RIGHT)
        
        # Save log button
        self.save_log_button = ModernButton(
            utils_frame,
            text="💾 Save Log",
            command=self.save_log,
            style="Action.TButton"
        )
        self.save_log_button.pack(side=tk.RIGHT, padx=5)
        self.create_tooltip(
            self.save_log_button,
            "Save log to file\n(Ctrl+S)"
        )
        
        # Clear log button
        self.clear_log_button = ModernButton(
            utils_frame,
            text="🗑️ Clear Log",
            command=self.clear_log,
            style="Action.TButton"
        )
        self.clear_log_button.pack(side=tk.RIGHT, padx=5)
        self.create_tooltip(
            self.clear_log_button,
            "Clear the log\n(Ctrl+L)"
        )
        
        # Theme toggle button
        self.theme_button = ModernButton(
            utils_frame,
            text="🌓 Toggle Theme",
            command=self.toggle_theme,
            style="Action.TButton"
        )
        self.theme_button.pack(side=tk.RIGHT, padx=5)
        self.create_tooltip(
            self.theme_button,
            "Switch between light and dark theme\n(Ctrl+T)"
        )
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.main_frame,
            mode='indeterminate',
            length=300
        )
        self.progress.grid(row=2, column=0, sticky="ew", pady=(0, 20))

    def create_log_frame(self):
        # Create main log frame
        self.log_frame = ttk.LabelFrame(
            self.main_frame,
            text="Build Log",
            padding="10"
        )
        self.log_frame.grid(row=3, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(3, weight=1)
        
        # Create toolbar
        toolbar = ttk.Frame(self.log_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Toolbar buttons
        self.clear_log_button = ModernButton(
            toolbar,
            text="🗑️ Clear Log",
            command=self.clear_log,
            style="Action.TButton"
        )
        self.clear_log_button.pack(side=tk.LEFT, padx=2)
        self.create_tooltip(self.clear_log_button, "Clear the log (Ctrl+L)")
        
        self.save_log_button = ModernButton(
            toolbar,
            text="💾 Save Log",
            command=self.save_log,
            style="Action.TButton"
        )
        self.save_log_button.pack(side=tk.LEFT, padx=2)
        self.create_tooltip(self.save_log_button, "Save log to file (Ctrl+S)")
        
        # Create log text widget
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Consolas', 10),
            background='#ffffff',
            foreground='#333333'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            padding=(10, 5)
        )
        self.status_bar.grid(row=4, column=0, sticky="ew", pady=(10, 0))

    def create_tooltip(self, widget, text):
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            
            # Calculate position
            x = event.x_root + 15
            y = event.y_root + 10
            
            # Create frame with border
            frame = ttk.Frame(
                tooltip,
                style='Tooltip.TFrame',
                padding=2
            )
            frame.pack(fill='both', expand=True)
            
            # Split shortcut from description if exists
            if '(' in text and ')' in text:
                desc, shortcut = text.rsplit('(', 1)
                shortcut = shortcut.rstrip(')')
                
                # Description label
                desc_label = ttk.Label(
                    frame,
                    text=desc.strip(),
                    style='Tooltip.TLabel',
                    padding=(8, 5, 8, 2)
                )
                desc_label.pack(anchor='w')
                
                # Shortcut label
                shortcut_label = ttk.Label(
                    frame,
                    text=shortcut,
                    style='TooltipShortcut.TLabel',
                    padding=(8, 2, 8, 5)
                )
                shortcut_label.pack(anchor='w')
            else:
                # Single label for tooltip without shortcut
                label = ttk.Label(
                    frame,
                    text=text,
                    style='Tooltip.TLabel',
                    padding=8
                )
                label.pack()
            
            # Position tooltip
            tooltip.wm_geometry(f"+{x}+{y}")
            
            # Configure tooltip styles
            style = ttk.Style()
            colors = self.colors['dark' if self.is_dark_mode else 'light']
            
            style.configure(
                'Tooltip.TFrame',
                background=colors['tooltip_bg'],
                borderwidth=1,
                relief='solid'
            )
            
            style.configure(
                'Tooltip.TLabel',
                background=colors['tooltip_bg'],
                foreground=colors['tooltip_fg'],
                font=('Segoe UI', 9)
            )
            
            style.configure(
                'TooltipShortcut.TLabel',
                background=colors['tooltip_bg'],
                foreground=colors['tooltip_fg'],
                font=('Segoe UI', 9, 'bold')
            )
            
            def hide_tooltip():
                tooltip.destroy()
            
            tooltip.after(2500, hide_tooltip)
            widget.tooltip = tooltip

        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def bind_shortcuts(self):
        self.root.bind('<Control-b>', lambda e: self.run_build())
        self.root.bind('<Control-c>', lambda e: self.run_clean())
        self.root.bind('<Control-l>', lambda e: self.clear_log())
        self.root.bind('<Control-s>', lambda e: self.save_log())
        self.root.bind('<Control-t>', lambda e: self.toggle_theme())

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        colors = self.colors['dark' if self.is_dark_mode else 'light']
        
        style = ttk.Style()
        
        # Update frame styles
        style.configure('TFrame', background=colors['bg'])
        style.configure('TLabelframe', background=colors['bg'])
        style.configure('TLabelframe.Label', background=colors['bg'], foreground=colors['fg'])
        
        # Update label styles
        style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        style.configure('Title.TLabel', background=colors['bg'], foreground=colors['accent'])
        style.configure('Subtitle.TLabel', background=colors['bg'], foreground=colors['fg'])
        
        # Update button styles
        style.configure('Action.TButton', background=colors['button'])
        style.configure('Hover.Action.TButton', background=colors['button_hover'])
        
        # Update log text
        self.log_text.configure(
            background=colors['log_bg'],
            foreground=colors['log_fg']
        )
        
        # Update status bar
        self.status_bar.configure(background=colors['bg'])
        
        self.status_var.set(f"Switched to {'dark' if self.is_dark_mode else 'light'} theme")

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("Log cleared")

    def save_log(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"build_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.status_var.set(f"Log saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {str(e)}")

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def check_queue(self):
        """Check for new log messages in the queue."""
        while True:
            try:
                msg = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, msg)
                self.log_text.see(tk.END)
                self.log_text.update_idletasks()
            except queue.Empty:
                break
        self.root.after(100, self.check_queue)

    def set_buttons_state(self, state):
        """Enable or disable buttons."""
        self.clean_button['state'] = state
        self.build_button['state'] = state

    def run_clean(self):
        """Run the clean operation in a separate thread."""
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("Cleaning repository...")
        self.set_buttons_state('disabled')
        self.progress.start(10)
        
        def clean_thread():
            sys.stdout = RedirectText(self.log_text, self.log_queue)
            try:
                clean()
                self.root.after(0, self.clean_complete)
            except Exception as e:
                self.root.after(0, self.operation_failed, "Clean", str(e))
            finally:
                sys.stdout = self.original_stdout

        threading.Thread(target=clean_thread, daemon=True).start()

    def run_build(self):
        """Run the build operation in a separate thread."""
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("Building executable...")
        self.set_buttons_state('disabled')
        self.progress.start(10)
        
        def build_thread():
            sys.stdout = RedirectText(self.log_text, self.log_queue)
            try:
                build_main()
                self.root.after(0, self.build_complete)
            except Exception as e:
                self.root.after(0, self.operation_failed, "Build", str(e))
            finally:
                sys.stdout = self.original_stdout

        threading.Thread(target=build_thread, daemon=True).start()

    def clean_complete(self):
        """Called when clean operation completes successfully."""
        self.progress.stop()
        self.set_buttons_state('normal')
        self.status_var.set("Repository cleaned successfully!")

    def build_complete(self):
        """Called when build operation completes successfully."""
        self.progress.stop()
        self.set_buttons_state('normal')
        self.status_var.set("Build completed successfully!")

    def operation_failed(self, operation, error):
        """Called when an operation fails."""
        self.progress.stop()
        self.set_buttons_state('normal')
        self.status_var.set(f"{operation} failed: {error}")
        self.log_queue.put(f"\nError: {error}\n")

def main():
    root = tk.Tk()
    app = BuildUtilGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 