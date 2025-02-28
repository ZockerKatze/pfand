import tkinter as tk
import platform
import os
from main import PfandCalculator

def setup_platform_specific():
    system = platform.system().lower()
    if system == "linux":
        try:
            from ctypes import cdll
            cdll.LoadLibrary("libtk8.6.so")
        except:
            pass
    elif system == "windows":
        if os.environ.get('PYTHONW_RUNNING') != '1':
            os.environ['PYTHONW_RUNNING'] = '1'

if __name__ == "__main__":
    setup_platform_specific()
    root = tk.Tk()
    app = PfandCalculator(root)
    root.mainloop() 