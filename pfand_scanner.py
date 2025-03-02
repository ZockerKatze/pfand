import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
from datetime import datetime
import threading
import queue

class PfandScanner:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        
        # Create main frames
        self.camera_frame = ttk.Frame(window)
        self.camera_frame.pack(side="left", padx=10, pady=5)
        
        self.control_frame = ttk.Frame(window)
        self.control_frame.pack(side="left", padx=10, pady=5, fill="y")
        
        self.info_frame = ttk.Frame(window)
        self.info_frame.pack(side="right", padx=10, pady=5, fill="both", expand=True)
        
        # Create camera label
        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack()
        
        # Create focus control
        focus_frame = ttk.LabelFrame(self.control_frame, text="Camera Controls")
        focus_frame.pack(pady=5, padx=5, fill="x")
        
        ttk.Label(focus_frame, text="Focus:").pack(pady=2)
        self.focus_slider = ttk.Scale(focus_frame, from_=0, to=255, orient="horizontal")
        self.focus_slider.set(0)  # Start with autofocus
        self.focus_slider.pack(pady=2, padx=5, fill="x")
        
        self.autofocus_var = tk.BooleanVar(value=True)
        self.autofocus_check = ttk.Checkbutton(
            focus_frame, 
            text="Autofocus", 
            variable=self.autofocus_var,
            command=self.toggle_autofocus
        )
        self.autofocus_check.pack(pady=2)
        
        # Create image processing controls
        process_frame = ttk.LabelFrame(self.control_frame, text="Image Processing")
        process_frame.pack(pady=5, padx=5, fill="x")
        
        ttk.Label(process_frame, text="Brightness:").pack(pady=2)
        self.brightness_slider = ttk.Scale(process_frame, from_=0, to=100, orient="horizontal")
        self.brightness_slider.set(50)
        self.brightness_slider.pack(pady=2, padx=5, fill="x")
        
        ttk.Label(process_frame, text="Contrast:").pack(pady=2)
        self.contrast_slider = ttk.Scale(process_frame, from_=0, to=100, orient="horizontal")
        self.contrast_slider.set(50)
        self.contrast_slider.pack(pady=2, padx=5, fill="x")
        
        # Create table
        self.tree = ttk.Treeview(self.info_frame, columns=("Time", "Barcode", "Type", "Deposit"), show="headings")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Barcode", text="Barcode")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Deposit", text="Deposit (€)")
        
        # Configure column widths
        self.tree.column("Time", width=150)
        self.tree.column("Barcode", width=200)
        self.tree.column("Type", width=100)
        self.tree.column("Deposit", width=100)
        
        self.tree.pack(fill="both", expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.info_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(0)  # Use 0 for default camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Disable autofocus and set initial manual focus (C920 specific)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus
        self.cap.set(cv2.CAP_PROP_FOCUS, 0)      # Set focus to 0
        
        # Queue for thread-safe communication
        self.queue = queue.Queue()
        
        # Dictionary to store known Pfand values
        self.pfand_values = {
            "EINWEG": 0.25,  # Single-use bottles
            "MEHRWEG": 0.15,  # Reusable bottles
            "DOSE": 0.25,    # Cans
        }
        
        # Start video streaming
        self.process_video()
        
        # Set window close handler
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start processing the queue
        self.process_queue()

    def toggle_autofocus(self):
        if self.autofocus_var.get():
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            self.focus_slider.state(['disabled'])
        else:
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            self.focus_slider.state(['!disabled'])
            self.cap.set(cv2.CAP_PROP_FOCUS, self.focus_slider.get())

    def adjust_image(self, frame):
        # Get current slider values
        brightness = self.brightness_slider.get() / 50.0 - 1.0  # Convert to range -1 to 1
        contrast = self.contrast_slider.get() / 50.0  # Convert to range 0 to 2
        
        # Apply brightness and contrast adjustments
        adjusted = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness * 127)
        
        # Apply additional processing to help with barcode detection
        gray = cv2.cvtColor(adjusted, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return binary

    def process_video(self):
        ret, frame = self.cap.read()
        if ret:
            # Update focus if in manual mode
            if not self.autofocus_var.get():
                self.cap.set(cv2.CAP_PROP_FOCUS, self.focus_slider.get())
            
            # Process image for better barcode detection
            processed_frame = self.adjust_image(frame)
            
            # Detect barcodes on both original and processed frames
            barcodes = decode(processed_frame) or decode(frame)
            
            # Draw rectangle around detected barcodes
            for barcode in barcodes:
                points = barcode.polygon
                if len(points) == 4:
                    pts = [(p.x, p.y) for p in points]
                    cv2.polylines(frame, [cv2.convexHull(
                        cv2.UMat(cv2.Mat(pts))).get()], True, (0, 255, 0), 2)
                
                # Add barcode data to queue
                barcode_data = barcode.data.decode('utf-8')
                self.queue.put(barcode_data)
            
            # Convert frame for display
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
        
        # Schedule next frame processing
        self.window.after(10, self.process_video)

    def process_queue(self):
        try:
            while True:
                barcode_data = self.queue.get_nowait()
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Determine type and deposit value based on barcode
                if len(barcode_data) == 13:  # EAN-13
                    pfand_type = "EINWEG"
                elif len(barcode_data) == 8:  # EAN-8
                    pfand_type = "MEHRWEG"
                else:
                    pfand_type = "DOSE"
                
                deposit = self.pfand_values.get(pfand_type, 0.00)
                
                # Insert into table
                self.tree.insert("", 0, values=(current_time, barcode_data, 
                                              pfand_type, f"{deposit:.2f}"))
                
        except queue.Empty:
            pass
        finally:
            # Schedule next queue check
            self.window.after(100, self.process_queue)

    def on_closing(self):
        if self.cap.isOpened():
            self.cap.release()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PfandScanner(root, "Pfand Barcode Scanner")
    root.mainloop() 