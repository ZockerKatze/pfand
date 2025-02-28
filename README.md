# Österreichischer Pfandrechner 🥤

A modern deposit calculator application for managing bottle and container deposits in Austria. Track your recyclables, earn achievements, and manage your deposit history with this easy-to-use GUI application.

## Features 🌟

- **Multiple Container Types**
  - Flaschen (Bottles)
  - Kasten (Crates)
  - Dose (Cans)
  - Plastikflasche (Plastic Bottles)

- **Achievement System** 🏆
  - Collection Achievements
    - "Krass, Weiter So!" - Collect 100 of each item
    - "Adlersson wäre neidisch!" - Collect 500 of each item
    - "Arbeitslos I" - Collect 1000 of each item
    - "Arbeitslos II" - Total of 2000 items
    - "Arbeitslos III" - Total of 3000 items
    - "Krankhafte Sucht!" - More than 3000 items
  - Deposit Achievements
    - "Depositer!" - First deposit
    - "Depositer I" - 10 deposits
    - "Depositer II" - 50 deposits
    - "Depositer III" - 100 deposits
    - "Meister Depositer" - 150 deposits

- **Deposit Management** 📊
  - Quick deposit with current date
  - Custom date deposit
  - Complete deposit history
  - Export history to CSV

## Requirements 📋

- Python 3.x
- tkinter (usually comes with Python)
- Pillow (PIL)
- tkcalendar

## Installation 🔧

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pfandrechner.git
cd pfandrechner
```

2. Install required packages:
```bash
pip install pillow tkcalendar
```

## Running the Application 🚀

### Windows
- Double-click `run.bat`
- Or run from command prompt:
```bash
python run.py
```

### Linux/Unix
- Make the run script executable:
```bash
chmod +x run.sh
```
- Run the application:
```bash
./run.sh
```

## Keyboard Shortcuts ⌨️

- **File Operations**
  - `Ctrl+S` - Save quantities
  - `Ctrl+O` - Open file location
  - `Ctrl+Shift+F1` - Delete save file
  - `Ctrl+Q` - Quit application

- **Deposit Operations**
  - `Ctrl+D` - Quick deposit
  - `Ctrl+H` - View deposit history
  - `Ctrl+E` - Export history to CSV
  - `Ctrl+Shift+F2` - Clear deposit history

- **Achievement Operations**
  - `Ctrl+F6` - View achievements
  - `Ctrl+F7` - Delete achievements

## File Structure 📁

```
pfandrechner/
├── main.py           # Main application code
├── run.py           # Python launcher
├── run.bat          # Windows launcher
├── run.sh           # Linux/Unix launcher
├── README.md        # This file
└── images/          # Image assets
    └── auszeichnung.png  # Achievement icon
```

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 👏

- Thanks to all contributors and users of the application
- Icons and images used in this project 