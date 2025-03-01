import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from PIL import Image, ImageTk
import os
import subprocess
from datetime import datetime
from tkcalendar import DateEntry
import csv

class Achievement:
    def __init__(self, title, description, condition_type, condition_value):
        self.title = title
        self.description = description
        self.condition_type = condition_type
        self.condition_value = condition_value
        self.unlocked = False
        self.unlock_date = None

class PfandCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Österreichischer Pfandrechner")
        
        self.PRICES = {
            "Flaschen": 0.25,
            "Bierflasche": 0.20,
            "Kasten": 1.25,
            "Dose": 0.25,
            "Plastikflasche": 0.25
        }
        self.products = ["Flaschen", "Bierflasche", "Kasten", "Dose", "Plastikflasche"]
        self.quantities = {}
        self.images = {}
        self.deposit_history = self.load_deposit_history()
        
        self.achievements = self.initialize_achievements()
        self.load_achievements()
        
        if not os.path.exists('images'):
            os.makedirs('images')
            
        self.create_menu()
        self.load_quantities()
        self.create_widgets()
        
        self.achievement_image = self.load_achievement_image()

    def load_image(self, product_name):
        try:
            # Use Flaschen icon for Bierflasche
            if product_name == "Bierflasche":
                product_name = "Flaschen"
                
            image_path = f"images/{product_name.lower()}.png"
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize((100, 100), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
            else:
                return None
        except Exception as e:
            print(f"Error loading {image_path}: {e}")
            return None
    
    def load_achievement_image(self):
        try:
            image_path = "images/auszeichnung.png"
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize((50, 50), Image.Resampling.LANCZOS)
                # Store both normal and gray versions
                self.achievement_image = ImageTk.PhotoImage(image)
                # Create grayscale version while preserving transparency
                gray_image = Image.new('RGBA', image.size)
                for x in range(image.width):
                    for y in range(image.height):
                        r, g, b, a = image.getpixel((x, y))
                        # Convert to grayscale while preserving alpha
                        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                        # Make it lighter
                        gray = min(255, gray + 100)
                        gray_image.putpixel((x, y), (gray, gray, gray, a))
                self.achievement_image_gray = ImageTk.PhotoImage(gray_image)
                return self.achievement_image
            return None
        except Exception as e:
            print(f"Error loading achievement image: {e}")
            return None

    def initialize_achievements(self):
        return {
            "each_100": Achievement("Krass, Weiter So!", "Du hast bis jetzt 100 von jedem Element gesammelt!", "each_element", 100),
            "each_500": Achievement("Adlersson wäre neidisch!", "Adlersson wäre neidisch auf dich! Du hast 500 von jedem Element gesammelt!", "each_element", 500),
            "each_1000": Achievement("Arbeitslos I", "Arbeitsamt hat angerufen! Du hast 1000 von jedem Element gesammelt!", "each_element", 1000),
            "total_2000": Achievement("Arbeitslos II", "Das Arbeitsamt hat angst vor dir! Du hast 2000 totale Elemente gesammelt!", "total_elements", 2000),
            "total_3000": Achievement("Arbeitslos III", "Drachenlord hat angst vor dir! Du hast mehr wie 3000 Elemente gesammelt!", "total_elements", 3000),
            "total_over_3000": Achievement("Krankhafte Sucht!", "Du hast echt einen Vogel! Pfandangel #1! Du hast >3000 gesammelt!", "total_elements", 3001),
            "first_deposit": Achievement("Depositer!", "Guter Anfang!", "deposits", 1),
            "deposits_10": Achievement("Depositer I", "Cool, Weiter So!", "deposits", 10),
            "deposits_50": Achievement("Depositer II", "WoW, Echt viele Abgaben!", "deposits", 50),
            "deposits_100": Achievement("Depositer III", "Du bist der Meister der Abgaben!", "deposits", 100),
            "deposits_150": Achievement("Meister Depositer", "Der Pfandautomat hat Angst vor dir, so viel wie du Abgegeben hast müsstest du eine Villa besitzen!", "deposits", 150)
        }

    def load_achievements(self):
        try:
            with open('achievements.json', 'r') as f:
                data = json.load(f)
                for key, achievement_data in data.items():
                    if key in self.achievements:
                        self.achievements[key].unlocked = achievement_data['unlocked']
                        self.achievements[key].unlock_date = achievement_data['unlock_date']
        except FileNotFoundError:
            pass

    def save_achievements(self):
        data = {
            key: {
                'unlocked': achievement.unlocked,
                'unlock_date': achievement.unlock_date
            }
            for key, achievement in self.achievements.items()
        }
        with open('achievements.json', 'w') as f:
            json.dump(data, f)

    def check_achievements(self):
        total_elements = sum(self.deposit_history[-1]['quantities'].values()) if self.deposit_history else 0
        all_time_total = sum(sum(d['quantities'].values()) for d in self.deposit_history)
        deposits_count = len(self.deposit_history)
        
        for achievement in ["each_100", "each_500", "each_1000"]:
            if not self.achievements[achievement].unlocked:
                if all(self.deposit_history[-1]['quantities'][product] >= self.achievements[achievement].condition_value 
                      for product in self.products):
                    self.unlock_achievement(achievement)

        for achievement in ["total_2000", "total_3000", "total_over_3000"]:
            if not self.achievements[achievement].unlocked and all_time_total >= self.achievements[achievement].condition_value:
                self.unlock_achievement(achievement)

        deposit_achievements = {
            1: "first_deposit",
            10: "deposits_10",
            50: "deposits_50",
            100: "deposits_100",
            150: "deposits_150"
        }
        
        for count, achievement_key in deposit_achievements.items():
            if not self.achievements[achievement_key].unlocked and deposits_count >= count:
                self.unlock_achievement(achievement_key)

    def unlock_achievement(self, achievement_key):
        achievement = self.achievements[achievement_key]
        if not achievement.unlocked:
            achievement.unlocked = True
            achievement.unlock_date = datetime.now().strftime("%d.%m.%Y")
            self.save_achievements()
            messagebox.showinfo("Auszeichnung freigeschaltet!", 
                              f"Neue Auszeichnung: {achievement.title}\n\n{achievement.description}")

    def show_achievements(self):
        achievements_window = tk.Toplevel(self.root)
        achievements_window.title("Auszeichnungen")
        achievements_window.geometry("800x600")

        notebook = ttk.Notebook(achievements_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        all_frame = ttk.Frame(notebook)
        notebook.add(all_frame, text="Alle Auszeichnungen")

        unlocked_frame = ttk.Frame(notebook)
        notebook.add(unlocked_frame, text="Freigeschaltete")

        self._create_achievements_view(all_frame, show_all=True)
        self._create_achievements_view(unlocked_frame, show_all=False)

    def _create_achievements_view(self, parent_frame, show_all=True):
        canvas = tk.Canvas(parent_frame)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(widget):
            widget.bind('<MouseWheel>', _on_mousewheel)
            for child in widget.winfo_children():
                _bind_mousewheel(child)

        canvas.bind('<MouseWheel>', _on_mousewheel)
        _bind_mousewheel(scrollable_frame)

        sammeln_achievements = {
            "each_100": self.achievements["each_100"],
            "each_500": self.achievements["each_500"],
            "each_1000": self.achievements["each_1000"],
            "total_2000": self.achievements["total_2000"],
            "total_3000": self.achievements["total_3000"],
            "total_over_3000": self.achievements["total_over_3000"]
        }

        abgeben_achievements = {
            "first_deposit": self.achievements["first_deposit"],
            "deposits_10": self.achievements["deposits_10"],
            "deposits_50": self.achievements["deposits_50"],
            "deposits_100": self.achievements["deposits_100"],
            "deposits_150": self.achievements["deposits_150"]
        }

        row = 0

        def add_group_header(title):
            nonlocal row
            header_frame = ttk.Frame(scrollable_frame)
            header_frame.grid(row=row, column=0, sticky='ew', padx=5, pady=(15, 5))
            
            header_label = ttk.Label(header_frame, text=title, 
                                   font=('TkDefaultFont', 12, 'bold'))
            header_label.pack(anchor='w')
            
            separator = ttk.Separator(scrollable_frame, orient='horizontal')
            row += 1
            separator.grid(row=row, column=0, sticky='ew', pady=2)
            row += 1

        def add_achievement(key, achievement):
            nonlocal row
            if not show_all and not achievement.unlocked:
                return

            frame = ttk.Frame(scrollable_frame)
            frame.grid(row=row, column=0, sticky='ew', padx=5, pady=5)

            if self.achievement_image:
                if achievement.unlocked:
                    image_label = ttk.Label(frame, image=self.achievement_image)
                else:
                    image_label = ttk.Label(frame, image=self.achievement_image_gray)
                image_label.grid(row=0, column=0, rowspan=2, padx=(5, 10), pady=5)

            content_frame = ttk.Frame(frame)
            content_frame.grid(row=0, column=1, sticky='nsew', pady=5)

            title_label = ttk.Label(content_frame, text=achievement.title, 
                                  font=('TkDefaultFont', 10, 'bold'))
            title_label.grid(row=0, column=0, sticky='w')

            if achievement.unlocked:
                date_label = ttk.Label(content_frame, 
                                     text=f"Freigeschaltet am: {achievement.unlock_date}",
                                     font=('TkDefaultFont', 8))
                date_label.grid(row=0, column=1, padx=(20, 0))

            desc_label = ttk.Label(content_frame, text=achievement.description, 
                                 wraplength=600)
            desc_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(2, 0))

            content_frame.grid_columnconfigure(0, weight=1)
            content_frame.grid_columnconfigure(1, weight=0)

            separator = ttk.Separator(scrollable_frame, orient='horizontal')
            row += 1
            separator.grid(row=row, column=0, sticky='ew', pady=5)
            row += 1

            _bind_mousewheel(frame)

        add_group_header("Sammeln")
        for key, achievement in sammeln_achievements.items():
            add_achievement(key, achievement)

        add_group_header("Abgeben")
        for key, achievement in abgeben_achievements.items():
            add_achievement(key, achievement)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_menu(self):
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="Speichern", command=self.save_quantities, accelerator="Strg+S")
        file_menu.add_command(label="Ordner öffnen", command=self.open_file_location, accelerator="Strg+O")
        file_menu.add_command(label="Speicherdatei löschen", command=self.remove_save_file, accelerator="Strg+Shift+F1")
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit, accelerator="Strg+Q")

        deposit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Pfand", menu=deposit_menu)
        deposit_menu.add_command(label="Pfand Abgeben", command=self.quick_deposit, accelerator="Strg+D")
        deposit_menu.add_command(label="Abgabe Historie", command=self.show_deposit_history, accelerator="Strg+H")
        deposit_menu.add_separator()
        deposit_menu.add_command(label="Historie Exportieren (CSV)", command=self.export_history_csv, accelerator="Strg+E")
        deposit_menu.add_command(label="Historie Löschen", command=self.clear_deposit_history, accelerator="Strg+Shift+F2")

        achievements_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Auszeichnungen", menu=achievements_menu)
        achievements_menu.add_command(label="Auszeichnungen anzeigen", command=self.show_achievements, accelerator="Strg+F6")
        achievements_menu.add_command(label="Auszeichnungen löschen", command=self.delete_achievements, accelerator="Strg+F7")

        self.root.bind('<Control-s>', lambda e: self.save_quantities())
        self.root.bind('<Control-o>', lambda e: self.open_file_location())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-d>', lambda e: self.quick_deposit())
        self.root.bind('<Control-h>', lambda e: self.show_deposit_history())
        self.root.bind('<Control-e>', lambda e: self.export_history_csv())
        self.root.bind('<Control-F1>', lambda e: self.handle_shift_f1(e))
        self.root.bind('<Control-F2>', lambda e: self.handle_shift_f2(e))
        self.root.bind('<Control-F6>', lambda e: self.show_achievements())
        self.root.bind('<Control-F7>', lambda e: self.delete_achievements())

    def open_file_location(self):
        current_dir = os.getcwd()
        if os.name == 'nt':  # Windows
            os.startfile(current_dir)
        else:  # Linux/Mac
            try:
                subprocess.run(['xdg-open', current_dir])
            except:
                subprocess.run(['open', current_dir])

    def remove_save_file(self):
        if os.path.exists('quantities.json'):
            if messagebox.askyesno("Löschen bestätigen", "Sind Sie sicher, dass Sie die Speicherdatei löschen möchten?"):
                try:
                    os.remove('quantities.json')
                    messagebox.showinfo("Erfolg", "Speicherdatei wurde erfolgreich gelöscht!")
                    self.quantities = {product: 0 for product in self.products}
                    self.update_total()
                    for widget in self.root.winfo_children():
                        if isinstance(widget, ttk.Frame):
                            for child in widget.winfo_children():
                                if isinstance(child, ttk.Frame):
                                    for grandchild in child.winfo_children():
                                        if isinstance(grandchild, ttk.Spinbox):
                                            grandchild.set("0")
                except Exception as e:
                    messagebox.showerror("Fehler", f"Datei konnte nicht gelöscht werden: {str(e)}")
        else:
            messagebox.showinfo("Info", "Keine Speicherdatei vorhanden.")

    def load_quantities(self):
        try:
            with open('quantities.json', 'r') as f:
                self.quantities = json.load(f)
        except FileNotFoundError:
            self.quantities = {product: 0 for product in self.products}
    
    def save_quantities(self):
        with open('quantities.json', 'w') as f:
            json.dump(self.quantities, f)
        messagebox.showinfo("Erfolg", "Mengen wurden erfolgreich gespeichert!")
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        for i, product in enumerate(self.products):
            frame = ttk.Frame(main_frame)
            frame.grid(row=0, column=i, padx=10, pady=5)
            
            image = self.load_image(product)
            if image:
                self.images[product] = image  
                label = ttk.Label(frame, image=self.images[product])
                label.grid(row=0, column=0, pady=5)
            else:
                canvas = tk.Canvas(frame, width=100, height=100, bg='lightgray')
                canvas.grid(row=0, column=0, pady=5)
                canvas.create_text(50, 50, text=f"Kein {product}\nBild gefunden")
            
            ttk.Label(frame, text=product).grid(row=1, column=0, pady=2)
            ttk.Label(frame, text=f"€{self.PRICES[product]:.2f}").grid(row=2, column=0, pady=2)
            
            quantity_var = tk.StringVar(value=str(self.quantities.get(product, 0)))
            spinbox = ttk.Spinbox(
                frame,
                from_=0,
                to=100,
                width=5,
                textvariable=quantity_var,
                command=lambda p=product, v=quantity_var: self.update_quantity(p, v)
            )
            spinbox.grid(row=3, column=0, pady=5)
            
            spinbox.bind('<Return>', lambda event, p=product, v=quantity_var: self.update_quantity(p, v))
            spinbox.bind('<FocusOut>', lambda event, p=product, v=quantity_var: self.update_quantity(p, v))
        
        self.total_label = ttk.Label(main_frame, text="Gesamt: €0.00", font=('TkDefaultFont', 10, 'bold'))
        self.total_label.grid(row=1, column=0, columnspan=len(self.products), pady=10)
        
        self.update_total()
    
    def update_quantity(self, product, var, event=None):
        try:
            quantity = int(var.get())
            self.quantities[product] = quantity
            self.update_total()
        except ValueError:
            var.set(str(self.quantities.get(product, 0)))
    
    def update_total(self):
        total = sum(self.quantities[product] * self.PRICES[product] for product in self.products)
        self.total_label.config(text=f"Gesamt: €{total:.2f}")

    def load_deposit_history(self):
        try:
            with open('deposit_history.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_deposit_history(self):
        with open('deposit_history.json', 'w') as f:
            json.dump(self.deposit_history, f)

    def show_deposit_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Pfand Abgabe Historie")
        history_window.geometry("700x400")

        main_frame = ttk.Frame(history_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree = ttk.Treeview(main_frame, columns=('Datum', 'Flaschen', 'Bierflasche', 'Kasten', 'Dose', 'Plastikflasche', 'Gesamt'), show='headings')
        
        tree.heading('Datum', text='Datum', anchor='center')
        tree.heading('Flaschen', text='Flaschen', anchor='center')
        tree.heading('Bierflasche', text='Bierflasche', anchor='center')
        tree.heading('Kasten', text='Kasten', anchor='center')
        tree.heading('Dose', text='Dose', anchor='center')
        tree.heading('Plastikflasche', text='Plastikflasche', anchor='center')
        tree.heading('Gesamt', text='Gesamt (€)', anchor='center')

        tree.column('Datum', width=100, anchor='center')
        tree.column('Flaschen', width=70, anchor='center')
        tree.column('Bierflasche', width=70, anchor='center')
        tree.column('Kasten', width=70, anchor='center')
        tree.column('Dose', width=70, anchor='center')
        tree.column('Plastikflasche', width=100, anchor='center')
        tree.column('Gesamt', width=80, anchor='e')

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        total_flaschen = sum(deposit['quantities']['Flaschen'] for deposit in self.deposit_history)
        total_bierflasche = sum(deposit['quantities'].get('Bierflasche', 0) for deposit in self.deposit_history)
        total_kasten = sum(deposit['quantities']['Kasten'] for deposit in self.deposit_history)
        total_dose = sum(deposit['quantities']['Dose'] for deposit in self.deposit_history)
        total_plastik = sum(deposit['quantities']['Plastikflasche'] for deposit in self.deposit_history)
        total_amount = sum(deposit['total'] for deposit in self.deposit_history)

        for deposit in self.deposit_history:
            tree.insert('', tk.END, values=(
                deposit['date'],
                deposit['quantities']['Flaschen'],
                deposit['quantities'].get('Bierflasche', 0),
                deposit['quantities']['Kasten'],
                deposit['quantities']['Dose'],
                deposit['quantities']['Plastikflasche'],
                f"{deposit['total']:.2f}"
            ))

        totals_frame = ttk.Frame(main_frame)
        totals_frame.grid(row=1, column=0, sticky='ew', pady=(5, 0))

        totals_frame.grid_columnconfigure(0, minsize=100)  # Datum
        totals_frame.grid_columnconfigure(1, minsize=70)   # Flaschen
        totals_frame.grid_columnconfigure(2, minsize=70)   # Bierflasche
        totals_frame.grid_columnconfigure(3, minsize=70)   # Kasten
        totals_frame.grid_columnconfigure(4, minsize=70)   # Dose
        totals_frame.grid_columnconfigure(5, minsize=100)  # Plastikflasche
        totals_frame.grid_columnconfigure(6, minsize=80)   # Gesamt

        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=2, column=0, sticky='ew', pady=2)

        bold_font = ('TkDefaultFont', 9, 'bold')
        ttk.Label(totals_frame, text="Gesamt:", font=bold_font).grid(row=0, column=0, sticky='w', padx=5)
        ttk.Label(totals_frame, text=str(total_flaschen), font=bold_font).grid(row=0, column=1, sticky='n', padx=5)
        ttk.Label(totals_frame, text=str(total_bierflasche), font=bold_font).grid(row=0, column=2, sticky='n', padx=5)
        ttk.Label(totals_frame, text=str(total_kasten), font=bold_font).grid(row=0, column=3, sticky='n', padx=5)
        ttk.Label(totals_frame, text=str(total_dose), font=bold_font).grid(row=0, column=4, sticky='n', padx=5)
        ttk.Label(totals_frame, text=str(total_plastik), font=bold_font).grid(row=0, column=5, sticky='n', padx=5)
        ttk.Label(totals_frame, text=f"€{total_amount:.2f}", font=bold_font).grid(row=0, column=6, sticky='e', padx=5)

    def make_deposit(self):
        deposit_dialog = tk.Toplevel(self.root)
        deposit_dialog.title("Pfand Abgeben")
        deposit_dialog.geometry("300x150")
        deposit_dialog.transient(self.root)
        deposit_dialog.grab_set()

        ttk.Label(deposit_dialog, text="Abgabe Datum:").pack(pady=5)
        date_picker = DateEntry(deposit_dialog, width=12, background='darkblue',
                              foreground='white', borderwidth=2, locale='de_DE')
        date_picker.pack(pady=5)

        def confirm_deposit():
            date = date_picker.get_date().strftime("%d.%m.%Y")
            current_total = sum(self.quantities[product] * self.PRICES[product] 
                              for product in self.products)
            
            deposit_record = {
                'date': date,
                'quantities': dict(self.quantities),
                'total': current_total
            }
            self.deposit_history.append(deposit_record)
            self.save_deposit_history()

            self.quantities = {product: 0 for product in self.products}
            self.save_quantities()
            self.update_total()

            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Frame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, ttk.Spinbox):
                                    grandchild.set("0")

            messagebox.showinfo("Erfolg", "Pfand wurde erfolgreich abgegeben!")
            deposit_dialog.destroy()

        button_frame = ttk.Frame(deposit_dialog)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Abgeben", command=confirm_deposit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Abbrechen", command=deposit_dialog.destroy).pack(side=tk.LEFT, padx=5)

    def quick_deposit(self):
        if sum(self.quantities.values()) == 0:
            messagebox.showinfo("Info", "Keine Mengen zum Abgeben vorhanden.")
            return

        if messagebox.askyesno("Pfand Abgeben", "Möchten Sie den Pfand mit dem heutigen Datum abgeben?"):
            current_date = datetime.now().strftime("%d.%m.%Y")
            current_total = sum(self.quantities[product] * self.PRICES[product] 
                            for product in self.products)
            
            deposit_record = {
                'date': current_date,
                'quantities': dict(self.quantities),
                'total': current_total
            }
            self.deposit_history.append(deposit_record)
            self.save_deposit_history()
            
            self.check_achievements()

            self.quantities = {product: 0 for product in self.products}
            self.save_quantities()
            self.update_total()

            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Frame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, ttk.Spinbox):
                                    grandchild.set("0")

            messagebox.showinfo("Erfolg", "Pfand wurde erfolgreich abgegeben!")
        else:
            self.make_deposit()

    def export_history_csv(self):
        if not self.deposit_history:
            messagebox.showinfo("Info", "Keine Historie zum Exportieren vorhanden.")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Dateien", "*.csv")],
                initialfile="pfand_historie.csv"
            )
            
            if not file_path:
                return

            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                writer.writerow(['Datum', 'Flaschen', 'Bierflasche', 'Kasten', 'Dose', 'Plastikflasche', 'Gesamt (€)'])
                
                for deposit in self.deposit_history:
                    writer.writerow([
                        deposit['date'],
                        deposit['quantities']['Flaschen'],
                        deposit['quantities'].get('Bierflasche', 0),
                        deposit['quantities']['Kasten'],
                        deposit['quantities']['Dose'],
                        deposit['quantities']['Plastikflasche'],
                        f"{deposit['total']:.2f}"
                    ])
            
            messagebox.showinfo("Erfolg", "Historie wurde erfolgreich exportiert!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Exportieren: {str(e)}")

    def clear_deposit_history(self):
        if not self.deposit_history:
            messagebox.showinfo("Info", "Keine Historie zum Löschen vorhanden.")
            return

        if messagebox.askyesno("Löschen bestätigen", 
                              "Sind Sie sicher, dass Sie die gesamte Abgabe-Historie löschen möchten?\n"
                              "Dieser Vorgang kann nicht rückgängig gemacht werden!"):
            try:
                self.deposit_history = []
                if os.path.exists('deposit_history.json'):
                    os.remove('deposit_history.json')
                messagebox.showinfo("Erfolg", "Abgabe-Historie wurde erfolgreich gelöscht!")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen der Historie: {str(e)}")

    def handle_shift_f1(self, event):
        if event.state & 0x1:
            self.remove_save_file()

    def handle_shift_f2(self, event):
        if event.state & 0x1:
            self.clear_deposit_history()

    def delete_achievements(self):
        if not any(achievement.unlocked for achievement in self.achievements.values()):
            messagebox.showinfo("Info", "Keine Auszeichnungen zum Löschen vorhanden.")
            return

        if messagebox.askyesno("Löschen bestätigen", 
                              "Sind Sie sicher, dass Sie alle Auszeichnungen löschen möchten?\n"
                              "Dieser Vorgang kann nicht rückgängig gemacht werden!"):
            try:
                for achievement in self.achievements.values():
                    achievement.unlocked = False
                    achievement.unlock_date = None
                
                if os.path.exists('achievements.json'):
                    os.remove('achievements.json')
                messagebox.showinfo("Erfolg", "Alle Auszeichnungen wurden erfolgreich gelöscht!")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen der Auszeichnungen: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PfandCalculator(root)
    root.mainloop()
